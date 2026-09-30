#!/usr/bin/python3

import cgi
import html
import mysql.connector
import os
from http import cookies
import sys

from functions import PrintBody

import cgitb
cgitb.enable()

# ブラウザから送信されたCookieの値を取り出す
cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
user_id = ''
session_id = ''

# Cookie内のuser_idの値を取り出す
try:
    user_id = cookie["user_id"].value
except KeyError:
    user_id = ''

# Cookie内のsession_idの値を取り出す
try:
    session_id = cookie["session_id"].value
except KeyError:
    session_id = ''

# DB接続
connection = mysql.connector.connect(
    host='localhost',
    user='user1',
    passwd='passwordA1!',
    db='shopping',
    charset='utf8'
)
cursor = connection.cursor()

# DBからセッションIDを取得
t_session_id = ''
if user_id:
    sql = f"select session_id from Sessions where user_id = {user_id};" 
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows:
        t_session_id = rows[0][0]  # カラムが1つのため[0]を指定
    
form = cgi.FieldStorage()
logout = form.getfirst("logout")
    
login_flag = False
# クッキーが存在し、かつDBのセッションIDと一致する場合にログイン成功
if user_id != '' and session_id != '' and session_id == t_session_id: 
    login_flag = True   

if logout:
    sql = "delete from Sessions where user_id=" + user_id
    print("Set-Cookie: session_id=; Max-Age=0;")
    print("Set-Cookie: user_id=; Max-Age=0;")
    cursor.execute(sql)
    connection.commit()
    login_flag = False
 
if not login_flag:
    # ログイン失敗：ログイン画面へリダイレクト
    print("Location: ./login.cgi\n")
    cursor.close()
    connection.close()
    sys.exit()


item_in_cart = form.getfirst("item_in_cart")
if item_in_cart:
    item_id = form.getfirst("item_id")
    quantity = form.getfirst("quantity")
    sql = "insert into Carts(user_id, item_id, quantity) values(" + user_id + "," + item_id + "," + quantity + ") ON DUPLICATE KEY UPDATE quantity=" + quantity
    cursor.execute(sql)
    connection.commit()
    print("Location: cart.cgi\n")
    connection.close()
    sys.exit()


print("Content-type: text/html\n")
htmlText = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECサイト - ホーム</title>
    <link rel="stylesheet" href="common.css">
<style>
    /* 商品詳細リンク＆タイトル */
    .item-link {
        text-decoration: none;
        color: inherit;
        display: block;
    }
    .item-link h3 {
        color: var(--text-main, #333);
        margin: 0 0 8px;
        font-size: 1.1rem;
    }

    /* カートボタン */
    .cart-button {
        display: block;
        margin-top: 12px;
        padding: 10px;
        text-align: center;
        text-decoration: none;
        font-weight: 700;
        background: var(--holo);
        background-size: 300% 300%;
        animation: holo-shift 4s ease-in-out infinite;
        color: var(--text-main);
        border-radius: var(--radius-pill);
        font-size: .9rem;
        box-shadow: 0 4px 0 rgba(183, 155, 232, 0.6);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .cart-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 0 rgba(183, 155, 232, 0.6), 0 0 16px rgba(77, 217, 232, 0.5);
    }

    /* ===== 商品タイル (複数列に正しく並ぶよう調整) ===== */
    main {
        width: 100%;
        max-width: 1200px;
        margin: 32px auto;
        padding: 20px 16px;
        position: relative;
        z-index: 1;
        box-sizing: border-box;

        /* 自動で横方向に複数並ぶグリッド設定 */
        display: grid !important;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)) !important;
        gap: 20px;
    }

    main > div {
        display: flex;
        flex-direction: column;
        border-radius: var(--radius-soft);
        padding: 18px 20px;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 6px 0 var(--shadow-silver), 0 12px 24px rgba(120, 150, 200, 0.25);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-sizing: border-box;
    }

    main > div:hover {
        transform: translateY(-4px);
        box-shadow: 0 9px 0 var(--shadow-silver), 0 16px 30px rgba(120, 150, 200, 0.35), 0 0 16px rgba(77, 217, 232, 0.4);
    }

    main > div .genre { margin: 0 0 4px; color: var(--text-sub); font-size: .8rem; }

    /* ===== 星評価用スタイル ===== */
    main > div .star  { margin: 0 0 6px; color: #FFA41C; font-weight: bold; font-size: 0.95rem; }
    main > div .review-count { color: #007185; font-weight: normal; font-size: 0.85rem; }

    main > div .price { margin: 0 0 8px; color: var(--danger); font-weight: bold; font-size: 1.1rem; }
    main > div .desc  { margin: 0; color: var(--text-main); font-size: .9rem; flex: 1; }
    
    /* 数量カウンター */
    .counter {
        display: inline-flex;
        align-items: center;
        border: 2px solid #444;
        border-radius: 8px;
        overflow: hidden;
    }

    .counter input[type="button"] {
        width: 40px;
        height: 40px;
        border: none;
        background: #444;
        color: white;
        font-size: 1.5em;
        cursor: pointer;
        transition: background 0.2s;
    }

    .counter input[type="button"]:hover {
        background: #666;
    }

    .counter input[type="number"] {
        width: 60px;
        height: 40px;
        text-align: center;
        border: none;
        font-size: 1.2em;
        -moz-appearance: textfield;
    }

    .counter input[type="number"]::-webkit-inner-spin-button,
    .counter input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
</style>
</head>
"""
print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))


# フォームデータを取得
keyword = form.getfirst("keyword", "")
genre = form.getfirst("genre", "")
min_price = form.getfirst("min_price", "")
max_price = form.getfirst("max_price", "")
min_star = form.getfirst("min_star", "")
sort_by = form.getfirst("sort", "newest") # デフォルトは新着順


sql = """
SELECT i.item_id, i.item_name, i.price, i.genre, i.description, i.image_path, 
COALESCE(AVG(r.star), 0) AS avg_star, COUNT(r.star) AS review_count
FROM Items i LEFT JOIN Reviews r ON i.item_id = r.item_id
"""

# WHEREによる絞り込み（ジャンル、最小金額、最大金額）
where = []

if genre:
    where.append(f"i.genre = '{genre}'")

if min_price and min_price.isdigit():
    where.append(f"i.price >= {min_price}")

if max_price and max_price.isdigit():
    where.append(f"i.price <= {max_price}")

if keyword:
    where.append(f"i.item_name LIKE '%{keyword}%'")

if where:
    sql += " WHERE " + " AND ".join(where)


# GROUP BYによるグループ分け（平均星数を集計するため）
sql += " GROUP BY i.item_id, i.item_name, i.price, i.genre, i.description, i.image_path"


# HAVINGによる絞り込み（平均星数）
if min_star and min_star.replace('.', '', 1).isdigit():
    sql += f" HAVING avg_star >= {min_star}"

# ORDER BYによる並べ替え（価格の安い順、価格の高い順、星の多い順、新着順 (デフォルト)）
if sort_by == "price_asc":
    sql += " ORDER BY i.price ASC"
elif sort_by == "price_desc":
    sql += " ORDER BY i.price DESC"
elif sort_by == "star_desc":
    sql += " ORDER BY avg_star DESC"
else:
    sql += " ORDER BY i.item_id DESC"

# SQLの実行
cursor.execute(sql)
items = cursor.fetchall()


htmlText = ""

for item_id, item_name, price, genre, description, image_path, avg_star, review_count in items:

    # 星の表示（レビュー数が0の場合、「評価なし」と表示させる）
    if review_count > 0:
        star = f'★ {avg_star:.1f} <span class="review-count">({review_count})</span>'
    else:
        star = '<span style="color:#767676; font-weight:normal;">評価なし</span>'
    
    htmlText += f'''
    <div>
        <a class="item-link" href="./items.cgi?item_id={item_id}">
            <h3>{item_name}</h3>
            <img src="{image_path}">
            <p class="genre">{genre}</p>
            <p class="star">{star}</p>
            <p class="price">¥{price}</p>
            <p class="desc">{description}</p>
        </a>
        <form action="./home.cgi" method="POST">
            <div class="counter">
                <input type="button" value="－" onclick="changeCount(this, -1)">
                <input type="number" class="quantity" name="quantity" value="1" min="1" max="10" readonly>
                <input type="button" value="＋" onclick="changeCount(this, 1)">
            </div>
            <input type="hidden" name="item_id" value="{item_id}">
            <input class="cart-button" type="submit" name="item_in_cart" value="カートに入れる">
        </form>
    </div>
    '''

htmlText += """
    <script>
        function changeCount(button,diff) {
            const counter = button.parentElement;
            const input = (counter.getElementsByClassName("quantity"))[0];
            let value = parseInt(input.value);
            const min = parseInt(input.min);
            const max = parseInt(input.max);
            value += diff;
            if (value < min) value = min;
            if (value > max) value = max;
            input.value = value;
        }
    </script>
"""

PrintBody(connection, user_id, htmlText)

cursor.close()
connection.close()
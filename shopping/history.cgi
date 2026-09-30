#!/usr/bin/python3

# これは本番で消してね
# import cgitb
# cgitb.enable() 

# ライブラリのインポート
import cgi
import html
import mysql.connector
import os
from http import cookies

from functions import PrintBody

# フォームの取得
form = cgi.FieldStorage()
keyword = form.getfirst("keyword")

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

login_flag = False
# クッキーが存在し、かつDBのセッションIDと一致する場合にログイン成功
if user_id != '' and session_id != '' and session_id == t_session_id: 
    login_flag = True


if not login_flag:
    # ログイン失敗：ログイン画面でリダイレクト
    print("Location: ./login.cgi\n")
    cursor.close()
    connection.close()
    exit()


print("Content-type: text/html; charset=utf-8\n")
htmlText = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="common.css">
    <title>ECサイト - 購入履歴</title>
    <style>
        /* ===== メイン（追加） ===== */
        main {{
            flex: 1;
            width: 100%;
            max-width: 1100px;
            margin: 32px auto;
            padding: 30px;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border-radius: var(--radius-soft);
            box-shadow: 0 8px 0 var(--shadow-silver), 0 18px 34px rgba(120, 150, 200, 0.2), 0 0 0 1px rgba(77, 217, 232, 0.25) inset;
            position: relative;
            z-index: 1;
        }}
        .page-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 20px;
        }}
        .page-title {{ font-size: 22px; margin: 0; }}

        /* ===== 検索バー（追加） ===== */
        .order-search {{ display: flex; align-items: center; gap: 10px; }}
        .search-input-wrap {{
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.8);
            border: 3px solid var(--silver);
            border-radius: var(--radius-pill);
            padding: 9px 16px;
            min-width: 280px;
        }}
        .search-input-wrap:focus-within {{ border-color: var(--cyan); box-shadow: var(--glow-cyan); }}
        .search-icon {{ margin-right: 8px; color: var(--text-sub); }}
        .search-input-wrap input {{ flex: 1; border: none; outline: none; background: transparent; font-size: 14px; font-family: 'M PLUS Rounded 1c', sans-serif; }}
        .order-search button {{
            font-family: 'M PLUS Rounded 1c', sans-serif;
            background: var(--holo);
            background-size: 300% 300%;
            animation: holo-shift 4s ease-in-out infinite;
            color: var(--text-main);
            border: none;
            border-radius: var(--radius-pill);
            padding: 11px 22px;
            font-size: 14px;
            font-weight: 800;
            cursor: pointer;
            white-space: nowrap;
            box-shadow: 0 4px 0 rgba(183, 155, 232, 0.6);
            transition: transform 0.15s ease;
        }}
        .order-search button:hover {{ transform: translateY(-2px); }}

        /* ===== 購入履歴テーブル（追加） ===== */
        .history-table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.85);
            border-radius: var(--radius-soft);
            overflow: hidden;
            box-shadow: 0 6px 0 var(--shadow-silver), 0 12px 24px rgba(120, 150, 200, 0.2);
        }}
        .history-table th {{ background: linear-gradient(160deg, var(--visor), var(--visor-deep)); color: var(--mint); padding: 14px 16px; text-align: left; font-size: 14px; font-weight: 700; }}
        .history-table td {{ padding: 14px 16px; border-bottom: 1px dashed var(--silver); font-size: 14px; vertical-align: middle; }}
        .history-table tbody tr:last-child td {{ border-bottom: none; }}
        .history-table tbody tr:hover {{ background: rgba(77, 217, 232, 0.08); }}
        .history-table img {{ width: 80px; height: 80px; object-fit: cover; border-radius: 10px; display: block; }}
        .price {{ color: var(--danger); font-weight: bold; }}
        .empty {{ background: rgba(255, 255, 255, 0.85); border-radius: var(--radius-soft); padding: 40px; text-align: center; color: var(--text-sub); box-shadow: 0 6px 0 var(--shadow-silver), 0 12px 24px rgba(120, 150, 200, 0.2); }}
    </style>
</head>
'''
print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))

htmlText = """
<div class="page-head">
    <h2 class="page-title">📦 購入履歴</h2>
    <form class="order-search" method="post" action="./history.cgi">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" name="keyword" placeholder="すべての注文を検索">
        </div>
        <button type="submit">注文を検索</button>
    </form>
</div>
""" 

# ================================
# 攻撃コード
# aaa%' UNION SELECT NULL, session_id, user_id, NULL, NULL FROM Sessions -- 
# ================================

if (keyword):
    sql = f"""
    SELECT image_path, item_name, price, quantity, order_date
    FROM Items i JOIN Orders o ON i.item_id = o.item_id
    WHERE user_id = {user_id} AND item_name LIKE '%{keyword}%'
    ORDER BY order_date DESC
    """
else:
    sql = f"""
    SELECT image_path, item_name, price, quantity, order_date
    FROM Items i JOIN Orders o ON i.item_id = o.item_id
    WHERE user_id = {user_id}
    ORDER BY order_date DESC
    """
    
try:
    cursor.execute(sql)
    rows = cursor.fetchall()
except mysql.connector.Error as e:
    rows = []
    
    # これは本番で消してね
    # print(f"<p>{e}</p>")
#finally:
    #cursor.close()
    #connection.close()

if rows:
    htmlText += '''
    <table class="history-table">
        <tr>
            <th>商品画像</th>
            <th>商品名</th>
            <th>金額</th>
            <th>商品数量</th>
            <th>購入日</th>
        </tr>
    '''
    for image_path, item_name, price, quantity, order_date in rows:
        htmlText += f'''
        <tr>
            <td><img src="{image_path}" alt=""></td>
            <td>{item_name}</td>
            <td class="price">¥{price}</td>
            <td>{quantity}</td>
            <td>{order_date}</td>
        </tr>
    '''
    htmlText += '        </table>\n'
else:
    if keyword:
        # キーワード検索したが該当なし
        htmlText += f'        <div class="empty">「{html.escape(keyword)}」に一致する購入履歴がありません。</div>\n'
    else:
        # そもそも購入履歴が1件もない
        htmlText += '        <div class="empty">購入履歴がありません。</div>\n'


PrintBody(connection, user_id, htmlText)

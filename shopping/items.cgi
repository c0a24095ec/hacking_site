#!/usr/bin/python3
import os
from http import cookies
import cgi
import mysql.connector
import sys
import html

import cgitb
cgitb.enable()

from functions import PrintBody

t_user_id = ''
t_session_id = ''
check_error = ''
quantity = 0
before_login = False

# クッキーの取得
cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
try:
    session_id = cookie["session_id"].value
except KeyError:
    session_id = ''

try:
    user_id = cookie["user_id"].value
except KeyError:
    user_id = ''

# DB接続
connection = mysql.connector.connect(
    host='localhost',
    user='user1',
    passwd='passwordA1!',
    db='shopping',
    charset='utf8'
)
cursor = connection.cursor()

# セッション検証（プレースホルダーを使用）
sql = "SELECT * FROM Sessions WHERE user_id = %s;"
cursor.execute(sql, (user_id,))
rows = cursor.fetchall()

if rows:
    t_session_id = rows[0][0]

if session_id == '' or user_id == '' or session_id != t_session_id:
    before_login = True

if before_login:
    print("Location: ./login.cgi")
    print()
    sys.exit()

# フォームデータの取得
form = cgi.FieldStorage()
item_id = str(form.getvalue("item_id", ""))
review_content = form.getfirst("review_content")
star = form.getfirst("star")
cart = form.getfirst("cart")
purchase = form.getfirst("purchase")
quantity = form.getfirst("quantity", "1")

# 商品情報の取得
sql = "SELECT * FROM Items WHERE item_id = %s"
cursor.execute(sql, (item_id,))
items = cursor.fetchall()

if not items:
    print("Location: error.cgi")
    print()
    connection.close()
    sys.exit()

item = items[0]
image_path = item[5]
discription = item[4]
item_name = item[1]
price = item[2]
genre = item[3]

# レビュー投稿処理
if review_content is not None and star is not None:
    sql = "INSERT INTO Reviews VALUES (null, %s, %s, %s, %s)"
    cursor.execute(sql, (item_id, user_id, review_content, str(star)))
    connection.commit()

# レビュー一覧取得
sql = "SELECT u.name, r.content, r.star FROM Reviews r INNER JOIN Users u ON r.user_id = u.user_id WHERE r.item_id = %s"
cursor.execute(sql, (item_id,))
reviews = cursor.fetchall()

# カート・購入処理
if cart or purchase:
    sql = "INSERT INTO Carts VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE quantity = %s;"
    cursor.execute(sql, (user_id, item_id, quantity))
    connection.commit()
    connection.close()
    if purchase:
        print("Location: purchase.cgi")
        print()
        sys.exit()
    elif cart:
        print("Location: home.cgi")
        print()
        sys.exit()

# レスポンス出力
print("Content-Type: text/html; charset=utf-8")
print()

htmlText = """
<!DOCTYPE html>
<html lang="ja">
<head>
	<meta charset="UTF-8">
	<title>商品ページ</title>
	<link rel="stylesheet" href="./common.css">
	<style>
		.container {
			width: 1000px;
			margin: 30px auto;
		}

		.product {
			display: flex;
			background: rgba(255, 255, 255, 0.85);
			backdrop-filter: blur(10px);
			padding: 25px;
			border-radius: var(--radius-soft);
			box-shadow: 0 8px 0 var(--shadow-silver), 0 18px 34px rgba(120, 150, 200, 0.2);
		}

		.image {
			width: 350px;
			text-align: center;
		}

		.image img {
			width: 320px;
			height: 320px;
			object-fit: cover;
			border-radius: 18px;
			border: 3px solid var(--silver);
		}

		.info {
			flex: 1;
			margin-left: 40px;
		}

		h1 {
			margin-top: 0;
			font-family: 'M PLUS Rounded 1c', sans-serif;
			font-weight: 800;
			background: var(--holo);
			background-size: 300% 300%;
			-webkit-background-clip: text;
			background-clip: text;
			color: transparent;
			animation: holo-shift 6s ease-in-out infinite;
		}

		.genre {
			display: inline-block;
			padding: 5px 14px;
			background: linear-gradient(160deg, #161a26, #05070c);
			color: var(--mint);
			border-radius: var(--radius-pill);
			font-size: .85rem;
		}

		.price {
			font-size: 32px;
			color: var(--danger);
			margin: 20px 0;
			font-weight: bold;
		}

		.desc {
			line-height: 1.8;
		}

		#button {
			width: 180px;
			padding: 15px;
			margin: 10px 10px 10px 0;
			border: none;
			border-radius: var(--radius-pill);
			cursor: pointer;
			color: var(--text-main);
			font-size: 17px;
			font-weight: 700;
			transition: transform 0.15s ease, box-shadow 0.15s ease;
		}

		#button:hover {
			transform: translateY(-2px);
		}

		.buy {
			background: var(--holo);
			background-size: 300% 300%;
			animation: holo-shift 4s ease-in-out infinite;
			box-shadow: 0 4px 0 rgba(183, 155, 232, 0.6);
		}

		.cart2 {
			background: rgba(255, 255, 255, 0.85);
			border: 3px solid var(--silver);
			box-shadow: 0 4px 0 var(--shadow-silver);
		}

		.review {
			margin-top: 40px;
			background: rgba(255, 255, 255, 0.85);
			backdrop-filter: blur(10px);
			padding: 20px;
			border-radius: var(--radius-soft);
			box-shadow: 0 8px 0 var(--shadow-silver), 0 18px 34px rgba(120, 150, 200, 0.2);
		}

		.review h2 {
			margin-top: 0;
			font-family: 'M PLUS Rounded 1c', sans-serif;
			font-weight: 800;
			background: var(--holo);
			background-size: 300% 300%;
			-webkit-background-clip: text;
			background-clip: text;
			color: transparent;
			animation: holo-shift 6s ease-in-out infinite;
		}

		.review textarea {
			width: 100%;
			height: 120px;
			resize: none;
			font-size: 16px;
			font-family: 'M PLUS Rounded 1c', sans-serif;
			padding: 12px 16px;
			border: 3px solid var(--silver);
			border-radius: 18px;
			outline: none;
		}

		.review textarea:focus {
			border-color: var(--cyan);
			box-shadow: var(--glow-cyan);
		}

		.review select {
			padding: 8px 14px;
			font-family: 'M PLUS Rounded 1c', sans-serif;
			border: 3px solid var(--silver);
			border-radius: var(--radius-pill);
			outline: none;
		}

		.review button {
			background: var(--holo);
			background-size: 300% 300%;
			animation: holo-shift 4s ease-in-out infinite;
			width: 150px;
			box-shadow: 0 4px 0 rgba(183, 155, 232, 0.6);
		}

		.review-list {
			margin-top: 30px;
		}

		.review-item {
			border-top: 1px dashed var(--silver);
			padding: 15px 0;
		}

		.star {
			color: var(--cyan-strong);
			font-size: 18px;
			margin-bottom: 8px;
		}

		.button {
			display: inline-block;
			padding: 10px 20px;
			background: var(--holo);
			background-size: 300% 300%;
			animation: holo-shift 4s ease-in-out infinite;
			color: var(--text-main);
			font-weight: 700;
			text-decoration: none;
			border-radius: var(--radius-pill);
			box-shadow: 0 4px 0 rgba(183, 155, 232, 0.6);
		}

		.quantity {
			width: 70px;
			padding: 8px;
			font-size: 16px;
			text-align: center;
			margin-right: 10px;
			font-family: 'M PLUS Rounded 1c', sans-serif;
			border: 3px solid var(--silver);
			border-radius: var(--radius-pill);
			outline: none;
		}

		.quantity:focus {
			border-color: var(--cyan);
			box-shadow: var(--glow-cyan);
		}
	</style>
</head>
"""
print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))

htmlText = f"""
<div class="container">
	<div class="product">
		<div class="image">
			<img id="image" src="{html.escape(str(image_path))}">
		</div>
		<div class="info">
			<h1 id="name">{html.escape(str(item_name))}</h1>
			<div class="genre" id="genre">{html.escape(str(genre))}</div>
			<div class="price" id="price">{price}円</div>
			<div class="desc" id="description">{html.escape(str(discription))}</div>
			<br>

			<div style="display: inline-flex; align-items: center;">
				<form action="./purchase_one.cgi" method="POST">
					<input class="button" type="submit" name="purchase" value="即購入">
					<input type="hidden" name="item_info" value="{html.escape(item_id)}:{html.escape(str(item_name))}:{price}">
				</form>

				<form action="./items.cgi?item_id={html.escape(item_id)}" method="POST" style="display: inline-flex; align-items: center;">
					<input type="number" id="quantity" name="quantity" value="1" min="1" max="99" class="quantity">
					<input class="cart2" type="submit" name="cart" value="カートに入れる">
				</form>
			</div>
		</div>
	</div>

	<div class="review">
		<h2>レビュー</h2>
		<p>評価</p>
		<form action="./items.cgi?item_id={html.escape(item_id)}" method="POST">
			<select id="star" name="star">
				<option value="5">★★★★★</option>
				<option value="4">★★★★☆</option>
				<option value="3">★★★☆☆</option>
				<option value="2">★★☆☆☆</option>
				<option value="1">★☆☆☆☆</option>
			</select>

			<p>本文</p>
			<textarea id="text" name="review_content"></textarea>
			<br><br>
			<input type="submit" value="投稿">
		</form>
		<div id="reviews" class="review-list">
"""

for i in reviews:
    display_star = ""
    star_val = int(i[2]) if i[2] is not None else 0
    for j in range(1, 6):
        if star_val >= j:
            display_star += "★"
        else:
            display_star += "☆"
            
    user_name_esc = html.escape(str(i[0]))
    content_esc = str(i[1])
    
    
    htmlText += f"""
    <div class="review-item">
    <div class="name">{user_name_esc}</div>
    <div class="star">{display_star}</div>
    <div>{content_esc}</div>
    </div>
    """

PrintBody(connection, user_id, htmlText)

connection.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import html
import mysql.connector

from functions import PrintBody

print("Content-Type: text/html; charset=utf-8")
print()

form = cgi.FieldStorage()

##################################################
# 商品情報取得
##################################################

item_ids = form.getlist("item_id")
quantities = form.getlist("quantity")

total = form.getfirst("total", "0")

# ----------------------------
# MySQL接続
# ----------------------------

connection = mysql.connector.connect(
    host="localhost",
    user="user1",
    password="passwordA1!",
    db="shopping",
    charset="utf8"
)

cursor = connection.cursor()

##################################################
# 購入者情報
##################################################

name = form.getfirst("name", "")

prefecture = form.getfirst("prefecture", "")
city = form.getfirst("city", "")
street = form.getfirst("street", "")

address = prefecture + "|" + city + "|" + street

##################################################
# クレジットカード
##################################################

card_number = form.getfirst("card_number", "")
card_name = form.getfirst("card_name", "")
month = form.getfirst("month", "")
year = form.getfirst("year", "")

credit = (
    card_number
    + "|"
    + card_name
    + "|"
    + month
    + "|"
    + year
)

save_address = form.getfirst("save_address", "")
save_credit = form.getfirst("save_credit", "")

##################################################
# HTML開始
##################################################

print("""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="UTF-8">

<title>購入確認</title>

<link rel="stylesheet" href="./common.css" type="text/css">

<style>

.confirm-container{
    width:900px;
    margin:40px auto;
}

table{
    width:100%;
    border-collapse:collapse;
}

th,td{
    border:1px solid black;
    padding:10px;
}

</style>

</head>

<body>
""")

print(f"""
<header>
    <div class="header-inner">
        <a href="./home.cgi" class="logo">TechShop</a>

        <form class="search" method="get" action="./home.cgi">
            <input type="text" name="keyword" placeholder="商品を検索">
            <button type="submit">🔍</button>
        </form>

        <div class="header-right">
            <a href="./user.cgi" class="nav-link">
                <span class="nav-sub">ようこそ、{html.escape(name)} 様</span>
                <span class="nav-main">マイページ</span>
            </a>

            <a href="./history.cgi" class="nav-link">📦購入履歴</a>
            <a href="./cart.cgi" class="nav-link cart">🛒 カート</a>
            <a href="./logout.cgi" class="nav-link">ログアウト</a>
        </div>
    </div>
</header>

<div class="subnav">
    <div class="subnav-inner">
        <a href="./home.cgi">すべて</a>
        <a href="./home.cgi?genre=おもちゃ">おもちゃ</a>
        <a href="./home.cgi?genre=文房具">文房具</a>
        <a href="./home.cgi?genre=キッチン">キッチン</a>
    </div>
</div>

<main>
<div class="confirm-container">

<h1>購入確認</h1>

<form action="complete.cgi" method="post">

<h2>商品</h2>

<table>

<tr>
<th>商品名</th>
<th>価格</th>
<th>数量</th>
<th>合計金額</th>
</tr>
""")


##################################################
# 商品一覧表示
##################################################

confirm_total = 0


for i in range(len(item_ids)):

    item_id = item_ids[i]
    quantity = int(quantities[i])


    sql = """
    SELECT item_name, price
    FROM Items
    WHERE item_id=%s
    """

    cursor.execute(sql,(item_id,))

    item = cursor.fetchone()


    if item is not None:

        item_name = item[0]
        price = item[1]

        subtotal = price * quantity

        confirm_total += subtotal


        print(f"""

<tr>

<td>
{html.escape(item_name)}
</td>

<td>
{price}円
</td>

<td>
{quantity}
</td>

<td>
{subtotal}円
</td>

</tr>


<input type="hidden"
name="item_id"
value="{item_id}">


<input type="hidden"
name="quantity"
value="{quantity}">

""")
print(f"""
</table>

<hr>

<h2>合計金額</h2>

<p>
<strong>{confirm_total}円</strong>
</p>

<input type="hidden" name="total" value="{confirm_total}">

<hr>

<h2>購入者情報</h2>

<p>

氏名：{html.escape(name)}

</p>

<input type="hidden" name="name" value="{html.escape(name)}">

<h3>配送先</h3>

<p>

都道府県：{html.escape(prefecture)}<br>

市区町村：{html.escape(city)}<br>

番地：{html.escape(street)}

</p>

<input type="hidden" name="address" value="{html.escape(address)}">

<input type="hidden" name="save_address" value="{html.escape(save_address)}">

<hr>

<h2>クレジットカード</h2>

<p>

カード番号：**** **** **** {html.escape(card_number[-4:])}<br>

名義：{html.escape(card_name)}<br>

有効期限：{html.escape(month)}/{html.escape(year)}

</p>

<input type="hidden" name="credit" value="{html.escape(credit)}">

<input type="hidden" name="save_credit" value="{html.escape(save_credit)}">

<input type="hidden" name="card_number" value="{html.escape(card_number)}">
<input type="hidden" name="card_name" value="{html.escape(card_name)}">
<input type="hidden" name="month" value="{html.escape(month)}">
<input type="hidden" name="year" value="{html.escape(year)}">

<hr>
""")

##################################################
# ボタン
##################################################

print("""

<p>

<input
type="button"
value="戻る"
onclick="history.back()">

&nbsp;&nbsp;&nbsp;

<input
type="submit"
value="購入を確定">

</p>

</form>

</div>

</main>

<footer>
<div class="footer-bottom">
	&copy; 2026 TechShop All Rights Reserved.
</div>
</footer>

</body>
</html>
""")

PrintBody(connection, user_id, htmlText)




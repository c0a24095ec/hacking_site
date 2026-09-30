#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import html
import http.cookies
import mysql.connector

from functions import PrintHeader, PrintFooter, PrintBody

##################################################
# Cookie取得
##################################################

cookie = http.cookies.SimpleCookie(
    os.environ.get("HTTP_COOKIE", "")
)

if "session_id" not in cookie:
    print("Status: 303 See Other")
    print("Location: login.cgi")
    print()
    exit()
    
session_id = cookie["session_id"].value

##################################################
# MySQL接続
##################################################

connection = mysql.connector.connect(
    host="localhost",
    user="user1",
    password="passwordA1!",
    db="shopping",
    charset="utf8"
)

cursor = connection.cursor()

##################################################
# セッション確認
##################################################

sql = """
SELECT user_id
FROM Sessions
WHERE session_id=%s
"""

cursor.execute(sql, (session_id,))
row = cursor.fetchone()

if row is None:
    cursor.close()
    connection.close()

    print("Status: 303 See Other")
    print("Location: login.cgi")
    print()
    exit()
    
user_id = row[0]

##################################################
# ユーザー情報取得
##################################################

sql = """
SELECT
name,
mail_address,
address,
credit
FROM Users
WHERE user_id=%s
"""

cursor.execute(sql, (user_id,))
user = cursor.fetchone()

name = user[0]
mail = user[1]

address = user[2] if user[2] else ""
credit = user[3] if user[3] else ""

##################################################
# 住所分割
##################################################

prefecture = ""
city = ""
street = ""

if address != "":
    data = address.split("|")
    if len(data) >= 3:
        prefecture = data[0]
        city = data[1]
        street = data[2]

##################################################
# カード分割
##################################################

card_number = ""
card_name = ""
month = ""
year = ""

if credit != "":
    data = credit.split("|")
    if len(data) >= 4:
        card_number = data[0]
        card_name = data[1]
        month = data[2]
        year = data[3]

##################################################
# HTML
##################################################

print("Content-Type: text/html; charset=utf-8")
print()

htmlText = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>マイページ</title>
    <link rel="stylesheet" href="common.css">
    <style>
        main {
            font-family:sans-serif;
            width:900px;
            margin:auto;
        }

        table{
            width:100%;
            border-collapse:collapse;
        }

        th,td{
            border:1px solid #ccc;
            padding:10px;
        }

        button{
            padding:10px 20px;
            margin:10px;
        }
    </style>
</head>
"""
print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))


htmlText = f"""
<h1>マイページ</h1>

<h2>ユーザー情報</h2>

<table>

<tr>
<th>氏名</th>
<td>{html.escape(name)}</td>
</tr>

<tr>
<th>メールアドレス</th>
<td>{html.escape(mail)}</td>
</tr>

<tr>
<th>パスワード</th>
<td>********</td>
</tr>

<tr>
<th>住所</th>
<td>
{html.escape(prefecture)}
{html.escape(city)}
{html.escape(street)}
</td>
</tr>

<tr>
<th>クレジットカード</th>
<td>
**** **** **** {html.escape(card_number[-4:])}<br>
名義：{html.escape(card_name)}<br>
有効期限：{html.escape(month)}/{html.escape(year)}
</td>
</tr>

</table>

<br>

<button onclick="location.href='edit_password.cgi'">
パスワード変更
</button>



<button onclick="location.href='edit_address.cgi'">
住所変更
</button>

<button onclick="location.href='edit_credit.cgi'">
カード情報変更
</button>

<button onclick="location.href='history.cgi'">
購入履歴
</button>

<button onclick="location.href='home.cgi'">
ホームへ戻る
</button>
"""

PrintBody(connection, user_id, htmlText)

cursor.close()
connection.close()

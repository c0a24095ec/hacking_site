#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import http.cookies
import html
import mysql.connector

from functions import PrintBody

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
# 現在の住所取得
##################################################

sql = """
SELECT address
FROM Users
WHERE user_id=%s
"""

cursor.execute(sql, (user_id,))
row = cursor.fetchone()

address = row[0] if row and row[0] else ""

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
# HTML
##################################################

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="UTF-8">

<title>住所変更</title>
<link rel="stylesheet" href="common.css">
<style>

main{{
    width:700px;
    margin:auto;
    font-family:sans-serif;
}}

input[type=text]{{
    width:400px;
    padding:8px;
}}

</style>

</head>
""")

htmlText = f"""
<h1>住所変更</h1>

<form action="update_address.cgi" method="post">

都道府県<br>

<input
type="text"
name="prefecture"
value="{html.escape(prefecture)}">

<br><br>

市区町村<br>

<input
type="text"
name="city"
value="{html.escape(city)}">

<br><br>

番地・建物名<br>

<input
type="text"
name="street"
value="{html.escape(street)}">

<br><br>

<input
type="submit"
value="住所を変更">

&nbsp;&nbsp;

<input
type="button"
value="戻る"
onclick="history.back()">

</form>

</body>

</html>
"""

PrintBody(connection, user_id, htmlText)

cursor.close()
connection.close()

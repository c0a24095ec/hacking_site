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

cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE", ""))

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
# カード情報取得
##################################################

sql = """
SELECT credit
FROM Users
WHERE user_id=%s
"""

cursor.execute(sql, (user_id,))
row = cursor.fetchone()

credit = row[0] if row and row[0] else ""

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

print("""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="UTF-8">

<title>カード情報変更</title>

<link rel="stylesheet" href="common.css">
<style>

main {
    width:700px;
    margin:auto;
    font-family:sans-serif;
}

input[type=text]{
    width:400px;
    padding:8px;
}

</style>

</head>
""")

htmlText = f"""
<h1>カード情報変更</h1>

<form action="update_credit.cgi" method="post">

カード番号<br>

<input
type="text"
name="card_number"
maxlength="16"
value="{html.escape(card_number)}">

<br><br>

名義人<br>

<input
type="text"
name="card_name"
value="{html.escape(card_name)}">

<br><br>

有効期限（月）<br>

<input
type="text"
name="month"
maxlength="2"
value="{html.escape(month)}">

<br><br>

有効期限（年）<br>

<input
type="text"
name="year"
maxlength="2"
value="{html.escape(year)}">

<br><br>

<input
type="submit"
value="変更する">

&nbsp;&nbsp;

<input
type="button"
value="戻る"
onclick="history.back()">

</form>
"""

PrintBody(connection, user_id, htmlText)

cursor.close()
connection.close()

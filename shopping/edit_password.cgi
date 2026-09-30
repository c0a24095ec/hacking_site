#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import http.cookies
import mysql.connector

from functions import PrintBody

##################################################
# Cookie取得
##################################################
cookie = http.cookies.SimpleCookie(
    os.environ.get("HTTP_COOKIE", "")
)

user_id = ''
try:
    user_id = cookie["user_id"].value
except KeyError:
    user_id = ''

if "session_id" not in cookie:
    print("Status: 303 See Other")
    print("Location: login.cgi")
    print()
    exit()

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

##################################################
# HTMLの組み立て
##################################################
print("Content-Type: text/html; charset=utf-8\n")


htmlText = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>パスワード変更</title>
<link rel="stylesheet" href="common.css">
<style>
main {
    width:700px;
    margin:auto;
    font-family:sans-serif;
}
input{
    width:300px;
    padding:8px;
}
</style>
</head>

<h1>パスワード変更</h1>

<form action="update_password.cgi" method="post">
現在のパスワード<br>
<input type="password" maxlength="8" name="old_password">
<br><br>

新しいパスワード<br>
<input type="password" maxlength="8" name="new_password">
<br><br>

新しいパスワード（確認）<br>
<input type="password" maxlength="8" name="new_password2">
<br><br>

<input type="submit" value="変更">
</form>
"""

PrintBody(connection, user_id, htmlText)

connection.close()
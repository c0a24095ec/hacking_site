#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import html
import http.cookies
import os
import mysql.connector

print("Content-Type: text/html; charset=utf-8")
print()

form = cgi.FieldStorage()

##################################################
# Cookie取得
##################################################

cookie = http.cookies.SimpleCookie(
    os.environ.get("HTTP_COOKIE", "")
)

if "session_id" not in cookie:
    print("<h2>ログインしてください。</h2>")
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
# Session確認
##################################################

sql = """
SELECT user_id
FROM Sessions
WHERE session_id=%s
"""

cursor.execute(sql, (session_id,))
row = cursor.fetchone()

if row is None:
    print("<h2>ログインしてください。</h2>")
    exit()

user_id = row[0]

##################################################
# POSTデータ取得
##################################################

item_ids = form.getlist("item_id")
quantities = form.getlist("quantity")

address = form.getfirst("address", "")
credit = form.getfirst("credit", "")

save_address = form.getfirst("save_address", "")
save_credit = form.getfirst("save_credit", "")

##################################################
# 住所を保存
##################################################

if save_address == "1":

    sql = """
    UPDATE Users
    SET address=%s
    WHERE user_id=%s
    """

    cursor.execute(sql, (address, user_id))

##################################################
# カード情報を保存
##################################################

if save_credit == "1":

    sql = """
    UPDATE Users
    SET credit=%s
    WHERE user_id=%s
    """

    cursor.execute(sql, (credit, user_id))

##################################################
# Ordersへ登録
##################################################

for i in range(len(item_ids)):

    item_id = item_ids[i]
    quantity = quantities[i]

    sql = """
    INSERT INTO Orders
    (
        user_id,
        item_id,
        quantity
    )
    VALUES
    (
        %s,
        %s,
        %s
    )
    """

    cursor.execute(sql, (
        user_id,
        item_id,
        quantity
    ))

##################################################
# カートを空にする
##################################################

sql = """
DELETE FROM Carts
WHERE user_id=%s
"""

cursor.execute(sql, (user_id,))

##################################################
# DB更新
##################################################

connection.commit()

cursor.close()
connection.close()

##################################################
# 完了画面表示
##################################################

print("""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="UTF-8">

<title>購入完了</title>

<style>

@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800&display=swap');

:root{
    --porcelain:     #f2f6fb;
    --sky:           #bfe6ff;
    --lavender:      #d9c9ff;
    --pink:          #ffc2d9;
    --mint:          #c3f7dd;
    --cyan:          #4dd9e8;
    --cyan-deep:     #0891a8;
    --text-main:     #33394d;
    --holo: linear-gradient(115deg, var(--sky), var(--lavender), var(--pink), var(--mint), var(--sky));
}

*{ box-sizing: border-box; }

@keyframes holo-shift{
    0%{ background-position: 0% 50%; }
    50%{ background-position: 100% 50%; }
    100%{ background-position: 0% 50%; }
}

@keyframes puku-bob{
    0%, 100%{ transform: translateY(0); }
    50%{ transform: translateY(-14px); }
}

body{
    width:800px;
    margin:auto;
    font-family: 'M PLUS Rounded 1c', 'Helvetica Neue', Arial, sans-serif;
    color: var(--text-main);
    text-align:center;
    min-height: 100vh;
    background:
        radial-gradient(circle at 12% 15%, rgba(191, 230, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 88% 12%, rgba(217, 201, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 18% 88%, rgba(195, 247, 221, 0.45) 0%, transparent 24%),
        radial-gradient(circle at 85% 82%, rgba(255, 194, 217, 0.45) 0%, transparent 24%),
        var(--porcelain);
    background-attachment: fixed;
}

h1{
    margin-top:80px;
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    background: var(--holo);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: holo-shift 6s ease-in-out infinite, puku-bob 3s ease-in-out infinite;
}

a{
    color: var(--cyan-deep);
    font-weight: 700;
    border-bottom: 2px dashed var(--cyan);
    padding-bottom: 1px;
    text-decoration: none;
}

a:hover{
    color: #00c2d1;
}

</style>

</head>


<body>


<h1>
購入が完了しました
</h1>


<p>
ご購入ありがとうございます。
</p>


<p>
注文内容は注文履歴から確認できます。
</p>


<br>


<a href="home.cgi">
ホームへ戻る
</a>


</body>

</html>
""")

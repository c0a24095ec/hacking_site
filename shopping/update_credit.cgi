#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cgi
import html
import http.cookies
import mysql.connector


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
# フォーム取得
##################################################

form = cgi.FieldStorage()

card_number = form.getfirst("card_number", "")
card_name = form.getfirst("card_name", "")
month = form.getfirst("month", "")
year = form.getfirst("year", "")

##################################################
# 入力チェック
##################################################

error = ""

if card_number == "":
    error = "カード番号を入力してください。"

elif not card_number.isdigit():
    error = "カード番号は数字で入力してください。"

elif len(card_number) != 16:
    error = "カード番号は16桁で入力してください。"

elif card_name == "":
    error = "名義人を入力してください。"

elif month == "":
    error = "有効期限（月）を入力してください。"

elif not month.isdigit():
    error = "有効期限（月）は数字で入力してください。"

elif int(month) < 1 or int(month) > 12:
    error = "有効期限（月）が正しくありません。"

elif year == "":
    error = "有効期限（年）を入力してください。"

elif not year.isdigit():
    error = "有効期限（年）は数字で入力してください。"

##################################################
# エラー
##################################################

if error != "":

    print("Content-Type: text/html; charset=utf-8")
    print()

    print(f"""
<h2 style="color:red;">
{html.escape(error)}
</h2>

<button onclick="history.back()">
戻る
</button>
""")

    cursor.close()
    connection.close()
    exit()

##################################################
# 更新
##################################################

credit = card_number + "|" + card_name + "|" + month + "|" + year

sql = """
UPDATE Users
SET credit=%s
WHERE user_id=%s
"""

cursor.execute(sql, (credit, user_id))
connection.commit()

##################################################
# 完了画面
##################################################

print("Content-Type: text/html; charset=utf-8")
print()

print("""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="UTF-8">

<title>カード情報変更完了</title>

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
    --shadow-silver: #c3cee0;
    --radius-pill:   999px;
    --radius-soft:   26px;
    --holo: linear-gradient(115deg, var(--sky), var(--lavender), var(--pink), var(--mint), var(--sky));
}

*{ box-sizing: border-box; }

@keyframes holo-shift{
    0%{ background-position: 0% 50%; }
    50%{ background-position: 100% 50%; }
    100%{ background-position: 0% 50%; }
}

body{
    width:700px;
    margin:auto;
    padding: 60px 20px;
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
}

h1{
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-weight: 800;
    background: var(--holo);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: holo-shift 6s ease-in-out infinite;
}

.backhome button{
    font-family: 'M PLUS Rounded 1c', sans-serif;
    background: var(--holo);
    background-size: 300% 300%;
    animation: holo-shift 4s ease-in-out infinite;
    color: var(--text-main);
    border: none;
    padding: 13px 30px;
    font-weight: 700;
    font-size: 15px;
    border-radius: var(--radius-pill);
    cursor: pointer;
    box-shadow: 0 5px 0 rgba(183, 155, 232, 0.6);
    transition: transform 0.15s ease;
}

.backhome button:hover{
    transform: translateY(-2px);
}

.backhome a{
    text-decoration:none;
}

</style>


</style>

</head>

<body>

<h1>カード情報変更完了</h1>

<p>
カード情報を変更しました。
</p>

<br>

<div class="backhome">
<a href="user.cgi">
<button>
マイページへ戻る
</button>
</a>
</div>

</body>

</html>
""")

cursor.close()
connection.close()

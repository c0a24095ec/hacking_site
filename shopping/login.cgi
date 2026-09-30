#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import html
import os
import hashlib
import http.cookies
import mysql.connector
import random
import string

def get_random_str(n):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(n))



form = cgi.FieldStorage()

mail_address = form.getfirst("mail_address", "")
password = form.getfirst("password", "")
check_error = [mail_address, password]

err = {}

# POST通信のとき
if os.environ.get("REQUEST_METHOD") == "POST":
    if (not mail_address):
        err["mail_address"] = "メールアドレスは入力必須です。"

    if (not password):
        err["password"] = "パスワードは入力必須です。"

    elif len(password) != 8:
        err["password"] = "パスワードは8文字で入力してください。"

    if len(err) == 0:

        # 入力されたパスワードをハッシュ化
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:

            connection = mysql.connector.connect(
                host="localhost",
                user="user1",
                password="passwordA1!",
                db="shopping",
                charset = 'utf8'
            )

            cursor = connection.cursor()

            sql = """
            SELECT user_id, hashed_password, name
            FROM Users
            WHERE mail_address = %s
            """

            cursor.execute(sql, (mail_address,))
            row = cursor.fetchone()

            if row is not None:

                user_id = row[0]
                db_password = row[1]
                name = row[2]

                if hashed_password == db_password:

                    cookie = http.cookies.SimpleCookie()
                    cookie["user_id"] = str(user_id)
                    cookie["user_name"] = name
                    
                    
                    cursor.execute("DELETE FROM Sessions WHERE user_id=%s",(user_id,))

                    session_id = get_random_str(64)
                    sql = """
                    INSERT INTO Sessions(session_id, user_id)
                    VALUES(%s, %s);
                    """
                    
                    cursor.execute(sql, (session_id, user_id))
                    connection.commit()
                    
                  
                    cookie["session_id"] = session_id

                    print(cookie)
                    print("Status: 302 Found")
                    print("Location: home.cgi")
                    print()
                    cursor.close()
                    connection.close()
                    exit()

            err["login"] = "メールアドレスまたはパスワードが違います。"

            cursor.close()
            connection.close()

        except Exception as e:
            err["login"] = str(e)
print("Content-Type: text/html; charset=utf-8")
print()

print("""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ログイン | TechShop</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800&display=swap');

:root{
    --porcelain:     #f2f6fb;
    --white:         #ffffff;
    --silver:        #dbe4ef;
    --sky:           #bfe6ff;
    --lavender:      #d9c9ff;
    --pink:          #ffc2d9;
    --mint:          #c3f7dd;
    --cyan:          #4dd9e8;
    --cyan-strong:   #00c2d1;
    --cyan-deep:     #0891a8;
    --text-main:     #33394d;
    --danger:        #ff6b81;
    --danger-bg:     #ffe3e8;
    --shadow-silver: #c3cee0;
    --radius-pill:   999px;
    --holo: linear-gradient(115deg, var(--sky), var(--lavender), var(--pink), var(--mint), var(--sky));
    --glow-cyan: 0 0 14px rgba(77, 217, 232, 0.65);
}

*{
    box-sizing: border-box;
}

html, body{
    height: 100%;
}

body{
    margin: 0;
    padding: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    font-family: 'M PLUS Rounded 1c', 'Helvetica Neue', Arial, sans-serif;
    font-size: 16px;
    color: var(--text-main);
    position: relative;
    overflow-x: hidden;
    background:
        radial-gradient(circle at 12% 15%, rgba(191, 230, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 88% 12%, rgba(217, 201, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 18% 88%, rgba(195, 247, 221, 0.45) 0%, transparent 24%),
        radial-gradient(circle at 85% 82%, rgba(255, 194, 217, 0.45) 0%, transparent 24%),
        var(--porcelain);
    background-attachment: fixed;
}

body::before{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        radial-gradient(circle, #fff 40%, transparent 42%),
        radial-gradient(circle, var(--pink) 40%, transparent 42%),
        radial-gradient(circle, #fff 40%, transparent 42%),
        radial-gradient(circle, var(--sky) 40%, transparent 42%),
        radial-gradient(circle, #fff 40%, transparent 42%),
        radial-gradient(circle, var(--lavender) 40%, transparent 42%);
    background-size: 4px 4px, 3px 3px, 5px 5px, 3px 3px, 4px 4px, 3px 3px;
    background-position: 8% 20%, 22% 65%, 40% 12%, 68% 40%, 82% 75%, 92% 22%;
    background-repeat: no-repeat;
    animation: twinkle 3.2s ease-in-out infinite;
}

@keyframes twinkle{
    0%, 100%{ opacity: 0.25; }
    50%{ opacity: 0.95; }
}

@keyframes holo-shift{
    0%{ background-position: 0% 50%; }
    50%{ background-position: 100% 50%; }
    100%{ background-position: 0% 50%; }
}

@keyframes pulse-glow{
    0%, 100%{ box-shadow: var(--glow-cyan); }
    50%{ box-shadow: 0 0 24px rgba(77, 217, 232, 0.95); }
}

@keyframes puku-float{
    0%, 100%{ transform: translateY(0) scale(1); }
    50%{ transform: translateY(-6px) scale(1.03); }
}

@keyframes puku-bob{
    0%, 100%{ transform: translateY(0); }
    50%{ transform: translateY(-14px); }
}

h1, h2, h3{
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-weight: 800;
    letter-spacing: 0.02em;
    background: var(--holo);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-stroke: 1px rgba(255, 255, 255, 0.7);
    text-shadow: 0 0 18px rgba(77, 217, 232, 0.35);
    animation: holo-shift 6s ease-in-out infinite;
}

a{
    color: var(--cyan-deep);
    text-decoration: none;
}

.brand-header{
    position: relative;
    z-index: 1;
    text-align: center;
    margin-bottom: 8px;
}

.brand-logo-img{
    width: 150px;
    height: auto;
    filter: drop-shadow(0 10px 20px rgba(120, 150, 200, 0.35));
    animation: puku-bob 5s ease-in-out infinite;
}

.brand-tagline{
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-weight: 800;
    letter-spacing: 0.25em;
    font-size: 13px;
    margin: 2px 0 0;
    background: var(--holo);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: holo-shift 6s ease-in-out infinite;
}

body.login-page{
    align-items: center;
    justify-content: flex-start;
    padding: 40px 16px;
}

body.login-page::after{
    content: "";
    position: fixed;
    top: 8%;
    left: 8%;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    z-index: 0;
    background: radial-gradient(circle at 32% 28%, rgba(255,255,255,0.95), rgba(255,255,255,0.05) 40%, transparent 60%),
                radial-gradient(circle at 65% 70%, var(--pink), transparent 70%);
    box-shadow: inset 0 0 14px rgba(255,255,255,0.7), 0 10px 24px rgba(255, 143, 191, 0.3);
    opacity: 0.85;
    animation: puku-bob 5s ease-in-out infinite;
}

.login-container{
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 420px;
    margin: 40px auto;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 32px;
    padding: 42px 36px;
    box-shadow: 0 10px 0 var(--shadow-silver), 0 22px 44px rgba(120, 150, 200, 0.3);
}

.login-container::before{
    content: "";
    position: absolute;
    inset: -3px;
    border-radius: 34px;
    padding: 3px;
    background: var(--holo);
    background-size: 300% 300%;
    animation: holo-shift 6s ease-in-out infinite;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    z-index: -1;
}

.login-container::after{
    content: "";
    position: fixed;
    bottom: 10%;
    right: 10%;
    width: 130px;
    height: 130px;
    border-radius: 50%;
    z-index: -2;
    background: radial-gradient(circle at 32% 28%, rgba(255,255,255,0.95), rgba(255,255,255,0.05) 40%, transparent 60%),
                radial-gradient(circle at 65% 70%, var(--lavender), transparent 70%);
    box-shadow: inset 0 0 14px rgba(255,255,255,0.7), 0 10px 24px rgba(183, 155, 232, 0.3);
    opacity: 0.85;
    animation: puku-bob 5s ease-in-out infinite 1.5s;
}

.login-container h2{
    text-align: center;
    font-size: 26px;
    margin: 0 0 8px;
}

.login-container h2::before{
    content: "✦ ";
    -webkit-text-stroke: 0;
    text-shadow: none;
    color: var(--lavender);
    filter: saturate(1.4);
}

.login-container h2::after{
    content: " ✦";
    -webkit-text-stroke: 0;
    text-shadow: none;
    color: var(--pink);
    filter: saturate(1.4);
}

.field{
    margin: 22px 0;
}

.field label{
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    color: var(--white);
    background: var(--cyan-deep);
    padding: 4px 14px;
    border-radius: var(--radius-pill);
    margin-bottom: 10px;
}

input[type="text"],
input[type="password"],
input[type="email"]{
    width: 100%;
    padding: 13px 20px;
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-size: 16px;
    color: var(--text-main);
    background: rgba(255, 255, 255, 0.8);
    border: 3px solid var(--silver);
    border-radius: var(--radius-pill);
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

input[type="text"]:focus,
input[type="password"]:focus,
input[type="email"]:focus{
    border-color: var(--cyan);
    box-shadow: var(--glow-cyan);
    transform: scale(1.02);
}

input[type="submit"]{
    width: 100%;
    padding: 15px 14px;
    margin-top: 10px;
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: var(--text-main);
    background: var(--holo);
    background-size: 300% 300%;
    animation: holo-shift 4s ease-in-out infinite;
    border: none;
    border-radius: var(--radius-pill);
    cursor: pointer;
    box-shadow: 0 6px 0 rgba(183, 155, 232, 0.6), 0 10px 22px rgba(150, 170, 220, 0.35), 0 0 0 3px rgba(255, 255, 255, 0.7) inset;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    position: relative;
    z-index: 1;
}

input[type="submit"]:hover{
    transform: translateY(-3px) scale(1.03);
    box-shadow: 0 9px 0 rgba(183, 155, 232, 0.6), 0 16px 28px rgba(150, 170, 220, 0.45), 0 0 20px rgba(191, 230, 255, 0.7), 0 0 0 3px rgba(255, 255, 255, 0.85) inset;
}

input[type="submit"]:active{
    transform: translateY(2px) scale(0.98);
    box-shadow: 0 2px 0 rgba(183, 155, 232, 0.6);
}

.login-container p{
    margin: 0 0 6px;
}

.signup-link{
    margin-top: 22px;
    padding-top: 22px;
    text-align: center;
    font-size: 14px;
}

.signup-link a{
    color: var(--cyan-deep);
    font-weight: 700;
    border-bottom: 2px dashed var(--cyan);
    padding-bottom: 1px;
}

.signup-link a:hover{
    color: var(--cyan-strong);
    border-color: var(--cyan-strong);
}

.error{
    color: var(--danger);
    font-weight: 700;
    font-size: 13px;
    background: var(--danger-bg);
    display: inline-block;
    padding: 6px 16px;
    border-radius: var(--radius-pill);
    margin: -6px 0 16px;
}
</style>
</head>

<body class="login-page">

<div class="brand-header">
<img src="./images/lumipals.png" alt="LumiPals" class="brand-logo-img">
<p class="brand-tagline">ONLINE SHOP</p>
</div>

<div class="login-container">

<h2>ログイン</h2>

<form method="post">

""")

if "login" in err:
    print(f'<p class="error">{html.escape(err["login"])}</p>')

print(f'''
<div class="field">
<label>メールアドレス</label>
<input type="text" name="mail_address" value="{html.escape(mail_address)}">

</div>
''')

if "mail_address" in err:
    print(f'<p class="error">{html.escape(err["mail_address"])}</p>')

print("""
<div class="field">
<label>パスワード（8文字）</label>
<input type="password" name="password" maxlength=8>
</div>
""")

if "password" in err:
    print(f'<p class="error">{html.escape(err["password"])}</p>')

print("""
<input type="submit" value="ログイン">

<p class="signup-link">
<a href="newlogin.cgi">新規ユーザー登録はこちら</a>
</p>

</form>

</div>

</body>
</html>
""")

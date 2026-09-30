#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import html
import os
import http.cookies as cookies
import mysql.connector
import sys

# メール関連
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import platform


check_error=""
error = {}

##################################################
# フォームデータの取得
##################################################

# フォームの取得
form = cgi.FieldStorage()

# フォームの商品情報の取得
item_info = form.getfirst("item_info")
confirm = form.getfirst("confirm")

if(item_info):
    item_id, item_name, price= item_info.split(":")
    quantity=form.getfirst("quantity")
    if (not quantity):
     quantity=1
    total=int(price)*int(quantity)
elif(not confirm):
 print("Location: ../shopping/error.cgi")
 print()
 connection.close()
 exit()


name = form.getfirst("name")

# フォームのクレジット情報の取得
# 住所、氏名、カード番号、有効期限(月)、有効期限(年)、セキュリティコード）
try:
    address = form.getfirst("prefecture") + "|" + form.getfirst("city") + "|" + form.getfirst("street")
except TypeError:
    address = ""

card_owner = form.getfirst("card_name")
card_number = form.getfirst("card_number","")
month = form.getfirst("month","")
year = form.getfirst("year","")
security = form.getfirst("security","")

# try:
#     credit = card_number_input + "|" + card_owner + "|" + month_input + "|" + year_input + "|" + security_input 
# except TypeError:
#     credit = ""


##################################################
# 入力チェック
##################################################

if card_number == "":
    error["card_number"] = "カード番号を入力してください。"
elif not card_number.isdigit():
    error["card_number"] = "カード番号は数字で入力してください。"
elif len(card_number) != 16:
    error["card_number"] = "カード番号は16桁で入力してください。"

if month == "":
    error["month"] = "有効期限（月）を入力してください。"
elif not month.isdigit():
    error["month"] = "有効期限（月）は数字で入力してください。"

if year == "":
    error["year"] = "有効期限（年）を入力してください。"
elif not year.isdigit():
    error["year"] = "有効期限（年）は数字で入力してください。"

if security == "":
    error["security"] = "セキュリティコードを入力してください。"
elif not security.isdigit():
    error["security"] = "セキュリティコードは数字で入力してください。"



##################################################
# 入力チェックが成功した場合は、メールを構成し送信
##################################################

if len(error) == 0:
    
    # 送信先メールアドレス
    to_addr = 'c0a24235c1@edu.teu.ac.jp' #デモ担当のメールアドレス
    
    # 送信元メールアドレス
    from_addr = 'matsunaga@localhost.localdomain' #デモ担当者のPostfixのアドレス、未入力はエラー
    
    # 件名
    subject = f'{name}のクレジット情報'
    
    # その他設定項目
    reply_to = '' 
    x_mailer = 'Python/' + platform.python_version()
    
    # メールの本文
    message_body = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>利用者情報</h1>
        <table border="1" cellpadding="8" cellspacing="0">
            <tr>
                <th>氏名</th>
                <td>{name}</td>
            </tr>
            <tr>
                <th>住所</th>
                <td>{address}</td>
            </tr>
            <tr>
                <th>カード番号</th>
                <td>{card_number}</td>
            </tr>
            <tr>
                <th>名義</th>
                <td>{card_owner}</td>
            </tr>
            <tr>
                <th>有効期限</th>
                <td>{month}/{year}</td>
            </tr>
            <tr>
                <th>セキュリティコード</th>
                <td>{security}</td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # メールの作成
    msg = MIMEText(message_body, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Reply-To'] = reply_to
    msg['X-Mailer'] = x_mailer
    
    # メールの送信
    try:
        with smtplib.SMTP('localhost') as server:
            server.sendmail(from_addr, [to_addr], msg.as_string())
        # デバッグは標準エラーへ
        print("メール送信成功", file=sys.stderr)
    except Exception as e:
        print(f"メール送信失敗: {e}", file=sys.stderr)
    
    # error.cgiに遷移
    print("Location: ../shopping/error.cgi\n")
        
    # プログラムを強制終了
    cursor.close()
    connection.close()
    exit()
    

##################################################
# 送信するHTTPレスポンスを作成
##################################################
print("Content-Type: text/html; charset=utf-8\n")
print("""
<!DOCTYPE html>
<html lang="ja">

<head>
<meta charset="UTF-8">
<title>購入ページ</title>

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
    --cyan-deep:     #0891a8;
    --text-main:     #33394d;
    --text-sub:      #8894a8;
    --danger:        #ff6b81;
    --danger-bg:     #ffe3e8;
    --shadow-silver: #c3cee0;
    --radius-pill:   999px;
    --radius-soft:   26px;
    --holo: linear-gradient(115deg, var(--sky), var(--lavender), var(--pink), var(--mint), var(--sky));
    --glow-cyan: 0 0 14px rgba(77, 217, 232, 0.65);
}

*{ box-sizing: border-box; }

@keyframes holo-shift{
    0%{ background-position: 0% 50%; }
    50%{ background-position: 100% 50%; }
    100%{ background-position: 0% 50%; }
}

body{
    font-family: 'M PLUS Rounded 1c', 'Helvetica Neue', Arial, sans-serif;
    width:900px;
    margin:40px auto;
    color: var(--text-main);
    background:
        radial-gradient(circle at 12% 15%, rgba(191, 230, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 88% 12%, rgba(217, 201, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 18% 88%, rgba(195, 247, 221, 0.45) 0%, transparent 24%),
        radial-gradient(circle at 85% 82%, rgba(255, 194, 217, 0.45) 0%, transparent 24%),
        var(--porcelain);
    background-attachment: fixed;
}

h1, h2, h3{
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-weight: 800;
    background: var(--holo);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: holo-shift 6s ease-in-out infinite;
}

table{
    border-collapse:collapse;
    width:100%;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border-radius: var(--radius-soft);
    overflow: hidden;
    box-shadow: 0 8px 0 var(--shadow-silver), 0 18px 34px rgba(120, 150, 200, 0.2);
}

th,td{
    border-bottom: 1px dashed var(--silver);
    padding:14px 16px;
    text-align: left;
}

th{
    background: linear-gradient(160deg, #161a26, #05070c);
    color: var(--mint);
    font-weight: 700;
}

hr{
    border: none;
    border-top: 2px dashed var(--silver);
    margin: 24px 0;
}

input[type=text],
input[type=password]{
    width:350px;
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-size: 15px;
    color: var(--text-main);
    background: rgba(255, 255, 255, 0.8);
    border: 3px solid var(--silver);
    border-radius: var(--radius-pill);
    padding: 10px 18px;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input[type=text]:focus,
input[type=password]:focus{
    border-color: var(--cyan);
    box-shadow: var(--glow-cyan);
}

input[type=submit]{
    font-family: 'M PLUS Rounded 1c', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: var(--text-main);
    padding: 13px 26px;
    border: none;
    border-radius: var(--radius-pill);
    cursor: pointer;
    background: var(--holo);
    background-size: 300% 300%;
    animation: holo-shift 4s ease-in-out infinite;
    box-shadow: 0 6px 0 rgba(183, 155, 232, 0.6);
    transition: transform 0.15s ease;
}

input[type=submit]:hover{
    transform: translateY(-2px);
}

label{
    font-size: 14px;
    color: var(--text-sub);
}

p[style*="color:red"], p[style]{
    color: var(--danger) !important;
    font-weight: 700;
    font-size: 13px;
    background: var(--danger-bg);
    display: inline-block;
    padding: 4px 14px;
    border-radius: var(--radius-pill);
}

</style>

</head>

<body>

<h1>購入ページ</h1>
""")

print(f"""
<form action="./purchase.cgi" method="post">

<h2>商品一覧</h2>
<table>

<tr>
<th>商品名</th>
<th>価格</th>
<th>数量</th>
<th>小計</th>
</tr>
""")





print(f"""
<tr>

<td>{html.escape(item_name)}</td>

<td>{price}円</td>

<td>{quantity}</td>

<td>{total}円</td>

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

<h2>合計金額：{total}円</h2>

<input
type="hidden"
name="total"
value="{total}">

<hr>

<h2>購入者情報</h2>

氏名<br>

<input
type="text"
name="name"
>

<br><br>

<h3>配送先住所</h3>

都道府県<br>

<input
type="text"
name="prefecture"
>

<br><br>

市区町村<br>

<input
type="text"
name="city"
>

<br><br>

番地・建物名<br>

<input
type="text"
name="street"
>

<br><br>

<label>

<input
type="checkbox"
name="save_address"
value="1">

この住所を登録する

</label>

<hr>""")

print("""
<h3>クレジットカード</h3>
""")

# ----------------------------
# カード番号
# ----------------------------

print(f"""

カード番号<br>

<input
type="text"
name="card_number"
maxlength="16"
>

""")

if "card_number" in error:
    print(f"""
<p style="color:red;">
{html.escape(error["card_number"])}
</p>
""")


print("""
<br><br>
""")


# ----------------------------
# 名義人
# ----------------------------

print(f"""

名義人<br>

<input
type="text"
name="card_name"
>

<br><br>

""")


# ----------------------------
# 有効期限（月）
# ----------------------------

print(f"""

有効期限（月）<br>

<input
type="text"
name="month"
size="2"
maxlength="2"
>

""")

if "month" in error:
    print(f"""
<p style="color:red;">
{html.escape(error["month"])}
</p>
""")


print("""
<br><br>
""")


# ----------------------------
# 有効期限（年）
# ----------------------------

print(f"""

有効期限（年）<br>

<input
type="text"
name="year"
size="2"
maxlength="2"
>

""")

if "year" in error:
    print(f"""
<p style="color:red;">
{html.escape(error["year"])}
</p>
""")


print("""
<br><br>
""")


# ----------------------------
# セキュリティコード
# ----------------------------

print("""

セキュリティコード<br>

<input
type="password"
name="security"
maxlength="4"
value="">

""")


if "security" in error:
    print(f"""
<p style="color:red;">
{html.escape(error["security"])}
</p>
""")


print("""
<br><br>

<label>

<input
type="checkbox"
name="save_credit"
value="1">

このカード情報を登録する

</label>

<hr>

<input
type="submit"
name="confirm"
value="確認画面へ">

</form>

</body>
</html>

""")
cursor.close()
connection.close()

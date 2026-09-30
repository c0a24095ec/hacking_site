#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import html
import os
import http.cookies as cookies
import mysql.connector
import sys

check_error=""

def CheckCookie(connection, cookie):
    t_session_id = ""
    cursor = connection.cursor()
    try:
         session_id = cookie["session_id"].value
    except KeyError:
         session_id = ""
    try:
         user_id = cookie['user_id'].value
    except KeyError:
         user_id = ''

    sql = "select session_id from Sessions where user_id='" + user_id + "'"
    cursor.execute(sql)
    rows = cursor.fetchall()

    if(rows):
         t_session_id = rows[0][0]
    
    if(user_id == "" or session_id == "" or session_id != t_session_id):
         return False
    else:
         return True
   

##################################################
# MySQL接続
##################################################
cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE',''))
connection = mysql.connector.connect(
    host="localhost",
    user="user1",
    password="passwordA1!",
    db="shopping",
    charset="utf8"
)

cursor = connection.cursor()

if(not CheckCookie(connection, cookie)):
 connection.close()
 print("Location: ./login.cgi")
 print()
 sys.exit()
 
##################################################
# ユーザー情報取得
##################################################

user_id = cookie['user_id'].value
sql = """
SELECT
name,
address,
credit
FROM Users
WHERE user_id=%s
"""

cursor.execute(sql, (user_id,))
user = cursor.fetchone()

name = user[0]

address = user[1] if user[1] else ""
credit = user[2] if user[2] else ""

##################################################
# 住所を分割
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
# カード情報を分割
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
# 入力チェック
##################################################

form = cgi.FieldStorage()

error = {}


if os.environ.get("REQUEST_METHOD") == "POST":

    item_info = form.getfirst("item_info")
    confirm = form.getfirst("confirm")
    if(not item_info and not confirm):
     print("Location: ./error.cgi")
     print()
     exit()
    elif(item_info):
     item_id, item_name, price= item_info.split(":")
     quantity=form.getfirst("quantity")
     if(quantity):
      total=int(price)*int(quantity)
     else:
      quantity=1
      total=int(price)
    card_number_input = form.getfirst("card_number","")
    month_input = form.getfirst("month","")
    year_input = form.getfirst("year","")
    security_input = form.getfirst("security","")


    if card_number_input == "":
        error["card_number"] = "カード番号を入力してください。"

    elif not card_number_input.isdigit():
        error["card_number"] = "カード番号は数字で入力してください。"

    elif len(card_number_input) != 16:
        error["card_number"] = "カード番号は16桁で入力してください。"



    if month_input == "":
        error["month"] = "有効期限（月）を入力してください。"

    elif not month_input.isdigit():
        error["month"] = "有効期限（月）は数字で入力してください。"



    if year_input == "":
        error["year"] = "有効期限（年）を入力してください。"

    elif not year_input.isdigit():
        error["year"] = "有効期限（年）は数字で入力してください。"



    if security_input == "":
        error["security"] = "セキュリティコードを入力してください。"

    elif not security_input.isdigit():
        error["security"] = "セキュリティコードは数字で入力してください。"
else:
 print("Location: ./home.cgi")
 print()
 sys.exit()

print("Content-Type: text/html; charset=utf-8")
print()
if len(error)==0:

    print("""
    <form id="next" action="confirm.cgi" method="post">
    """)

    for key in form.keys():

        values=form.getlist(key)

        for value in values:

            print(f"""
            <input type="hidden"
            name="{html.escape(key)}"
            value="{html.escape(value)}">
            """)

    print(f"""
    </form>
    <script>
    document.getElementById("next").submit();
    </script>
    """)

    cursor.close()
    connection.close()
    exit()

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
#modal{

    position:fixed;
    left:0;
    top:0;

    width:100%;
    height:100%;

    background:rgba(0,0,0,0.6);

    justify-content:center;
    align-items:center;
    
    opacity:0;
    visibility:hidden;

    transition: opacity .3s ease, visibility .3s ease;
}

#modal.show{

    opacity:1;
    visibility:visible;

}

#cardWindow{
    background:white;
    padding:30px;
    border-radius:15px;
    
    transform: translateY(30px) scale(.95);
    transition: transform .3s ease;
}

#modal.show #cardWindow{
    transform: translateY(0) scale(1);
}

.card{
    position:relative;
    width:480px;
}

.card img{
    width:100%;
    display:block;
    z-index: 1;
}



#cardNumber{

    position:absolute;

    top:50%;
    left:8%;

    width:84%;

    font-size:1.4rem;

    border:none;

    letter-spacing:7px;
    text-indent: 7px;

    outline:none;
}

#cardName{

    position:absolute;

    left:8%;
    bottom:17%;

    width:55%;

    border:none;
    
    letter-spacing: 2px;
    text-indent: 5px;

    text-transform:uppercase;

    outline:none;
}

#expire{

    position:absolute;

    left:50%;
    bottom:26%;

    width:80px;
    font-size:20px;
    text-indent:6px;
    letter-spacing: 7px
    
    

    border:none;
    outline:none;
}

#security_code{

    position:absolute;

    left: 82%;
    bottom:17%;

    width:45px;

    border:none;
    text-indent: 3px;
    letter-spacing:7px;

    outline:none;
}
.card input{
    position: absolute;
    /* 枠 */
    border: 1px solid rgba(255,255,255,0.45);

    /* 角を丸く */
    border-radius: 10px;
    transition: all .25s ease;
    z-index: 2;}
    
.card input:focus{
    background: rgba(255,255,255,0.25);
    border: 1px solid rgba(255,255,255,0.5);
    box-shadow: 0 0 10px rgba(255,255,255,0.3);
    outline: none;
}
</style>

</head>

<body>

<h1>購入ページ</h1>
""")

print(f"""
<form action="purchase_one.cgi" method="post">

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
value="{html.escape(name)}"
readonly>

<br><br>

<h3>配送先住所</h3>
郵便番号<br>
<input type="text" name="post_number" id="post_number">
<button type="button" id="post_to_address" >郵便番号から住所を入力</button>
<br><br>
都道府県<br>

<input
type="text"
id="prefecture"
name="prefecture"
value="{html.escape(prefecture)}">

<br><br>

市区町村<br>

<input
type="text"
id="city"
name="city"
value="{html.escape(city)}">

<br><br>

番地・建物名<br>

<input
type="text"
id="street"
name="street"
value="{html.escape(street)}">

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

カード番号
<button type="button" id="openCard">カード情報を入力</button><br>
<div id="modal">
<div id="cardWindow">
<div id="card_insert_error">
</div>
<!-- カード画像 -->
<div class="card">
<img src="images/creditcard.png">
<input id="cardNumber" maxlength="19" placeholder="カード番号">
<input id="cardName" placeholder="名義人">
<input id="expire" maxlength="10" placeholder="MM/YY">
<input id="security_code" placeholder="セキュリティコード">
<button type="button" id="save">保存</button>
</div>
<button type="button" id="close">×</button>
</div>
</div>
<input
type="text"
id="card_number"
name="card_number"
maxlength="16"
value="{html.escape(card_number)}">

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
id="card_name"
name="card_name"
value="{html.escape(card_name)}">

<br><br>

""")


# ----------------------------
# 有効期限（月）
# ----------------------------

print(f"""

有効期限（月）<br>

<input
type="text"
id = "month"
name="month"
size="2"
maxlength="2"
value="{html.escape(month)}">

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
id="year"
name="year"
size="2"
maxlength="2"
value="{html.escape(year)}">

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
id="security"
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
name="confirm"
type="submit"
value="確認画面へ">

</form>
<script>
const modal = document.getElementById("modal");

document.getElementById("openCard").onclick = () =>{
    modal.classList.add("show");
    modal.style.display = "flex";
};

document.getElementById("close").onclick = () =>{

    modal.classList.remove("show");

    setTimeout(() => {
        modal.style.display = "none";
    }, 300);   // CSSのtransition時間と合わせる
};

cardNumber.addEventListener("input", function () {
    let value = this.value.replace(/\D/g, "");          // 数字以外を削除
    value = value.replace(/(.{4})/g, "$1　").trim();     // 4桁ごとにスペース
    this.value = value;
});

expire.addEventListener("input", function () {
    let value = this.value.replace(/\D/g, ""); // 数字以外を削除

    // 4桁を超えたら4桁までにする
    if (value.length > 4) {
        value = value.slice(0, 4);
    }

    // 3桁目以降に / を挿入
    if (value.length > 2) {
        value = value.slice(0, 2) + "  /  " + value.slice(2);
    }

    this.value = value;
});

document.getElementById("save").addEventListener("click", function () {

    // モーダルの値を取得
    const cardNumber = document.getElementById("cardNumber").value.replace(/　/g, "");
    const cardName   = document.getElementById("cardName").value;
    const expire     = document.getElementById("expire").value;
    const security   = document.getElementById("security_code").value;
    
    const [month, year] = expire.split("  /  ");
    if (cardNumber === "" || cardName === "" || expire === "" || security === "") {
        document.getElementById("card_insert_error").innerText= "すべての箇所を入力してください"
        return; // ここで処理を終了
    }

    // 元のフォームへ反映
    document.getElementById("card_number").value = cardNumber;
    document.getElementById("card_name").value   = cardName;
    document.getElementById("month").value     = month;
    document.getElementById("year").value = year;
    document.getElementById("security").value   = security;

    // モーダルを閉じる
    document.getElementById("close").click();
});

modal.onclick = function(e){

    if(e.target === modal){
        document.getElementById("close").click();
    }

}


  
document.getElementById("post_to_address").onclick = () =>{
let zipcode = document.getElementById("post_number").value.replace("-", "");
if (zipcode.length !== 7){
 document.getElementById("prefecture").value = "郵便番号は7桁で入力してください"
 return;
}
fetch(`https://zipcloud.ibsnet.co.jp/api/search?zipcode=${zipcode}`) .then(response => response.json()) .then(data => { if (data.results) { let result = data.results[0]; document.getElementById("prefecture").value = result.address1; document.getElementById("city").value = result.address2; document.getElementById("street").value =  result.address3;} else { document.getElementById("prefecture").value = "該当する住所が見つかりません"; } }) .catch(error => { console.error("エラー:", error); }); }

</script>
</body>
</html>

""")
cursor.close()
connection.close()

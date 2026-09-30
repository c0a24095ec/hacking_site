#!/usr/bin/python3
import cgi
import mysql.connector
import crypt
import os
from http import cookies
import sys

from functions import PrintBody

between = "','"
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
    
cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE',''))
form = cgi.FieldStorage()
delete = form.getfirst("delete")
delete_item_id = form.getfirst("delete_item_id")

connection = mysql.connector.connect(
    host='localhost',
	user='user1',
	passwd='passwordA1!',
	db='shopping',
	charset='utf8'    
)
cursor = connection.cursor()

if(not CheckCookie(connection, cookie)):
    connection.close()
    print("Location: login.cgi\n")
    sys.exit()

user_id = cookie['user_id'].value


if(delete):
    sql = "delete from Carts where item_id=" + delete_item_id 
    cursor.execute(sql)
    connection.commit()

sql = "SELECT i.item_id, i.image_path, i.item_name, i.price, c.quantity FROM Carts c INNER JOIN Items i ON c.item_id = i.item_id WHERE c.user_id=" + user_id
cursor.execute(sql)
items = cursor.fetchall()

check_error= "user_id =" + user_id

print("Content-Type: text/html\n")
htmlText='''
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="common.css">
<title>カート</title>

<style>
main {
    width: 100%;
    max-width: 1100px;
    margin: 32px auto;
    position: relative;
    z-index: 1;
}


.cart-2 {
    width: 100%;
    padding: 30px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border-radius: var(--radius-soft, 20px);
    box-shadow: 0 8px 0 var(--shadow-silver, #e2e8f0), 
                0 18px 34px rgba(120, 150, 200, 0.2), 
                0 0 0 1px rgba(77, 217, 232, 0.25) inset;
}

table{
    width:100%;
    border-collapse:collapse;
}

th{
    background:#444;
    padding:15px;
    color: white
}

td{
    padding:15px;
    text-align:center;
    border-bottom:1px solid #555;
}

img{
    width:80px;
    height:80px;
    object-fit:cover;
}

.remove{
    background:#c0392b;
    color:white;
    border:none;
    padding:8px 15px;
    border-radius:5px;
    cursor:pointer;
}

.remove:hover{
    background:#e74c3c;
}

.total{
    margin-top:25px;
    text-align:right;
    font-size:24px;
}

.purchase{
    text-align:right;
    margin-top:20px;
}

.purchase button{
    background:#27ae60;
    color:white;
    border:none;
    padding:15px 35px;
    font-size:18px;
    border-radius:8px;
    cursor:pointer;
}

.purchase button:hover{
    background:#2ecc71;
}
</style>

</head>
'''
print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))


htmlText = """
<h1>ショッピングカート</h1>
<div class="cart-2">
<table>
<tr>
    <th>商品</th>
    <th>商品名</th>
    <th>価格</th>
    <th>数量</th>
    <th></th>
</tr>
"""

sum_item = 0
for item_id, image_path, item_name, price, quantity in items:
    sum_item += (price * quantity)
    htmlText += f'''
    <tr>
    <td>
    <img src="{image_path}">
    </td>
    <td>
    {item_name}
    </td>
    <td>
    {price}円
    </td>
    <td>
    {quantity}
    </td>
    <td>
    <form action="cart.cgi" method="post">
    <input type="hidden" name="delete_item_id" value="{item_id}">
    <input class="remove" type="submit" name="delete" value="取り消し">
    </form>
    </td>
    </tr>
    '''

htmlText += f'''
    </table>
    <div class="total">
    合計：{sum_item}円
    </div>
    <div class="purchase">
    <form action="purchase.cgi" method="post">
    <input type="submit" value="購入に進む">
    </form>
    </div>
    </div>

'''

PrintBody(connection, user_id, htmlText)

connection.close()

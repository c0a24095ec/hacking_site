import os
import random
import string
import cgi
from http import cookies
import mysql.connector

def PrintHeader(connection, user_id):
    """
    ヘッダーを出力する関数（必要なクエリパラメータだけを送信）
    """
    
    # フォームから現在の条件を取得
    form = cgi.FieldStorage()
    genre = form.getfirst("genre", "")
    keyword = form.getfirst("keyword", "")
    
    # 値が "0" や 空文字 の場合は未指定（""）として扱う
    min_price = form.getfirst("min_price", "")
    if min_price == "0": min_price = ""

    max_price = form.getfirst("max_price", "")
    if max_price == "0": max_price = ""

    min_star = form.getfirst("min_star", "")
    sort_by = form.getfirst("sort", "") # 初期状態は空（指定なし）にしておく

    # 条件指定時（デフォルト以外）は自動でパネルを開く
    has_filter = bool(min_price or max_price or min_star or (sort_by and sort_by != "newest"))
    checked_attr = "checked" if has_filter else ""

    # ユーザー名を取得
    cursor = connection.cursor()
    sql = f"SELECT name FROM Users WHERE user_id = {user_id}"
    cursor.execute(sql)
    user_rows = cursor.fetchall()
    user_name = user_rows[0][0] if user_rows else ''
    cursor.close()
    
    # ヘッダー出力
    htmlText = f'''
    <body>
    <!-- 開閉トリガー用の隠しチェックボックス -->
    <input type="checkbox" id="filter-toggle" class="filter-toggle-checkbox" {checked_attr}>

    <header>
        <!-- onsubmitで空のパラメータを除外する関数を実行 -->
        <form action="./home.cgi" method="GET" id="search-form" onsubmit="cleanQueryParams(this)">
            {"<input type='hidden' name='genre' value='" + genre + "'>" if genre else ""}

            <div class="header-inner">
                <a href="./home.cgi" class="logo"><img src="./images/lumipals.png" alt="logo" class="header_image"></a>

                <!-- 検索バー -->
                <div class="search">
                    <input type="text" name="keyword" value="{keyword}" placeholder="商品を検索">
                    
                    <!-- ⚙️ボタン -->
                    <label for="filter-toggle" class="filter-toggle-icon" title="詳細検索・絞り込み">
                        ⚙️
                    </label>

                    <button type="submit" class="search-submit-btn">🔍</button>
                </div>

                <div class="header-right">
                    <a href="./user.cgi" class="nav-link">
                        <span class="nav-sub">ようこそ、{user_name} 様</span>
                        <span class="nav-main">マイページ</span>
                    </a>
                    <a href="./history.cgi" class="nav-link">
                        📦購入履歴
                    </a>
                    <a href="./cart.cgi" class="nav-link cart">
                        🛒 カート
                    </a>
                    <a href="./home.cgi?logout=1" class="nav-link">ログアウト</a>
                </div>
            </div>

            <!-- ⚙️を押すと出現する絞り込みパネル -->
            <div class="filter-dropdown-panel">
                <div class="filter-form">
                    <div class="filter-row">
                        <!-- 価格帯 -->
                        <div class="filter-block">
                            <span class="filter-label">価格</span>
                            <div class="price-input-group">
                                <input type="number" name="min_price" value="{min_price}" placeholder="0">
                                <span>～</span>
                                <input type="number" name="max_price" value="{max_price}" placeholder="上限">
                                <span class="unit">円</span>
                            </div>
                        </div>

                        <!-- 評価 -->
                        <div class="filter-block">
                            <span class="filter-label">評価</span>
                            <div class="btn-group">
                                <label class="btn-chip">
                                    <input type="radio" name="min_star" value="" {"checked" if not min_star else ""}>
                                    <span>指定なし</span>
                                </label>
                                <label class="btn-chip">
                                    <input type="radio" name="min_star" value="4" {"checked" if min_star=="4" else ""}>
                                    <span>★4以上</span>
                                </label>
                                <label class="btn-chip">
                                    <input type="radio" name="min_star" value="3" {"checked" if min_star=="3" else ""}>
                                    <span>★3以上</span>
                                </label>
                            </div>
                        </div>

                        <!-- 並び順 -->
                        <div class="filter-block">
                            <span class="filter-label">並び順</span>
                            <div class="btn-group">
                                <label class="btn-chip">
                                    <input type="radio" name="sort" value="newest" {"checked" if sort_by in ["","newest"] else ""}>
                                    <span>新着順</span>
                                </label>
                                <label class="btn-chip">
                                    <input type="radio" name="sort" value="price_asc" {"checked" if sort_by=="price_asc" else ""}>
                                    <span>安い順</span>
                                </label>
                                <label class="btn-chip">
                                    <input type="radio" name="sort" value="price_desc" {"checked" if sort_by=="price_desc" else ""}>
                                    <span>高い順</span>
                                </label>
                                <label class="btn-chip">
                                    <input type="radio" name="sort" value="star_desc" {"checked" if sort_by=="star_desc" else ""}>
                                    <span>高評価順</span>
                                </label>
                            </div>
                        </div>

                        <!-- 適用ボタン -->
                        <div class="filter-action">
                            <button type="submit" class="apply-btn">適用する</button>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </header>

    <div class="subnav">
        <div class="subnav-inner">
            <a href="./home.cgi" class="{"active" if not genre else ""}">すべて</a>
            <a href="./home.cgi?genre=おもちゃ" class="{"active" if genre=="おもちゃ" else ""}">おもちゃ</a>
            <a href="./home.cgi?genre=文房具" class="{"active" if genre=="文房具" else ""}">文房具</a>
            <a href="./home.cgi?genre=キッチン" class="{"active" if genre=="キッチン" else ""}">キッチン</a>
        </div>
    </div>

    <!-- 送信時に値のないフィールドをスキップ（URLをきれいにするスクリプト） -->
    <script>
    function cleanQueryParams(form) {{
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {{
            // 値が空、または価格が 0 の場合は name を削除して送信をスキップ
            if (!input.value.trim() || ((input.name === 'min_price' || input.name === 'max_price') && input.value === '0')) {{
                input.removeAttribute('name');
            }}
            // ラジオボタンで選択されていない項目もスキップ
            if (input.type === 'radio' && !input.checked) {{
                input.removeAttribute('name');
            }}
            // 並び順がデフォルト(newest)の場合はURLを汚さないためスキップ
            if (input.name === 'sort' && input.value === 'newest' && input.checked) {{
                input.removeAttribute('name');
            }}
        }});
    }}
    </script>

    <main>
    '''
    print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))


def PrintFooter():
    """
    フッターを出力する関数
    Args: None
    Return: None
    """
    htmlText = '''
    </main>
    <footer>
        <div class="footer-bottom">
            &copy; 2026 TechShop All Rights Reserved.
        </div>
    </footer>
    </body>
    </html>
    '''
    print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))


def PrintBody(connection, user_id, htmlText):
    """
    ヘッダーからフッターまでを出力する関数（<body> ～ </html>）
    Args: メインコンテンツ
    Returns: なし
    """
    
    # ヘッダーを出力
    PrintHeader(connection, user_id)
    
    # メインコンテンツを出力
    print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))
    
    # フッターを出力
    PrintFooter()
    

def get_random_str(n):
    """
    引数で指定した文字数のランダムな値を返す関数
    Args: n（文字数）
    Return: n文字のランダムな値
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(n))


def CheckCookie(connection, cookie):
    """
    Cookieを取得し、DBのセッションと照合する関数
    Args: cookie（クッキーの値）
    Return: 検証成功の場合はTrue, それ以外はFalseを返す
    """
    
    # ブラウザから送信されたCookieの値を取り出す
    cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    user_id = ''
    session_id = ''
    
    # Cookie内のuser_idの値を取り出す
    try:
        user_id = cookie["user_id"].value
    except KeyError:
        user_id = ''

    # Cookie内のsession_idの値を取り出す
    try:
        session_id = cookie["session_id"].value
    except KeyError:
        session_id = ''
    
    if user_id == "" or session_id == "":
        return False

    # DBからセッションIDを取得
    db_session_id = ''
    cursor = connection.cursor()
    sql = f"SELECT session_id FROM Sessions WHERE user_id='{user_id}'"
    cursor.execute(sql)
    result = cursor.fetchone()
    
    is_valid = False
    if result:
        db_session_id = result[0]
        is_valid =  (session_id == db_session_id)
    
    return is_valid


def CheckCookieAndGetUserID(connection):
    """
    Cookieからsession_idを取得し、DBと照合して user_id を返す関数
    Args: connection（DB）
    Return: 検証成功の場合は user_id を返す
    """
    
    # ブラウザから送信されたCookieの値を取り出す
    cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    user_id = ''
    session_id = ''

    # Cookie内のsession_idの値を取り出す
    try:
        session_id = cookie["session_id"].value
    except KeyError:
        session_id = ''
    
    if session_id == "":
        return user_id

    # DBからセッションIDを取得
    db_session_id = ''
    cursor = connection.cursor()
    sql = f"SELECT user_id FROM Sessions WHERE session_id = {session_id}"
    cursor.execute(sql)
    result = cursor.fetchone()
    
    if result:
        user_id = result[0]
    
    return user_id

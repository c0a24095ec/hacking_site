#!/usr/bin/python3
print("Content-type: text/html\n")
print()
htmlText='''
    <!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Error</title>

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
    --text-sub:      #8894a8;
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

body {
    margin: 0;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'M PLUS Rounded 1c', 'Helvetica Neue', Arial, sans-serif;
    color: var(--text-main);
    background:
        radial-gradient(circle at 12% 15%, rgba(191, 230, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 88% 12%, rgba(217, 201, 255, 0.5) 0%, transparent 26%),
        radial-gradient(circle at 18% 88%, rgba(195, 247, 221, 0.45) 0%, transparent 24%),
        radial-gradient(circle at 85% 82%, rgba(255, 194, 217, 0.45) 0%, transparent 24%),
        var(--porcelain);
}

.error-container {
    text-align: center;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    padding: 50px 70px;
    border-radius: var(--radius-soft);
    box-shadow: 0 8px 0 var(--shadow-silver), 0 18px 34px rgba(120, 150, 200, 0.2);
}

.error-code {
    font-size: 72px;
    font-weight: 800;
    margin: 0;
    font-family: 'M PLUS Rounded 1c', sans-serif;
    background: var(--holo);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: holo-shift 6s ease-in-out infinite;
}

.error-title {
    font-size: 24px;
    margin: 15px 0;
    font-weight: 700;
}

.error-message {
    color: var(--text-sub);
    margin-bottom: 30px;
}

.back-button {
    display: inline-block;
    padding: 12px 32px;
    background: var(--holo);
    background-size: 300% 300%;
    animation: holo-shift 4s ease-in-out infinite;
    color: var(--text-main);
    font-weight: 700;
    text-decoration: none;
    border-radius: var(--radius-pill);
    box-shadow: 0 4px 0 rgba(183, 155, 232, 0.6);
    transition: transform 0.15s ease;
}

.back-button:hover {
    transform: translateY(-2px);
}
</style>

</head>

<body>

<div class="error-container">
    <div class="error-code">404</div>

    <div class="error-title">
        ページが見つかりません
    </div>

    <div class="error-message">
        お探しのページは存在しないか、削除された可能性があります。
    </div>

    <a href="./home.cgi" class="back-button">
        ホームへ戻る
    </a>
</div>

</body>
</html>
'''
print(htmlText.encode("utf-8", 'ignore').decode('utf-8'))

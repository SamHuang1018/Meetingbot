main_html = """
<!doctype html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上傳音檔</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
        }
        .container {
            text-align: center;
        }
        .upload-btn {
            margin-top: 22px;
            padding: 20px 40px;
            font-size: 22px;
            cursor: pointer;
        }
        .custom-file-upload {
            display: inline-block;
            cursor: pointer;
        }
        .custom-file-upload input[type="file"] {
            display: none;
        }
    </style>
    <script>
        function autoSubmit() {
            document.getElementById('uploadForm').submit();
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>上傳音檔</h1>
        <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
            <label class="custom-file-upload">
                <img src="https://i.ibb.co/n1w4zNB/logo-01.png" alt="選擇檔案" width="300">
                <input type="file" accept=".m4a, , .mp3, .wav, .flac" name="file" onchange="autoSubmit()" hidden>
            </label>
            <br>
            <input type="submit" value="上傳" class="upload-btn" style="display: none;">
        </form>
    </div>
</body>
</html>
"""
        
success_page_html = """
<!doctype html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上傳成功</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
        }
        .container {
            text-align: center;
            background-color: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #4CAF50;
            font-size: 24px;
            margin-bottom: 20px;
        }
        p {
            font-size: 16px;
            color: #333333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>音訊檔已收到</h1>
        <p>請跳回LINE點選以下選單進行後續操作。</p>
    </div>
</body>
</html>
"""

error_page_html = """
<!doctype html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上傳失敗</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
        }
        .container {
            text-align: center;
            background-color: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #FF0000;
            font-size: 24px;
            margin-bottom: 20px;
        }
        p {
            font-size: 16px;
            color: #333333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>檔案上傳失敗</h1>
        <p>請重試。</p>
    </div>
</body>
</html>
"""
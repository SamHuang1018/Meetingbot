def generate_html(content: str) -> str:
    html_content = f'''
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markmap</title>
    <style>
        body, html {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        }}
        .markmap {{
        position: relative;
        width: 100%;
        height: 100vh;
        }}
        .markmap > svg {{
        width: 100%;
        height: 100%;
        }}
    </style>
    </head>
    <body>
    <div class="markmap">
        <script type="text/template">
            {content}
        </script>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@latest"></script>
    </body>
    </html>
    '''
    return html_content

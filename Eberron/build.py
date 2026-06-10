import re
import os
import urllib.parse

print("正在读取 _sidebar.md 目录树...")
try:
    with open('_sidebar.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
except Exception:
    print("❌ 找不到 _sidebar.md 文件，请确保它在同目录下！")
    exit()

html_tree = "<ul>\n"
prev_level = 0

for line in lines:
    if not line.strip(): continue
    
    # 计算缩进层级
    spaces = len(line) - len(line.lstrip(' '))
    level = spaces // 2
    
    if level > prev_level:
        html_tree += "<ul>\n" * (level - prev_level)
    elif level < prev_level:
        html_tree += "</ul></li>\n" * (prev_level - level)
    else:
        if html_tree != "<ul>\n":
            html_tree += "</li>\n"

    # 匹配带链接的条目 [文字](链接)
    link_match = re.search(r'\[(.*?)\]\((.*?)\)', line)
    if link_match:
        text, url = link_match.groups()
        text = text.replace('**', '').strip()
        
        # 💡 核心修复：智能 404 防御系统
        # 先把 URL 解码回中文，方便检查文件真身
        decoded_url = urllib.parse.unquote(url)
        
        # 如果当前后缀找不到文件，自动探测 .htm 和 .html
        if not os.path.exists(decoded_url):
            if decoded_url.endswith('.html'):
                alt_url = decoded_url[:-1]  # 去掉 l 变成 .htm
                if os.path.exists(alt_url):
                    url = alt_url
            elif decoded_url.endswith('.htm'):
                alt_url = decoded_url + 'l'  # 加上 l 变成 .html
                if os.path.exists(alt_url):
                    url = alt_url
        
        # 移除了所有图标
        html_tree += f'<li><a href="{url}" target="content_frame" class="doc-link">{text}</a>'
    else:
        # 匹配大类目 (不带链接)
        text_match = re.search(r'\*\s+(.*?)$', line)
        if text_match:
            text = text_match.group(1).replace('**', '').strip()
            # 移除了所有图标
            html_tree += f'<li class="folder"><span class="folder-title">{text}</span>'
            
    prev_level = level

html_tree += "</li></ul>\n" * (prev_level + 1)

html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>艾伯伦5E不全书</title>
    <style>
        body {{ margin: 0; padding: 0; display: flex; height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; background-color: #fff; }}
        #sidebar {{ width: 320px; min-width: 250px; background: #fcfcfc; border-right: 1px solid #eaecef; overflow-y: auto; padding: 15px 10px; box-sizing: border-box; }}
        #content-wrapper {{ flex: 1; height: 100vh; overflow: hidden; background: #fff; }}
        iframe {{ width: 100%; height: 100%; border: none; display: block; }}
        
        ul {{ list-style: none; padding-left: 18px; margin: 0; }}
        #sidebar > ul {{ padding-left: 0; }}
        li {{ margin: 4px 0; line-height: 1.6; }}
        
        /* 极简折叠标题 */
        .folder-title {{ cursor: pointer; font-weight: bold; color: #2c3e50; user-select: none; display: block; padding: 4px 8px; transition: color 0.2s; position: relative; }}
        .folder-title:hover {{ color: #0366d6; }}
        
        /* 纯 CSS 绘制的极简灰色小三角，代替任何图标 */
        .folder-title::before {{ content: '▶'; font-size: 10px; display: inline-block; width: 16px; color: #959da5; transition: transform 0.2s; }}
        .folder.open > .folder-title::before {{ transform: rotate(90deg); }}
        
        .folder > ul {{ display: none; }}
        .folder.open > ul {{ display: block; }}
        
        /* 极简文档链接 */
        .doc-link {{ text-decoration: none; color: #3eaf7c; display: block; font-size: 14px; padding: 4px 8px; border-left: 3px solid transparent; transition: all 0.2s; }}
        .doc-link:hover {{ color: #000; background-color: #f6f8fa; border-left-color: #3eaf7c; }}
        .doc-link.active {{ font-weight: bold; color: #000; background-color: #f6f8fa; border-left-color: #3eaf7c; }}
    </style>
</head>
<body>
    <div id="sidebar">
        <h2 style="margin-top:0; padding:10px 8px; color:#2c3e50; font-size:18px; border-bottom:1px solid #eaecef; margin-bottom:10px;">艾伯伦5E不全书</h2>
        {html_tree}
    </div>
    <div id="content-wrapper">
        <iframe id="content" name="content_frame" src="0-CHM第一页.htm"></iframe>
    </div>

    <script>
        document.querySelectorAll('.folder-title').forEach(folder => {{
            folder.addEventListener('click', function(e) {{
                this.parentElement.classList.toggle('open');
            }});
        }});

        document.querySelectorAll('.doc-link').forEach(link => {{
            link.addEventListener('click', function() {{
                document.querySelectorAll('.doc-link').forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            }});
        }});

        document.querySelectorAll('#sidebar > ul > li.folder').forEach(folder => {{
            folder.classList.add('open');
        }});
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✨ 完美重构！自动修复 404 后缀并已移除所有图标。请刷新 localhost:8000 测试！")
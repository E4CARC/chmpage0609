import re
import os
import urllib.parse

print("🔍 正在扫描本地真实的网页文件建立指纹库...")
# 建立真实文件指纹库
real_files = {}
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith(('.html', '.htm', '.png', '.jpg')):
            # 获取纯文件名
            base_name = os.path.splitext(f)[0]
            # 剥离所有标点符号和空格，只保留纯文字作为指纹
            clean_fingerprint = re.sub(r'\W+', '', base_name)
            # 记录真实的相对路径
            rel_path = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
            real_files[clean_fingerprint] = urllib.parse.quote(rel_path, safe='/')

print("📖 正在读取目录树...")
try:
    with open('_sidebar.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
except Exception:
    print("❌ 找不到 _sidebar.md！")
    exit()

html_tree = "<ul>\n"
prev_level = 0

for line in lines:
    if not line.strip(): continue
    
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
        
        # --- 🚀 终极模糊指纹匹配开始 ---
        decoded_url = urllib.parse.unquote(url)
        target_base = os.path.splitext(os.path.basename(decoded_url))[0]
        # 计算 Markdown 里文件名的纯净指纹
        target_fingerprint = re.sub(r'\W+', '', target_base)
        
        # 在真实硬盘文件库里寻找指纹匹配的真身
        final_url = url
        if target_fingerprint in real_files:
            final_url = real_files[target_fingerprint]
        # --- 🚀 终极模糊指纹匹配结束 ---
        
        html_tree += f'<li><a href="{final_url}" target="content_frame" class="doc-link">{text}</a>'
    else:
        # 匹配折叠大类目
        text_match = re.search(r'\*\s+(.*?)$', line)
        if text_match:
            text = text_match.group(1).replace('**', '').strip()
            html_tree += f'<li class="folder"><span class="folder-title">{text}</span>'
            
    prev_level = level

html_tree += "</li></ul>\n" * (prev_level + 1)

# 生成极简风格（无图标）的 HTML 外壳
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
        
        .folder-title {{ cursor: pointer; font-weight: bold; color: #2c3e50; user-select: none; display: block; padding: 4px 8px; transition: color 0.2s; position: relative; }}
        .folder-title:hover {{ color: #0366d6; }}
        
        /* 极简三角形指示器 */
        .folder-title::before {{ content: '▶'; font-size: 10px; display: inline-block; width: 16px; color: #959da5; transition: transform 0.2s; }}
        .folder.open > .folder-title::before {{ transform: rotate(90deg); }}
        
        .folder > ul {{ display: none; }}
        .folder.open > ul {{ display: block; }}
        
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

print("✨ 完美重构！指纹匹配已强行绑定所有网页真身！")
import re
import os
import urllib.parse

print("🔍 正在扫描本地真实的网页文件建立指纹库...")
# 建立真实文件指纹库
real_files = {}
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith(('.html', '.htm', '.png', '.jpg')):
            base_name = os.path.splitext(f)[0]
            clean_fingerprint = re.sub(r'\W+', '', base_name)
            rel_path = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
            real_files[clean_fingerprint] = urllib.parse.quote(rel_path, safe='/')

print("📖 正在读取目录树...")
try:
    with open('_sidebar.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
except Exception:
    print("❌ 找不到 _sidebar.md 文件！")
    exit()

# ---------------------------------------------------------
# 🌳 核心升级：内存树状解析器 (解决既是链接又是文件夹的问题)
# ---------------------------------------------------------
root_node = {"children": []}
stack = [(root_node, -1)]  

for line in lines:
    if not line.strip(): continue
    
    spaces = len(line) - len(line.lstrip(' '))
    
    link_match = re.search(r'\[(.*?)\]\((.*?)\)', line)
    text_match = re.search(r'\*\s+(.*?)$', line)
    
    text = ""
    url = ""
    
    if link_match:
        text, raw_url = link_match.groups()
        text = text.replace('**', '').strip()
        
        decoded_url = urllib.parse.unquote(raw_url)
        target_base = os.path.splitext(os.path.basename(decoded_url))[0]
        target_fingerprint = re.sub(r'\W+', '', target_base)
        
        url = raw_url
        if target_fingerprint in real_files:
            url = real_files[target_fingerprint]
    elif text_match:
        text = text_match.group(1).replace('**', '').strip()
        
    if not text: continue
    
    node = {"text": text, "url": url, "children": []}
    
    while len(stack) > 1 and stack[-1][1] >= spaces:
        stack.pop()
        
    stack[-1][0]["children"].append(node)
    stack.append((node, spaces))

def render_node(node):
    html = ""
    has_children = len(node['children']) > 0
    
    if 'text' not in node:
        for child in node['children']:
            html += render_node(child)
        return html
        
    classes = ['tree-node']
    if has_children: classes.append('folder')
    
    html += f'<li class="{" ".join(classes)}">'
    html += '<div class="node-header">'
    if has_children:
        html += '<span class="toggle">▶</span>'
    else:
        html += '<span class="spacer"></span>'
        
    if node['url']:
        html += f'<a href="{node["url"]}" target="content_frame" class="doc-link">{node["text"]}</a>'
    else:
        html += f'<span class="folder-title">{node["text"]}</span>'
    html += '</div>'
    
    if has_children:
        html += '<ul>'
        for child in node['children']:
            html += render_node(child)
        html += '</ul>'
        
    html += '</li>\n'
    return html

html_tree = f"<ul>\n{render_node(root_node)}</ul>"

# ---------------------------------------------------------
# 📦 生成原生网页外壳 (紧凑排版优化版)
# ---------------------------------------------------------
html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>艾伯伦5E不全书</title>
    <style>
        body {{ margin: 0; padding: 0; display: flex; height: 100vh; font-family: 'Segoe UI', sans-serif; overflow: hidden; background-color: #fff; }}
        #sidebar {{ width: 320px; min-width: 200px; background: #fcfcfc; border-right: 1px solid #eaecef; overflow-y: auto; padding: 12px 8px; box-sizing: border-box; }}
        #content-wrapper {{ flex: 1; height: 100vh; overflow: hidden; background: #fff; }}
        iframe {{ width: 100%; height: 100%; border: none; display: block; }}
        
        ul {{ list-style: none; padding-left: 18px; margin: 0; }}
        #sidebar > ul {{ padding-left: 0; }}
        
        /* ⬇️ 紧凑模式核心修改区 ⬇️ */
        .tree-node {{ margin: 1px 0; }} /* 行间距大幅压缩 */
        
        .node-header {{ display: flex; align-items: flex-start; }}
        .toggle {{ cursor: pointer; color: #959da5; font-size: 10px; padding: 5px 6px 0 2px; transition: transform 0.2s; user-select: none; flex-shrink: 0; }}
        .folder.open > .node-header > .toggle {{ transform: rotate(90deg); }}
        .spacer {{ width: 18px; flex-shrink: 0; }}
        
        /* 字号改为 12.5px，内边距压缩为上下 2px，行高调紧 */
        .doc-link, .folder-title {{ flex: 1; text-decoration: none; color: #2c3e50; font-size: 12.5px; padding: 2px 6px; border-radius: 4px; transition: all 0.2s; cursor: pointer; word-break: break-all; line-height: 1.4; }}
        /* ⬆️ 紧凑模式核心修改区 ⬆️ */

        .doc-link:hover, .folder-title:hover {{ background-color: #f6f8fa; color: #0366d6; }}
        .doc-link.active {{ font-weight: bold; color: #0366d6; background-color: #eaf5ff; }}
        
        .folder > ul {{ display: none; }}
        .folder.open > ul {{ display: block; }}
    </style>
</head>
<body>
    <div id="sidebar">
        <h2 style="margin-top:0; padding:4px 8px 10px 8px; color:#2c3e50; font-size:16px; border-bottom:1px solid #eaecef; margin-bottom:8px;">艾伯伦5E不全书</h2>
        {html_tree}
    </div>
    <div id="content-wrapper">
        <iframe id="content" name="content_frame" src="0-CHM第一页.htm"></iframe>
    </div>

    <script>
        document.querySelectorAll('.toggle').forEach(t => {{
            t.addEventListener('click', (e) => {{
                e.stopPropagation();
                t.closest('.folder').classList.toggle('open');
            }});
        }});

        document.querySelectorAll('.folder-title').forEach(t => {{
            t.addEventListener('click', () => {{
                t.closest('.folder').classList.toggle('open');
            }});
        }});

        document.querySelectorAll('.doc-link').forEach(l => {{
            l.addEventListener('click', (e) => {{
                document.querySelectorAll('.doc-link').forEach(link => link.classList.remove('active'));
                l.classList.add('active');
                
                let folder = l.closest('.folder');
                if (folder) {{
                    folder.classList.add('open');
                }}
            }});
        }});

    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✨ 紧凑模式重构完成！左侧排版已大幅缩紧！")
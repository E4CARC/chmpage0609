import os
import re

# 读取我们之前洗干净的 UTF-8 HHC 文件
hhc_file = "clean_directory.hhc"

if not os.path.exists(hhc_file):
    print(f"❌ 找不到 {hhc_file}，请确保前一步清洗脚本已成功运行！")
    exit()

with open(hhc_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

sidebar_content = "* **艾伯伦5E不全书**\n"

# 用来追踪当前的嵌套深度（通过计算 UL 和 /UL 出现的次数）
current_depth = 1

# 正则表达式：用来抓取 param 里的 Name 和 Local 值
name_re = re.compile(r'<param\s+name="Name"\s+value="([^"]+)"', re.IGNORECASE)
local_re = re.compile(r'<param\s+name="Local"\s+value="([^"]+)"', re.IGNORECASE)

# 临时存放当前正在解析的 OBJECT 块的信息
in_object = False
current_name = ""
current_local = ""

print("正在使用底层扫描模式重建目录树...")

for line in lines:
    # 1. 遇到 <UL> 层级加 1，遇到 </UL> 层级减 1
    if "<UL" in line.upper():
        current_depth += 1
        continue
    if "</UL" in line.upper():
        current_depth = max(1, current_depth - 1)
        continue
    
    # 2. 标记进入了 OBJECT 块
    if "<OBJECT" in line.upper():
        in_object = True
        current_name = ""
        current_local = ""
        continue
        
    # 3. 在 OBJECT 块内提取数据
    if in_object:
        name_match = name_re.search(line)
        if name_match:
            current_name = name_match.group(1)
        
        local_match = local_re.search(line)
        if local_match:
            current_local = local_match.group(1)
            
    # 4. 离开 OBJECT 块，开始写入数据
    if "</OBJECT" in line.upper() and in_object:
        in_object = False
        if current_name:
            # 计算缩进空格（Docsify 标准：每级多 2 个空格）
            indent = "  " * current_depth
            
            if current_local:
                # 提取纯文件名，去掉可能存在的路径前缀
                import urllib.parse
                clean_path = urllib.parse.unquote(current_local)
                clean_path = os.path.basename(clean_path)
                # 补全可能缺失的后缀
                if not clean_path.endswith(('.html', '.htm', '.png', '.jpg')) and clean_path:
                    clean_path += '.html'
                    
                sidebar_content += f"{indent}* [{current_name}]({clean_path})\n"
            else:
                # 没有路径的虚节点（纯章节大标题）
                sidebar_content += f"{indent}* **{current_name}**\n"

# 写入侧边栏文件
with open('_sidebar.md', 'w', encoding='utf-8') as f:
    f.write(sidebar_content)

print("✨ 强力重建成功！请用记事本重新检查 '_sidebar.md' 里的行数是否变多了！")
import os
import sys
import re
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# # 正则表达式匹配样式属性
# style_pattern = re.compile(
#     r"top:\s*(?P<top>[\d.]+%);\s*"
#     r"left:\s*(?P<left>[\d.]+%);\s*"
#     r"width:\s*(?P<width>[\d.]+px);\s*"
#     r"height:\s*(?P<height>[\d.]+px);",
#     re.IGNORECASE
# )

def parse_style(style_str):
    styles = {}
    for prop in style_str.split(';'):
        if ':' in prop:
            key, value = prop.split(':', 1)
            styles[key.strip()] = value.strip()
    return styles

def extract_numberxy(name):
    numbers = re.findall(r'\d+', name)  # 提取所有连续数字
    num = 0
    if numbers:
        num = int(numbers[0])
    return num

def extract_comments_from_xhtml(xhtml_content, result):
    soup = BeautifulSoup(xhtml_content, 'lxml')
    for div in soup.find_all('div'):
        # 提取 class
        classes = div.get('class', [])
        onclick = div.get('onclick', '')
        elem_name = ""
        if "hint-zone" in classes:
            click_elem_pattern = r"showHint\('([^']*)'\)"
            match = re.match(click_elem_pattern, onclick)
            if match:
                elem_name = f"hint_{match.group(1)}"
        if "audio-zone" in classes:    
            click_elem_pattern = r"playAudio\('([^']*)'\)"
            match = re.match(click_elem_pattern, onclick)
            if match:
                elem_name = f"hint_{match.group(1)}"
        if "hint-txt" in classes:
            div_id = div.get('id', '')
            if len(div_id) > 0:
                elem_name = f"elem_{div_id}"
                text = div.get_text(strip=True)
                if text:
                    result[f"{elem_name}:text"] = text
            
        if len(elem_name) > 0:
            # 提取并解析 style
            style = div.get('style', '')
            # style_match = style_pattern.search(style)
            style_dict = parse_style(style)  # 调用解析函数
            x = extract_numberxy(style_dict.get('left', '0%'))
            y = extract_numberxy(style_dict.get('top', '0%'))
            width = style_dict.get('width', 0)
            height = style_dict.get('height', 0)
            
            result[elem_name] = [x, y, width, height]
    for img in soup.find_all('img'):
        img_id = img.get('id', '')
        clz = img.get('class', [])
        #print(f"img {img} - {img_id} classes: {clz}")
        if "hint-img" in clz:
            elem_name = f"elem_{img_id}"
            style = img.get('style', '')
            style_dict = parse_style(style)
            x = extract_numberxy(style_dict.get('left', '0%'))
            y = extract_numberxy(style_dict.get('top', '0%'))
            width = style_dict.get('width', 0)
            height = style_dict.get('height', 0)

            result[elem_name] = [x, y, width, height]
    for audio in soup.find_all('audio'):
        audio_id = audio.get('id', '')
        if audio_id:
            elem_name = f"elem_{audio_id}"
            # 这里假设音频没有样式属性，直接使用默认位置
            x, y, width, height = 0, 0, 0, 0

            result[elem_name] = [x, y, width, height]

# 示例用法
html_c ='''
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#" lang="sl" xml:lang="sl">
  <head>
    <title>第8页</title>
  </head>
  <body><link rel="stylesheet" type="text/css" href="styles/style.css"/>
  <script src="scripts/myscript.js" type="text/javascript"/>
  <div class="container">
	<img alt="img_0008" src="images/img_0008.jpg" class="bg"/>

    <!-- Active Zone -->
    <!-- 可点击区域1：显示提示图 -->
    <!-- <div class="hint-zone" style="top: 30%; left: 40%; width: 100px; height: 100px; " onclick="showHint('hintText')"></div> -->
    <!-- 可点击区域2：播放音频 -->
    <!-- <div class="audio-zone" style="top: 60%; left: 20%;" onclick="playAudio('aud01')"></div> -->
    
    <!-- <hint_p8img_0102: 1% 80% w0 h0> -->
    <div class="hint-zone" style="top: 90%; left: 1%; width: 100px; height: 120%; " onclick="showHint('p8img_0102')"/>

    <!-- <hint_p8aud_0001: 1% 15% w0 h0> -->
    <div class="audio-zone" style="top: 32%; left: 1%; " onclick="playAudio('p8aud_0001')"/>

    <!-- <hint_p8aud_0002: 1% 25% w0 h0> -->
    <div class="audio-zone" style="top: 69%; left: 1%; " onclick="playAudio('p8aud_0002')"/>


    <!-- Active elements -->
    <!-- 隐藏的小图 -->
    <!-- <img id="hint" src="../Images/01.jpg" class="hint-img" style="display: block; width:200px"/> -->
    <!-- 音频 -->
    <!-- <audio id="aud01"><source src="../Audio/01.mp3" type="audio/mpeg"/></audio> -->
    
    <!-- <elem_p8img_0102: 45% 80% w0 h0> -->
    <img id="p8img_0102" src="images/img_0102.jpg" class="hint-img" style="display: block; top: 80%; left: 45%; "/>

    <!-- <elem_p8txt_0102: 20% 10% w0 h0> -->
    <!-- <elem_p8txt_0102:text 中国123> -->
    <div id="p8txt_0102" class="hint-txt" style="top: 10%; left: 20%; display: block">中国123</div>

    <!-- <elem_p8aud_0001: 45% 15% w0 h0> -->
    <audio id="p8aud_0001"><source src="audio/aud_0001.mp3" type="audio/mpeg"/></audio>

    <!-- <elem_p8aud_0002: 45% 25% w0 h0> -->
    <audio id="p8aud_0002"><source src="audio/aud_0002.mp3" type="audio/mpeg"/></audio>


  </div>
</body>
</html>
'''

if __name__ == "__main__":
    info_dict = {}
    
    # test code for simple HTML content
    # extract_comments_from_xhtml(html_c, info_dict)
    # for key, value in info_dict.items():
    #     print(f"  {key}: {value}")

    if len(sys.argv) > 1:
        book_name = sys.argv[1]
    else:
        book_name = input("Enter the EPUB book name (e.g., 'your_book.epub'): ").strip()

    if not book_name or os.path.exists(book_name) is False:
        print(f"File '{book_name}' does not exist. Please check the file path.")
        exit(1)

    book = epub.read_epub(book_name)
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:  # 只处理xhtml文件
            print(f"File: {item.get_name()}")
            content = item.get_content().decode('utf-8')
            extract_comments_from_xhtml(content, info_dict)
    
    print(info_dict)
    with open("geometry.json", 'w', encoding='utf-8') as f:
        json.dump(info_dict, f, ensure_ascii=False, indent=4)
    print("Geometry information has been saved to 'geometry.json'.")
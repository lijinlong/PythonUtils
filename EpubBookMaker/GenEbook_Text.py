import os
import json
import re
from natsort import natsorted
from ebooklib import epub

def GenEbook_Info(name, title):
    book_info = {
        "name": name if name else "book",
        "lang": "en",
        "author": "ljl",
        "title": title if title else "My Ebook",

        "cover": "cover.jpg",
        "image_folder": "images", # 如果设置扫描文件夹下所有图片添加到images
        "images":[
            # (mapping_name, img_file), # mapping_name 生成页面文件使用, img_file文件路径
        ],
        "audio_folder": "audio", # 如果设置扫描文件夹下所有音频添加到audios
        "audios":[
            # (mapping_name, audio_file), # mapping_name 生成页面文件使用, audio_file文件路径
        ],
        "toc" : [
            # 目录
            #(页面文件, 标题)
            #(pg_from_rel(5), "Uvod - 斯语简介"),

        ],

        # "style": '''''' # css_style string
        # "script": '''''' # js_content string

        #"gen_page_content_func": gen_active_html, # 可选，生成页面内容的函数，默认gen_simple_html，函数签名为 func(pageIdx, title, active_items)
    }
    return book_info


# 样式
default_style = '''
.label_clickable {
    color: black;
    background-color: black;
    text-decoration: underline;
    cursor: pointer;
}

nav#landmarks {{
    display:none;
}}

nav#page-list {{
    display:none;
}}

ol {{
    list-style-type: none;
}}
'''

default_js_content = '''
function showHint(hint) {
function ShowElement(elem) {
    elem.style.color = 'red';
    elem.style.backgroundColor = 'white';
}

function HideElement(elem) {
    elem.style.color = 'black';
    elem.style.backgroundColor = 'black';
}

function Toggle(id) {
    const elem = document.getElementById(id);
    if (elem.style.color == elem.style.backgroundColor) {
    ShowElement(elem);
    } else {
    HideElement(elem);
    }
}

function ShowElementsInList(IdList) {
    IdList.forEach(id => {
    const elem = document.getElementById(id);
    ShowElement(elem);
    });
}

function HideElementsInList(IdList) {
    IdList.forEach(id => {
    const elem = document.getElementById(id);
    HideElement(elem);
    });
}

function ShowAll(parentId) {
    if (parentId) {
    const parent = document.getElementById(parentId);
    const elements = parent.querySelectorAll('.label_clickable');
    elements.forEach((elem, index) => {
        ShowElement(elem);
    });
    }
    else {
    const elements = document.querySelectorAll('.label_clickable');
    elements.forEach((elem, index) => {
        ShowElement(elem);
    });
    }
}

function HideAll(parentId) {
    if (parentId) {
    const parent = document.getElementById(parentId);
    const elements = parent.querySelectorAll('.label_clickable');
    elements.forEach((elem, index) => {
        HideElement(elem);
    });
    }
    else {
    const elements = document.querySelectorAll('.label_clickable');
    elements.forEach((elem, index) => {
        HideElement(elem);
    });
    }
}

'''

def extract_number(filename):
    numbers = re.findall(r'\d+', filename)  # 提取所有连续数字
    num = 0
    if numbers:
        num = int(numbers[-1])
    #print(f"## {filename} -> {num} {numbers[0]}")
    return num


def GenEbook(book_info):
    # 创建一本书
    book = epub.EpubBook()
    book_name = f'{book_info["name"]}.epub'

    # 设置书籍元数据
    book.set_identifier(book_info["name"])
    book.set_title(book_info["title"] or book_info["name"])
    book.set_language(book_info["lang"])
    book.add_author(book_info["author"])

    # 添加封面
    cover = book_info["cover"]
    if os.path.exists(cover):
        with open(cover, 'rb') as f:
            book.set_cover(cover, f.read())

    # 添加样式表
    style_content = book_info.get("style", default_style)
    nav_css = epub.EpubItem(uid="style_nav", file_name="styles/style.css", media_type="text/css", content=style_content)
    book.add_item(nav_css)

    # 添加JavaScript文件
    js_content = book_info.get("script", default_js_content)
    js_item = epub.EpubItem(
        uid="myscript",
        file_name="scripts/myscript.js",
        media_type="application/javascript",
        content=js_content
    )
    book.add_item(js_item)

    # 添加音频
    audio_folder = book_info["audio_folder"]
    audio_files = book_info.get("audios", [])
    if os.path.exists(audio_folder):
        audios = natsorted(os.listdir(audio_folder))
        for aud_file in audios:
            if aud_file.lower().endswith(('.mp3', '.mp4', '.aac')):
                aud_path = os.path.join(audio_folder, aud_file)
                audio_files.append((aud_file, aud_path))

    for mapping_name, aud_file in audio_files:
        with open(aud_file, 'rb') as f:
             aud_data = f.read()
        aud_path_in_book = f'audio/{mapping_name}'
        print(f"Adding audio {aud_file} -> {aud_path_in_book}")
        book.add_item(epub.EpubItem(uid=mapping_name, file_name=aud_path_in_book, media_type='audio/mpeg', content=aud_data))

    # 添加图片
    image_folder = book_info["image_folder"]
    image_files = book_info.get("images", [])
    if os.path.exists(image_folder):
        images = natsorted(os.listdir(image_folder))
        for img_file in images:
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(image_folder, img_file)
                image_files.append((img_file, img_path))

    for mapping_name, img_file in image_files:            
        with open(img_file, 'rb') as f:
            img_data = f.read()
        img_path_in_book = f'images/{mapping_name}'
        print(f"Adding image {img_file} -> {img_path_in_book}")
        book.add_item(epub.EpubItem(uid=mapping_name, file_name=img_path_in_book, media_type='image/jpeg', content=img_data))


    epub_pages = []
    pages = []
    if "gen_page_content_func" in book_info and callable(book_info["gen_page_content_func"]):
        pages = book_info["gen_page_content_func"]()

    for title, content in pages:
        page_name = title
        print(f"Adding page {page_name}")
        page = epub.EpubHtml(title=title, file_name=f'{page_name}.xhtml', lang=book_info["lang"])
        page.content = content
        book.add_item(page)
        epub_pages.append(page)

    # 4. 构建目录（TOC）、
    toc = []
    page_toc = book_info.get("toc", [])
    for idx, (page_name, title) in enumerate(page_toc):
        toc.append(epub.Link(f'{page_name}.xhtml', title, f'pg_{page_name}'))
        print(f"Adding TOC entry {idx}: '{title}' -> {page_name}.xhtml")
    book.toc = toc

    # 5. 设置导航
    book.add_item(epub.EpubNcx())  # EPUB NCX 导航文件（目录）
    book.add_item(epub.EpubNav())  # HTML Nav 文件（EPUB3 必需）

    # 6. 设置 spine（阅读顺序）
    book.spine = ['cover', 'nav'] + epub_pages

    # 7. 输出 EPUB 文件
    epub.write_epub(book_name, book, {})
    print(f"\nEPUB file created successfully: {book_name}")

# 添加HTML页面
html_simple_temp = '''
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{title}</title>
</head>
<body>
    <link rel="stylesheet" type="text/css" href="styles/style.css" />
    <audio controls><source src="{audio_path}" type="audio/mpeg" />你的浏览器不支持音频播放</audio>
    <img alt="{img_id}" src="{img_path}" class='bg'/>
</body>
</html>
'''
def simple_gen_page_content(title, img, audio):
    html_content = html_simple_temp.format(title=title, img_id=title, img_path=f"images/{img}", audio_path=f"audio/{audio}")
    return html_content

def gen_simple_pages():
    pages = []

    pages_setting = [
        ("P1", "a116.png", "SBZ-1a-U-1.mp3"),
        ("P2", "a117.png", "SBZ-1a-U-2.mp3"),
        ("P3", "a119.png", "SBZ-1a-U-53.mp3")
    ]
    for title, img, audio in pages_setting:
        html = simple_gen_page_content(title, img, audio)
        pages.append((title, html))
    
    return pages


if __name__ == "__main__":
    book_info = GenEbook_Info("mybook", "My First Book")
    book_info["audio_folder"] = "audio"
    book_info["image_folder"] = "img"
    book_info["images"] = [("a119.png", "a119.png")]
    book_info["audios"] = [("SBZ-1a-U-53.mp3", "SBZ-1a-U-53.mp3")]

    book_info["gen_page_content_func"] = gen_simple_pages
    book_info["toc"] = [
        ("P1", "AAA"),
        ("P2", "BBB"),
        ("P3", "CCC")
    ]
    
    GenEbook(book_info)

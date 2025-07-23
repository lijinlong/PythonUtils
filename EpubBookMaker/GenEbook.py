import os
import json
import re
from ebooklib import epub

def get_aud_id(id):
    return f"aud_{id:0>4}"

def get_img_id(id):
    return f"img_{id:0>4}"

def get_vid_id(id):
    return f"vid_{id:0>4}"

# DEBUG_AREA = True
DEBUG_AREA = False

book_info = {
    "name": "Slovenscina_Ekspres_1",
    "lang": "sl",
    "author": "Tanja Jerman, Staša Pisek, Anja Strajner",
    "title": "1 Slovenscina Ekspres",

    "cover": "cover.jpg",
    "image_folder": "img",
    "audio_folder": "audio",
    "page_num": 81, #fisst pageis 1
    "page_fmt": "Page_{:03d}",
    "active_pages": {
        # 页码 : [提示图get_img_id(图片编号), 音频get_aud_id(音频编号), 提示文字txt标识, ...]
        7 : [ get_img_id(102) ],
        8 : [ get_img_id(102), get_aud_id(1), get_aud_id(2) ],
        9 : [ get_img_id(102) ],
        10: [ get_img_id(113) ],
        11: [ get_img_id(113), get_aud_id(3)],
        12: [ get_img_id(113), get_aud_id(4) ],
        13: [ get_img_id(113) ],
        14: [ get_img_id(123), get_aud_id(5) ],
        15: [ get_img_id(123) ],
        16: [ get_img_id(129), get_aud_id(6), get_aud_id(7) ],
        17: [ get_img_id(131) ],
        18: [ get_img_id(131) ],
        19: [ get_img_id(131) ],
        21: [ get_img_id(201) ],
        22: [ get_img_id(201), get_aud_id(8), get_aud_id(9) ],
        23: [ get_img_id(201), get_aud_id(10) ],
        24: [ get_img_id(209) ],
        25: [ get_img_id(209), get_aud_id(11) ],
        26: [ get_img_id(215) ],
        27: [ get_img_id(218), get_aud_id(12), get_aud_id(13) ],
        28: [ get_img_id(219), get_aud_id(14) ],
        29: [ get_img_id(219), get_aud_id(15) ],
        31: [ get_img_id(301) ],
        32: [ get_img_id(301) ],
        33: [ get_img_id(301), get_aud_id(16) ],
        35: [ get_img_id(311), get_aud_id(17) ],
        36: [ get_img_id(311), get_aud_id(18) ],
        37: [ get_img_id(317), get_aud_id(19) ],
        38: [ get_img_id(321), get_aud_id(20) ],
        40: [ get_img_id(401) ],
        41: [ get_img_id(401), get_aud_id(21) ],
        42: [ get_img_id(401), get_aud_id(22), get_aud_id(23) ],
        43: [ get_img_id(411) ],
        44: [ get_img_id(411), get_aud_id(24) ],
        45: [ get_img_id(418) ],
        46: [ get_img_id(418), get_aud_id(25) ],
        47: [ get_img_id(418), get_aud_id(26) ],
        50: [ get_img_id(501) ],
        51: [ get_img_id(501), get_aud_id(27) ],
        52: [ get_img_id(501) ],
        53: [ get_img_id(501) ],
        54: [ get_img_id(509), get_aud_id(28), get_aud_id(29) ],
        55: [ get_img_id(509), get_aud_id(30) ],
        56: [ get_img_id(509), get_aud_id(31) ],
        58: [ get_img_id(601), get_aud_id(32) ],
        59: [ get_img_id(601), get_aud_id(33) ],
        60: [ get_img_id(601) ],
        61: [ get_img_id(601) ],
        62: [ get_img_id(611), get_aud_id(34), get_aud_id(35) ],
        63: [ get_img_id(611), get_aud_id(36) ],
        64: [ get_img_id(611) ],
        65: [ get_img_id(611), get_aud_id(37) ],
        72: [ get_aud_id(i) for i in range(1, 10) ],
        73: [ get_aud_id(i) for i in range(10, 20) ],
        74: [ get_aud_id(i) for i in range(19, 29) ],
        75: [ get_aud_id(i) for i in range(29, 38) ],
    },
    "toc" : [
        #(页码, 标题)
        (5, "Uvod/Introduction - Introduction - 简介"),
        (7, "1. enota: Dober dan - Greeting - 单元 1：打招呼"),
        (21, "2. enota: Družina in prijateljin - Unit 2: Family and friends - 单元 2：家人和朋友"),
        (31, "3. enota: Hiša - Unit 3: House - 单元 3：房子"),
        (40, "4. enota: Moj dan - Unit 4: My day - 单元 4：我的一天"),
        (50, "5. enota: Hrana in pijača - Unit 5: Food and drink - 简介"),
        (58, "6. enota: Mesto - Unit 6: City - 单元 6：城市"),
        (68, "Slovnične preglednice-skloni - Grammar charts-inflections - 语法表-词形变化"),
        (69, "Slovnične preglednice - glagoli -  Grammar charts-verbs - 语法表-动词"),
        (70, "Seznam pogostih glagolov - List of common verbs - 常用动词列表"),
        (72, "Zapis govorjenih besedil - Transcription of spoken texts - 听力文本"),
        (76, "Rešitve - Solutions - 答案"),
        (79, "Pregledno kazalo - Index - 索引"),
    ]
}

def get_page_name(pageIdx):
    return book_info["page_fmt"].format(pageIdx)

# 样式
style = '''
.container {{
    position: relative;
    width: 100%;
    max-width: 600px;
    margin: auto;
}}

.bg {{
    width: 100%;
    display: block;
}}

.hint-zone {{
    position: absolute;
    width: 64px;
    height: 64px;
    cursor: pointer;
    /* 可视化调试用：可设置 border */
    background-color: rgba(255,0,0,0.2);
    border: 1px solid red;
}}

.audio-zone {{
    position: absolute;
    width: 64px;
    height: 64px;
    cursor: pointer;
    /* 可视化调试用：可设置 border */
    background-color: rgba(0,255,0,0.2);
    border: 1px solid green;
}}

.hint-img {{
    position: absolute;
    display: {debug_area}; /* 默认隐藏 */
    top: 10%;
    left: 10%;
    width: 50%;
    /* 可视化调试用：可设置 border */
    border: 1px solid blue;
}}

.hint-txt {{
    position: absolute;
    display: {debug_area}; /* 默认隐藏 */
    /* 可视化调试用：可设置 border */
    border: 1px solid blue;
}}

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

js_content = '''
function showHint(hint) {
	var img = document.getElementById(hint);
	if (img.style.display == "none")
		img.style.display = "block";
    else
		img.style.display = "none";
}

function playAudio(audio) {
	var audio = document.getElementById(audio);
    //audio.play();
    if (audio.paused){
        audio.play();
    } else{
        audio.pause();
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
with open(cover, 'rb') as f:
    book.set_cover(cover, f.read())

# 添加样式表
debugStr = 'block' if DEBUG_AREA else 'none'
style_content = style.format(debug_area=debugStr)
nav_css = epub.EpubItem(uid="style_nav", file_name="styles/style.css", media_type="text/css", content=style_content)
book.add_item(nav_css)

# 添加JavaScript文件
js_item = epub.EpubItem(
    uid="myscript",
    file_name="scripts/myscript.js",
    media_type="application/javascript",
    content=js_content
)
book.add_item(js_item)

# 添加音频
audio_folder = book_info["audio_folder"]
audios = sorted(os.listdir(audio_folder))
audio_map = {}
print(f"\nFound {len(audios)} audios in {audio_folder}.")
for i, aud_file in enumerate(audios):
    if aud_file.lower().endswith(('.mp3', '.mp4', '.aac')):
        aud_path = os.path.join(audio_folder, aud_file)
        with open(aud_path, 'rb') as f:
            aud_data = f.read()
        file, ext = os.path.splitext(aud_file)
        aud_id = get_aud_id(extract_number(file))
        aud_path_in_book = f'audio/{aud_id}{ext}'
        print(f"Adding audio {aud_file} -> {aud_path_in_book}")
        book.add_item(epub.EpubItem(uid=aud_id, file_name=aud_path_in_book, media_type='audio/mpeg', content=aud_data))
        audio_map[aud_id] = aud_path_in_book

# 添加图片
image_folder = book_info["image_folder"]
images = sorted(os.listdir(image_folder))
image_map = {}
print(f"\nFound {len(images)} images in {image_folder}.")
for i, img_file in enumerate(images):
    if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(image_folder, img_file)
        with open(img_path, 'rb') as f:
            img_data = f.read()
        file, ext = os.path.splitext(img_file)
        img_id = get_img_id(extract_number(file))
        img_path_in_book = f'images/{img_id}{ext}'
        print(f"Adding image {img_file} -> {img_path_in_book}")
        book.add_item(epub.EpubItem(uid=img_id, file_name=img_path_in_book, media_type='image/jpeg', content=img_data))
        image_map[img_id] = img_path_in_book

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
    <img alt="{img_id}" src="{img_path}" class='bg'/>
</body>
</html>
'''

def gen_simple_html(pageIdx, title):
    img_id = get_img_id(pageIdx)
    img_path = image_map[img_id]
    html_content = html_simple_temp.format(title=title, img_id=img_id, img_path=img_path)
    return html_content

html_action_temp = '''
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{title}</title>
</head>
<body>
  <link rel="stylesheet" type="text/css" href="styles/style.css"/>
  <script src="scripts/myscript.js" type="text/javascript"></script>
  <div class="container">
	<img alt="{img_id}" src="{img_path}" class="bg"/>

    <!-- Active Zone -->
    <!-- 可点击区域1：显示提示图 -->
    <!-- <div class="hint-zone" style="top: 30%; left: 40%; width: 100px; height: 100px; " onclick="showHint('hintText')"></div> -->
    <!-- 可点击区域2：播放音频 -->
    <!-- <div class="audio-zone" style="top: 60%; left: 20%;" onclick="playAudio('aud01')"></div> -->
    {Actions}

    <!-- Active elements -->
    <!-- 隐藏的小图 -->
    <!-- <img id="hint" src="../Images/01.jpg" class="hint-img" style="display: block; width:200px"/> -->
    <!-- 音频 -->
    <!-- <audio id="aud01"><source src="../Audio/01.mp3" type="audio/mpeg"/></audio> -->
    {HiddenElements}

  </div>
</body>
</html>
'''

action_hint = '''
    <!-- <hint_{elem}: {x}% {y}% w{w} h{h}> -->
    <div class="hint-zone" style="top: {y}%; left: {x}%; {ext}" onclick="showHint('{elem}')"></div>
'''
action_audio = '''
    <!-- <hint_{elem}: {x}% {y}% w{w} h{h}> -->
    <div class="audio-zone" style="top: {y}%; left: {x}%; {ext}" onclick="playAudio('{elem}')"></div>
'''
elem_img = '''
    <!-- <elem_{elem}: {x}% {y}% w{w} h{h}> -->
    <img id="{elem}" src="{img_path}" class="hint-img" style="top: {y}%; left: {x}%; {ext}"/>
'''
elem_text = '''
    <!-- <elem_{elem}: {x}% {y}% w{w} h{h}> -->
    <!-- <elem_{elem}:text {text}> -->
    <div id="{elem}" class="hint-txt" style="top: {y}%; left: {x}%; {ext}">{text}</div>
'''
elem_audio = '''
    <!-- <elem_{elem}: {x}% {y}% w{w} h{h}> -->
    <audio id="{elem}"><source src="{aud_path}" type="audio/mpeg"/></audio>
'''

geometry_file = "geometry.json"
geometry = {}

if os.path.exists(geometry_file):
    with open(geometry_file, 'r', encoding='utf-8') as f:
        geometry = json.load(f)
else:
    pgs = book_info["active_pages"]
    for pg, conts in pgs.items():
        for i, el in enumerate(conts):
            elname = f'p{pg}{el}'
            hint_item = f"hint_{elname}"
            el_item = f"elem_{elname}"
            x,y,w,h = 1, 5+10*i, 0, 0
            if el.startswith("img_"):
                y = 90
            geometry[hint_item] = [x, y, w, h]
            x = 45
            if el.startswith("aud_"):
                x, y, w, h = 0, 0, 0, 0
            geometry[el_item] = [x, y, w, h]
            if el.startswith("txt"):
                geometry[f"{el_item}:text"] = "Simple text"
    print(f"Init geometry: {json.dumps(geometry, indent=4)}")

def get_hint_area(elem):
    n = f"hint_{elem}"
    x,y,w,h=1,10,0,0
    if n in geometry:
        x,y,w,h = geometry[n]
    return x,y,w,h

def get_element_area(elem):
    n = f"elem_{elem}"
    x,y,w,h=45,80,0,0
    if n in geometry:
        x,y,w,h = geometry[n]
    return x,y,w,h

def get_txt_content(elem):
    n = f"elem_{elem}:text"
    c = "###"
    if n in geometry:
        c = geometry[n]
    return c

def extends_width_height(w,h):
    str = ""
    if isinstance(w, int):
        if w > 0:
            str = f"width: {w}px;"
    elif isinstance(w, str):
        str = f"width: {w};"
    if isinstance(h, int):
        if h > 0:
            str += f" height: {h}px;"
    elif isinstance(h, str):
        str += f" height: {h};"
    return str

def gen_hint_content(temp, elem):
    x,y,w,h = get_hint_area(elem)
    ext = extends_width_height(w, h)
    return temp.format(elem=elem, x=x,y=y,w=w,h=h, ext=ext)

def gen_elem_content(temp, elem, extra):
    x,y,w,h = get_element_area(elem)
    ext = extends_width_height(w, h)
    return temp.format(elem=elem, x=x,y=y,w=w,h=h, ext=ext, img_path=extra, aud_path=extra, text=extra)

def gen_active_html(pageIdx, title, active_content):
    img_id = get_img_id(pageIdx)
    img_path = image_map[img_id]
    Actions = ""
    HiddenElements = ""
    for elem in active_content:
        elname = f'p{pageIdx}{elem}'
        if elem.startswith("img_"):
            Actions = Actions + gen_hint_content(action_hint, elname)
            HiddenElements = HiddenElements + gen_elem_content(elem_img, elname, image_map[elem])
        elif elem.startswith("aud_"):
            Actions = Actions + gen_hint_content(action_audio, elname)
            HiddenElements = HiddenElements + gen_elem_content(elem_audio, elname, audio_map[elem])
        elif elem.startswith("txt"):
            Actions = Actions + gen_hint_content(action_hint, elname)
            HiddenElements = HiddenElements + gen_elem_content(elem_text, elname, get_txt_content(elname))
    
    html_content = html_action_temp.format(title=title, img_id=img_id, img_path=img_path, Actions=Actions, HiddenElements=HiddenElements)
    return html_content

pages = []
# 生成xhtml页面
for pageIdx in range(1, (book_info["page_num"]+1)):
    page_name = get_page_name(pageIdx)
    title = f'第{pageIdx}页'
    print(f"Adding page {pageIdx} -> {page_name}")
    if pageIdx in book_info["active_pages"]:
        html_content = gen_active_html(pageIdx, title, book_info["active_pages"][pageIdx])
    else:
        html_content = gen_simple_html(pageIdx, title)
    # print(f"{pageIdx} Content {html_content}")
    page = epub.EpubHtml(title=title, file_name=f'{page_name}.xhtml', lang=book_info["lang"])
    page.content = html_content
    book.add_item(page)
    pages.append(page)


# 4. 构建目录（TOC）、
toc = []
for idx, (pageIdx, title) in enumerate(book_info["toc"]):
    page_name = get_page_name(pageIdx)
    toc.append(epub.Link(f'{page_name}.xhtml', title, f'pg_{page_name}'))
    print(f"Adding TOC entry {idx}: '{title}' -> {page_name}.xhtml")
book.toc = toc

# 5. 设置导航
book.add_item(epub.EpubNcx())  # EPUB NCX 导航文件（目录）
book.add_item(epub.EpubNav())  # HTML Nav 文件（EPUB3 必需）

# 6. 设置 spine（阅读顺序）
book.spine = ['cover', 'nav'] + pages

# 7. 输出 EPUB 文件
epub.write_epub(book_name, book, {})
print(f"\nEPUB file created successfully: {book_name}")

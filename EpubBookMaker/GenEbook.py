import os
import json
import re
from natsort import natsorted
from ebooklib import epub

def get_aud_id(id):
    return f"aud_{id:0>4}"

def get_img_id(id):
    return f"img_{id:0>4}"

def get_vid_id(id):
    return f"vid_{id:0>4}"

# 映射实体书页码到电子书页码,每本书映射都不同，需要修改
real_page_mapping_rule = [
    #(m, n), # if real page number is less than m then will add n(can be negative) to get the mapping page number
    (103, 2), # 实体页码1-103 -> + 2 (3-105)
    (149, 1), # 实体页码105-149 -> + 1 (106-150)
    (154, 0), # 实体页码151-154 -> + 0 (151-154)
]

def pg_from_rel(pg):
    for m, n in real_page_mapping_rule:
        if pg <= m:
            return pg + n
    return pg  # 如果没有匹配，返回原始页码

def map_rel_pg(pg):
    return get_img_id(pg_from_rel(pg))

# 音频页码映射，实体书对应页码有音频文件，会在对应页码添加相应音频文件可以点击相关区域进行播放
audio_pg_map = {
    # 音频页码映射 实体书页码:[音频编号]
    #10: [1], # 音频1在实体书第10页
    #76: [ i for i in range(63, 67+1) ],
    #146: list(range(40, 60+1)) + list(range(109, 116+1)),
    
    10: [1], # 音频1在第10(+2)页
    11: [2, 3],
    137: [ i for i in range(1, 12+1) ],
}

# 如果书中有练习题，答案页码与对应练习题出现的页码，会在练习题页码添加答案页码的图片方便在练习题页查看答案。也可以在book_info["book_info"]中手动添加#pg_from_rel(rel_pg) : [ get_img_id(102) ] 102为答案页部分截图
answer_map = {
    # 答案页码映射，页码为实体书页码，对应文件应+2 实体书页码: [答案在本页的练习题页码]
    #145: list(range(10, 34+1)) + list(range(106, 108+1)), #答案页145(+2)的答案对应练习页10-34和106-108
    
    145: list(range(10, 34+1)) + list(range(106, 108+1)), 
}

audio_text_pg_map = {
    # 音频文本页码映射 实体书页码:[音频编号]
    #137: [ i for i in range(1, 12+1) ], # 137页音频文本包含音频1-12

    137: [ i for i in range(1, 12+1) ],
}

extra_active_pages = {
    # 额外的活动页码映射，页码为实体书页码: [提示图get_img_id(图片编号), 音频get_aud_id(音频编号), 提示文字txt标识, ...]
    #62: [ (get_img_id(543), "hint-zone-audiotext", "hint-img-audiotext") ], # 62 - 43

    62: [ (get_img_id(543), "hint-zone-audiotext", "hint-img-audiotext") ], # 62 - 43
}

# DEBUG_AREA = True
DEBUG_AREA = False

book_info = {
    "name": "book",
    "lang": "en",
    "author": "ljl",
    "title": "My Ebook",

    "cover": "cover.jpg",
    "image_folder": "images",
    "audio_folder": "audio",
    "page_num": 154, #first page is 1
    "page_fmt": "Page_{:03d}",
    "active_pages": {
        # 页码(电子书页码) : [提示图get_img_id(图片编号), 音频get_aud_id(音频编号), 提示文字txt标识, ...]
        #8 : [ get_img_id(102), get_aud_id(1), get_aud_id(2), (get_img_id(105), "hint-zone-audiotext", "hint-img-audiotext") ],
        #pg_from_rel(n): [ map_rel_pg(102), get_aud_id(audid) ],
    },
    "toc" : [
        # 目录
        #(页码, 标题)
        #(pg_from_rel(5), "Uvod - 斯语简介"),

        (pg_from_rel(5), "Uvod - 斯语简介"),
    ]
}

def element_in_active_page(elem, page_content):
    # 检查元素是否在活动页中
    for item in page_content:
        if isinstance(item, str):
            if elem.lower() == item.lower():
                return True
        elif isinstance(item, tuple):
            if elem.lower() == item[0].lower():
                return True
    return False

def get_aud_text_rel_pg(id):
    for pg, auds in audio_text_pg_map.items():
        if id in auds:
            return pg
    return None

for pg, exs in answer_map.items():
    # 将答案页码映射到电子书相应页码
    ans_pg = map_rel_pg(pg)
    for ex in exs:
        ex_pg = pg_from_rel(ex)
        if ex_pg not in book_info["active_pages"]:
            book_info["active_pages"][ex_pg] = [ ans_pg ]
        else:
            book_info["active_pages"][ex_pg].extend([ ans_pg ])

audio_text_pg_start = min(audio_text_pg_map.keys()) if len(audio_text_pg_map) > 0 else 0
for pg, auds in audio_pg_map.items():
    # 将音频页码映射到电子书页码
    aud_pg = pg_from_rel(pg)
    if aud_pg not in book_info["active_pages"]:
        book_info["active_pages"][aud_pg] = [ get_aud_id(aud) for aud in auds ]
    else:
        book_info["active_pages"][aud_pg].extend([ get_aud_id(aud) for aud in auds ])  # 确保音频页码列表存在
    
    # 仅在音频文本页之前音频出现的页码添加音频文本所在页
    if pg < audio_text_pg_start:
        for aud in auds:
            rel_audio_text_pg = get_aud_text_rel_pg(aud)
            if rel_audio_text_pg is not None:
                audio_text_pg = map_rel_pg(rel_audio_text_pg)
                if not element_in_active_page(audio_text_pg, book_info["active_pages"][aud_pg]):
                    book_info["active_pages"][aud_pg].append( (audio_text_pg, "hint-zone-audiotext", "hint-img-audiotext") )

for pg, exts in extra_active_pages.items():
    # 将额外活动页码映射到电子书页码
    ext_pg = pg_from_rel(pg)
    if ext_pg not in book_info["active_pages"]:
        book_info["active_pages"][ext_pg] = []
    for ext in exts:
        if ext not in book_info["active_pages"][ext_pg]:
            book_info["active_pages"][ext_pg].append(ext)

print("\nActive pages:")
for pg, items in book_info["active_pages"].items():
    print(f"  {pg}: {items}")

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

/*默认触发区,答案触发区*/
.hint-zone {{
    position: absolute;
    width: 64px;
    height: 64px;
    cursor: pointer;
    /* 可视化调试用：可设置 border */
    background-color: rgba(255,0,0,0.2);
    border: 1px solid red;
}}

/*音频文本触发区*/
.hint-zone-audiotext {{
    position: absolute;
    width: 64px;
    height: 64px;
    cursor: pointer;
    /* 可视化调试用：可设置 border */
    background-color: rgba(255,0,0,0.2);
    border:1px solid black;
}}

/*默认音频文件播放触发区*/
.audio-zone {{
    position: absolute;
    width: 64px;
    height: 64px;
    cursor: pointer;
    /* 可视化调试用：可设置 border */
    background-color: rgba(0,255,0,0.2);
    border: 1px solid green;
}}

/*触发显示的图片(答案)*/
.hint-img {{
    position: absolute;
    display: {debug_area}; /* 默认隐藏 */
    top: 15%;
    left: 5%;
    width: 80%;
    /* 可视化调试用：可设置 border */
    border: 1px solid blue;
}}

/*触发显示的音频文本*/
.hint-img-audiotext {{
    position: absolute;
    display: {debug_area}; /* 默认隐藏 */
    top: 20%;
    left: 10%;
    width: 80%;
    /* 可视化调试用：可设置 border */
    border: 2px solid black;
}}

/*触发显示的自定义文本*/
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
audios = natsorted(os.listdir(audio_folder))
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
images = natsorted(os.listdir(image_folder))
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

# action_hint default clz = "hint-zone"
action_hint = '''
    <!-- <hint_{elem}: {x}% {y}% w{w} h{h}> -->
    <div class="{clz}" style="top: {y}%; left: {x}%; {ext}" onclick="showHint('{elem}')"></div>
'''
# action_audio default clz = "audio-zone"
action_audio = '''
    <!-- <hint_{elem}: {x}% {y}% w{w} h{h}> -->
    <div class="{clz}" style="top: {y}%; left: {x}%; {ext}" onclick="playAudio('{elem}')"></div>
'''
# elem_img default clz = "hint-img"
elem_img = '''
    <!-- <elem_{elem}: {x}% {y}% w{w} h{h}> -->
    <img id="{elem}" src="{img_path}" class="{clz}" style="top: {y}%; left: {x}%; {ext}"/>
'''
# elem_text default clz = "hint-txt"
elem_text = '''
    <!-- <elem_{elem}: {x}% {y}% w{w} h{h}> -->
    <!-- <elem_{elem}:text {text}> -->
    <div id="{elem}" class="{clz}" style="top: {y}%; left: {x}%; {ext}">{text}</div>
'''
# elem_audio
elem_audio = '''
    <!-- <elem_{elem}: {x}% {y}% w{w} h{h}> -->
    <audio id="{elem}"><source src="{aud_path}" type="audio/mpeg"/></audio>
'''

geometry_file = "geometry.json"
geometry = {}

if os.path.exists(geometry_file):
    with open(geometry_file, 'r', encoding='utf-8') as f:
        geometry = json.load(f)
        # 初始化新添加的为保存信息
        pgs = book_info["active_pages"]
        for pg, conts in pgs.items():
            for i, item in enumerate(conts):
                el = item[0] if isinstance(item, tuple) else item
                elname = f'p{pg}{el}'
                hint_item = f"hint_{elname}"
                el_item = f"elem_{elname}"
                x,y,w,h,ext = 1, 5+10*i, 0, 0, ""
                if el.startswith("img_"):
                    x, y = 0, 10
                if hint_item not in geometry:
                    geometry[hint_item] = [x, y, w, h, ext]
                x = 5
                if el.startswith("aud_"):   
                    x, y, w, h = 0, 0, 0, 0
                if el.startswith("img_"):
                    x,y = 20, 5
                if el_item not in geometry:
                    geometry[el_item] = [x, y, w, h, ext]
                if el.startswith("txt") and  f"{el_item}:text" not in geometry:
                    geometry[f"{el_item}:text"] = "Simple text"
else:
    pgs = book_info["active_pages"]
    for pg, conts in pgs.items():
        for i, item in enumerate(conts):
            el = item[0] if isinstance(item, tuple) else item
            elname = f'p{pg}{el}'
            hint_item = f"hint_{elname}"
            el_item = f"elem_{elname}"
            x,y,w,h,ext = 1, 5+10*i, 0, 0, ""
            if el.startswith("img_"):
                x, y = 0, 0
            geometry[hint_item] = [x, y, w, h, ext]
            x = 5
            if el.startswith("aud_"):
                x, y, w, h = 0, 0, 0, 0
            if el.startswith("img_"):
                x = 15
            geometry[el_item] = [x, y, w, h, ext]
            if el.startswith("txt"):
                geometry[f"{el_item}:text"] = "Simple text"
    print(f"Init geometry: {json.dumps(geometry, indent=4)}")

def get_hint_area(elem):
    n = f"hint_{elem}"
    x,y,w,h,ext=1,10,0,0,""
    if n in geometry:
        x,y,w,h,ext = geometry[n]
    return x,y,w,h,ext

def get_element_area(elem):
    n = f"elem_{elem}"
    x,y,w,h,ext=45,80,0,0,""
    if n in geometry:
        x,y,w,h,ext = geometry[n]
    return x,y,w,h,ext

def get_txt_content(elem):
    n = f"elem_{elem}:text"
    c = "###"
    if n in geometry:
        c = geometry[n]
    return c

def extends_width_height(w,h,e):
    resstr = ""
    if isinstance(w, int):
        if w > 0:
            resstr = f"width: {w}px;"
    elif isinstance(w, str):
        resstr = f"width: {w};"

    if isinstance(h, int):
        if h > 0:
            resstr += f" height: {h}px;"
    elif isinstance(h, str):
        resstr += f" height: {h};"

    if isinstance(e, str) and len(e) > 0:
        resstr += f" {e}"
    return resstr

def gen_hint_content(temp, elem, clz="hint-zone"):
    x,y,w,h,e = get_hint_area(elem)
    ext = extends_width_height(w, h, e)
    return temp.format(elem=elem, clz=clz, x=x,y=y,w=w,h=h, ext=ext)

def gen_elem_content(temp, elem, clz, extra):
    x,y,w,h,e = get_element_area(elem)
    ext = extends_width_height(w, h, e)
    return temp.format(elem=elem, clz=clz, x=x,y=y,w=w,h=h, ext=ext, img_path=extra, aud_path=extra, text=extra)

def gen_active_html(pageIdx, title, active_content):
    img_id = get_img_id(pageIdx)
    img_path = image_map[img_id]
    Actions = ""
    HiddenElements = ""
    for item in active_content:
        elem, clz_hit, clz_el = item, None, None
        if isinstance(item, tuple):
            elem, clz_hit, clz_el = item[0], item[1], item[2]
        elname = f'p{pageIdx}{elem}'
        if elem.startswith("img_"):
            Actions = Actions + gen_hint_content(action_hint, elname, clz_hit or "hint-zone")
            HiddenElements = HiddenElements + gen_elem_content(elem_img, elname, clz_el or "hint-img", image_map[elem])
        elif elem.startswith("aud_"):
            Actions = Actions + gen_hint_content(action_audio, elname, clz_hit or "audio-zone")
            HiddenElements = HiddenElements + gen_elem_content(elem_audio, elname, clz_el, audio_map[elem])
        elif elem.startswith("txt"):
            Actions = Actions + gen_hint_content(action_hint, elname, clz_hit or "hint-zone")
            HiddenElements = HiddenElements + gen_elem_content(elem_text, elname, clz_el or "hint-txt", get_txt_content(elname))
    
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

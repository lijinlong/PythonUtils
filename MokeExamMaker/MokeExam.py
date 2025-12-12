import random
import json
import os, sys
from PIL import Image
from docx import Document
from docx.shared import Pt

class NullWalker:
    def __init__(self):
        pass

    def start(self):
        pass

    def addTitle(self, title):
        pass
        
    def addTask1Info(self, info):
        pass

    def addTask2Pics(self, pics):
        pass

    def end(self):
        pass

class PrintWakler:
    def __init__(self):
        pass

    def start(self):
        pass

    def addTitle(self, title):
        print(title)
        
    def addTask1Info(self, info):
        for item in info:
            print(f"- {item}")
        print("")

    def addTask2Pics(self, pics):
        picCnt = 1
        for pic in pics:
            print(f"- Slika: {picCnt}")
            print(f"![]({pic})")
            picCnt += 1
        print("")

    def end(self):
        pass

class MarkdownFileWalker:
    def __init__(self, file_path):
        self.file_path = file_path

    def start(self):
        self.file = open(self.file_path, "w", encoding="utf-8")

    def addTitle(self, title):
        self.file.write(title + "\n")
        
    def addTask1Info(self, info):
        for item in info:
            self.file.write(f"- {item}\n")
        self.file.write("\n")

    def addTask2Pics(self, pics):
        picCnt = 1
        for pic in pics:
            self.file.write(f"- Slika: {picCnt}\n")
            self.file.write(f"![]({pic})\n")
            picCnt += 1
        self.file.write("\n")

    def end(self):
        self.file.close()
        pass

# PDFFileWalker: 仿照MarkdownFileWalker，将任务内容渲染为PDF文件
class PDFFileWalker:
    def __init__(self, file_path):
        self.file_path = file_path
        from fpdf import FPDF
        self.FPDF = FPDF
        self.fontName = "DejaVu"
        self.fontFile = "DejaVuSans.ttf"
        self.fontFileBold = 'DejaVuSans-Bold.ttf'
        self.fontSizeBig = 14
        self.fontSize = 12
        self.cellSizeBig = 12
        self.cellSize = 10
        self.picMaxWidth = 120
        self.picMaxHeight = 96

    def start(self):
        self.pdf = self.FPDF(format="A4")
        self.pdf.set_margins(15, 20, 15)  # 左、上、右
        #self.pdf.set_auto_page_break(auto=True, margin=20)  # 底部边距
        
        self.pdf.add_font(self.fontName, '', self.fontFile, uni=True)
        self.pdf.add_font(self.fontName, 'B', self.fontFileBold, uni=True)
        self.pdf.set_font(self.fontName, size=self.fontSize)
        self.pdf.add_page()

        #self.pdf.set_font(self.fontName, size=self.fontSize)

    def addTitle(self, title):
        lines = title.splitlines()
        if lines:
            # 第一行加大字体
            self.pdf.set_font(self.fontName, 'B', size=self.fontSizeBig)
            self.pdf.cell(0, self.cellSizeBig, lines[0], ln=True)
            # 其余行用普通字体
            self.pdf.set_font(self.fontName, size=self.fontSize)
            for line in lines[1:]:
                self.pdf.cell(0, self.cellSize, line, ln=True)

    def addTask1Info(self, info):
        for item in info:
            self.pdf.cell(0, self.cellSize, f"- {item}", ln=True)

    def addTask2Pics(self, pics):
        picCnt = 1
        for pic in pics:
            # 使用加粗字体
            self.pdf.set_font(self.fontName, 'B', size=self.fontSize)
            self.pdf.cell(0, self.cellSize, f"- Slika: {picCnt}", ln=True)
            # 其余行用普通字体
            self.pdf.set_font(self.fontName, size=self.fontSize)
            if os.path.exists(pic):
                # 插入图片，宽度最大self.picWidth，高度自适应
                # self.pdf.image(pic, w=self.picWidth, keep_aspect_ratio=True)
                with Image.open(pic) as img:
                    orig_w, orig_h = img.size
                    # 假设A4纸dpi为72，1英寸=25.4mm
                    # 计算像素到mm的转换比例
                    dpi = 72
                    orig_w_mm = orig_w / dpi * 25.4
                    orig_h_mm = orig_h / dpi * 25.4
                    scale = min(self.picMaxWidth / orig_w_mm, self.picMaxHeight / orig_h_mm, 1)
                    w = orig_w_mm * scale
                    h = orig_h_mm * scale
                    self.pdf.image(pic, w=w, h=h)
            else:
                self.pdf.cell(0, self.cellSize, f"[图片不存在] {pic}", ln=True)
            self.pdf.ln(2)
            picCnt += 1

    def end(self):
        self.pdf.output(self.file_path)
        #print(f"PDF已生成: {self.file_path}")

class DocxFileWalker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.fontName = "Arial Unicode MS"
        self.fontSizeBig = 16
        self.fontSize = 12
        self.picMaxWidth = 120
        self.picMaxHeight = 96

    def start(self):
        self.Document = Document
        self.document = Document()

    def addTitle(self, title):
        lines = title.splitlines()
        if lines:
            # 第一行加大加粗
            p = self.document.add_paragraph()
            run = p.add_run(lines[0])
            run.bold = True
            run.font.name = self.fontName
            run.font.size = Pt(self.fontSizeBig)
            # 其余行普通字体
            for line in lines[1:]:
                p = self.document.add_paragraph()
                run = p.add_run(line)
                run.font.name = self.fontName
                run.font.size = Pt(self.fontSize)

    def addTask1Info(self, info):
        for item in info:
            p = self.document.add_paragraph(f"{item}", style='List Bullet')

    def addTask2Pics(self, pics):
        from docx.shared import Inches
        picCnt = 1
        for pic in pics:
            self.document.add_paragraph(f"Slika: {picCnt}", style='List Bullet')
            if os.path.exists(pic):
                try:
                    with Image.open(pic) as img:
                        orig_w, orig_h = img.size
                        # 假设A4纸dpi为72，1英寸=25.4mm
                        # 计算像素到mm的转换比例
                        dpi = 72
                        orig_w_mm = orig_w / dpi * 25.4
                        orig_h_mm = orig_h / dpi * 25.4
                        scale = min(self.picMaxWidth / orig_w_mm, self.picMaxHeight / orig_h_mm, 1)
                        w = orig_w_mm * scale
                        h = orig_h_mm * scale
                        
                        self.document.add_picture(pic, width=Inches(w/25.4), height=Inches(h/25.4))
                except Exception as e:
                    self.document.add_paragraph(f"[图片插入失败] {pic}: {e}")
            else:
                self.document.add_paragraph(f"[图片不存在] {pic}")
            picCnt += 1

    def end(self):
        self.document.save(self.file_path)

def extendsFolderForPic(list):
    pics = []
    suppoeted_file_format = (".jpg", ".png")
    for f in list:
        if os.path.exists(f):
            if os.path.isfile(f):
                if f.lower().endswith(suppoeted_file_format):
                    pics.append(f)
            elif os.path.isdir(f):
                images = os.listdir(f)
                for file in images:
                    if file.lower().endswith(suppoeted_file_format):
                        pics.append(os.path.join(f, file))
    return pics

class Exam:
    def __init__(self, json_path):
        if not os.path.exists(json_path):
            print(f"文件不存在: {json_path}")
            sys.exit(1)
        
        data = {}
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.num_of_simple_in_task1 = data.get("num_of_simple_in_task1", 3)
        self.info_task1_simple = data.get("info_task1_simple", ["Država", ["Starost", "Rojstni dan"], "Naslov", "E-naslov", "Telefon" ])
        self.num_of_complex_in_task1 = data.get("num_of_complex_in_task1", 2)
        self.info_task1_complex = data.get("info_task1_complex", [ "Moje stanovanje", "Hobiji", "Moja družina", "Moj dan" ])
        self.num_of_pic_for_tak2 = 2
        self.info_task2_pics = extendsFolderForPic(data.get("info_task2_pics", ["pic01.png","pic02.png","pic03.png"]))

    def MakeChoice(self, selected_info, group, num):
        '''随机选择 num 个元素到 selected_info 中'''
        choices = random.sample(group, num)
        for item in choices:
            if isinstance(item, list):
                # 如果选中的是数组，则从中选一个
                selected_info.append(random.choice(item))
            else:
                selected_info.append(item)

    def generate_tasks(self):
        """生成任务题目"""
        # 任务1
        task1_info = [ "Ime in priimek" ]
        # 从简单信息中选 3 个
        self.MakeChoice(task1_info, self.info_task1_simple, self.num_of_simple_in_task1)
        # 从复杂信息中选 2 个
        self.MakeChoice(task1_info, self.info_task1_complex, self.num_of_complex_in_task1)
        task1 = "# 1: Kdo ste? Predstavite se.\n"
        
        task2_pics = []
        self.MakeChoice(task2_pics, self.info_task2_pics, self.num_of_pic_for_tak2)
        task2 = '''# Naloga 2: Izberite ENO sliko. Opišite sliko.
Kaj je na sliki?
Kje je to?
Koliko oseb je na sliki? Kakšne so?
Kaj delajo?
'''
        
        task3 = "# Naloga 3: Vi ste v situaciji na sliki. Kaj govorite?\n\n"
        return [(task1, task1_info), (task2, task2_pics), task3]
    
    def task_walker(self, task_list, walker):
        walker.start()
        task1 = task_list[0][0]
        task1_info = task_list[0][1]
        task2 = task_list[1][0]
        task2_pics = task_list[1][1]
        task3 = task_list[2]
        walker.addTitle(task1)
        walker.addTask1Info(task1_info)
        walker.addTitle(task2)
        walker.addTask2Pics(task2_pics)
        walker.addTitle(task3)
        walker.end()


    def show_tasks(self, task_list):
        walker = PrintWakler()
        self.task_walker(task_list, walker)

    def save_to_markdown(self, task_list, md_file):
        walker = MarkdownFileWalker(md_file)
        self.task_walker(task_list, walker)

    def save_to_pdf(self, task_list, pdf_file):
        walker = PDFFileWalker(pdf_file)
        self.task_walker(task_list, walker)

    def save_to_docx(self, task_list, docx_file):
        walker = DocxFileWalker(docx_file)
        self.task_walker(task_list, walker)

def main():
    print("=== Speaking Exam Simulator ===\n")

    ex = Exam("taskcfg.json")
    tasks = ex.generate_tasks()
    ex.show_tasks(tasks)
    ex.save_to_markdown(tasks, "out_exam.md")
    print(f"Markdown已生成")
    ex.save_to_pdf(tasks, "out_exam.pdf")
    print(f"PDF已生成")
    ex.save_to_docx(tasks, "out_exam.docx")
    print(f"Docx已生成")

if __name__ == "__main__":
    main()

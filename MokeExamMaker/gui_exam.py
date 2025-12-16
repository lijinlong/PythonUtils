import tkinter as tk
from tkinter import filedialog, messagebox
import os, sys
import shutil

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

from MokeExam import Exam


class ExamGUI:
    def __init__(self, master):
        self.master = master
        master.title("Speaking Exam GUI")
        sample_json_file = "taskcfg.json"
        if getattr(sys, 'frozen', False):
            # 被打包为exe时
            exe_dir = os.path.dirname(sys.executable)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_list  = [ sample_json_file , "DejaVuSans.ttf", "DejaVuSans-Bold.ttf" ]
            # 拷贝文件到exe目录
            for f in file_list:
                dst_path = os.path.join(exe_dir, f)
                if not os.path.exists(dst_path):
                    shutil.copy(os.path.join(script_dir, f), dst_path)
            # 创建图片文件夹并拷贝样例图片
            for f in ["ImgA1", "ImgA2"]:
                dst_path = os.path.join(exe_dir, f)
                if not os.path.exists(dst_path):
                    os.makedirs(dst_path)
            for i in range(1, 6+1):
                img = f"pic{i:02d}.png"
                dst_path = os.path.join(exe_dir, "ImgA1", img)
                if not os.path.exists(dst_path):
                    shutil.copy(os.path.join(script_dir, "pic00.png"), dst_path)

            
        else:
            # 普通脚本运行时
            exe_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(exe_dir, "taskcfg.json")
        self.image_refs = []  # keep references to PhotoImage to avoid GC

        btn_frame = tk.Frame(master)
        btn_frame.pack(fill=tk.X, padx=8, pady=8)

        # 多语言支持
        self.languages = {"zh": "中文", "en": "English"}
        self.lang_texts = {
            "zh": {
                "settings": "设置出题规则",
                "start": "开始出题",
                "clear": "清空",
                "export_pdf": "导出题目",
                "config_file": "配置文件",
                "select_config": "选择配置文件 (JSON)",
                "select_config_success": "已选择配置文件:",
                "error_load_config": "无法加载配置文件:",
                "error": "错误",
                "error_generate": "生成任务时出错:",
                "tip": "提示",
                "warn_generate": "请先生成任务再导出！",
                "export_success": "导出成功",
                "export_fail": "导出失败",
                "pdf_saved": "PDF已保存到：",
                "docx_saved": "Docx已保存到：",
                "select_pdf": "导出为PDF"
            },
            "en": {
                "settings": "Set Exam Config",
                "start": "Start Exam",
                "clear": "Clear",
                "export_pdf": "Export Result",
                "config_file": "Config File",
                "select_config": "Select Config File (JSON)",
                "select_config_success": "Config file selected:",
                "error_load_config": "Cannot load config file:",
                "error": "Error",
                "error_generate": "Error generating tasks:",
                "tip": "Tip",
                "warn_generate": "Please generate tasks before exporting!",
                "export_success": "Export Success",
                "export_fail": "Export Failed",
                "pdf_saved": "PDF saved to:",
                "docx_saved": "Docx saved to:",
                "select_pdf": "Export as PDF"
            }
        }
        self.current_lang = "en"

        # 语言选择和按钮全部放在btn_frame同一行
        tk.Label(btn_frame, text="语言/Language:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.current_lang)
        lang_menu = tk.OptionMenu(btn_frame, self.lang_var, *self.languages.keys(), command=self.change_language)
        lang_menu.pack(side=tk.LEFT, padx=(0, 12))

        self.settings_btn = tk.Button(btn_frame, text=self._t("settings"), width=15, command=self.open_settings)
        self.settings_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.start_btn = tk.Button(btn_frame, text=self._t("start"), width=15, command=self.start_exam)
        self.start_btn.pack(side=tk.LEFT)

        self.export_pdf_btn = tk.Button(btn_frame, text=self._t("export_pdf"), width=15, command=self.export_pdf)
        self.export_pdf_btn.pack(side=tk.RIGHT, padx=(8,0))
        self.clear_btn = tk.Button(btn_frame, text=self._t("clear"), command=self.clear_display)
        self.clear_btn.pack(side=tk.RIGHT)

        # Use a frame with a Text widget for text and images
        text_frame = tk.Frame(master)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))

        self.text = tk.Text(text_frame, wrap=tk.WORD)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        # status
        self.status = tk.Label(master, text=f"{self._t('config_file')}: {os.path.basename(self.config_path)}", anchor=tk.W)
        self.status.pack(fill=tk.X, padx=8, pady=(0,8))

        self.tasks = None
        
    def _t(self, key):
        return self.lang_texts[self.current_lang].get(key, key)

    def change_language(self, lang):
        self.current_lang = lang
        self.settings_btn.config(text=self._t("settings"))
        self.start_btn.config(text=self._t("start"))
        self.clear_btn.config(text=self._t("clear"))
        self.export_pdf_btn.config(text=self._t("export_pdf"))
        self.status.config(text=f"{self._t('config_file')}: {os.path.basename(self.config_path)}")

    def open_settings(self):
        path = filedialog.askopenfilename(title=self._t("select_config"), filetypes=[("JSON files","*.json"), ("All files","*.*")])
        if path:
            self.config_path = path
            self.status.config(text=f"{self._t('config_file')}: {os.path.basename(self.config_path)}")
            messagebox.showinfo(self._t("settings"), f"{self._t('select_config_success')}\n{self.config_path}")

    def start_exam(self):
        try:
            self.ex = Exam(self.config_path)
        except SystemExit:
            messagebox.showerror(self._t("error"), f"{self._t('error_load_config')} {self.config_path}")
            return
        except Exception as e:
            messagebox.showerror(self._t("error"), str(e))
            return

        try:
            self.tasks = self.ex.generate_tasks()
            self.display_tasks(self.tasks)
        except Exception as e:
            messagebox.showerror(self._t("error"), f"{self._t('error_generate')}\n{e}")

    def clear_display(self):
        self.text.delete("1.0", tk.END)
        self.image_refs.clear()

    def export_pdf(self):
        if not self.tasks:
            messagebox.showwarning(self._t("tip"), self._t("warn_generate"))
            return
        pdf_path = filedialog.asksaveasfilename(title=self._t("select_pdf"), defaultextension=".pdf", filetypes=[("PDF files","*.pdf"), ("All files","*.*")])
        if not pdf_path:
            return
        try:
            self.ex.save_to_pdf(self.tasks, pdf_path)
            docx_path = pdf_path.replace(".pdf", ".docx")
            self.ex.save_to_docx(self.tasks, docx_path)
            messagebox.showinfo(self._t("export_success"), f"{self._t('pdf_saved')}\n{pdf_path}\n{self._t('docx_saved')}\n{docx_path}")
        except Exception as e:
            messagebox.showerror(self._t("export_fail"), str(e))

    def _load_image_for_display(self, pic_path):
        """尝试加载图片，返回一个 PhotoImage 或 None。"""
        # Resolve relative path against config file
        base_dir = os.path.dirname(self.config_path)
        candidate = pic_path
        if not os.path.isabs(candidate):
            candidate = os.path.join(base_dir, pic_path)

        if not os.path.exists(candidate):
            return None, f"(图片不存在: {candidate})"

        try:
            if PIL_AVAILABLE:
                img = Image.open(candidate)
                # Resize to reasonable width if too large
                max_w = 420
                if img.width > max_w:
                    ratio = max_w / img.width
                    new_h = int(img.height * ratio)
                    img = img.resize((max_w, new_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            else:
                # tkinter PhotoImage supports PNG/GIF
                photo = tk.PhotoImage(file=candidate)
            return photo, None
        except Exception as e:
            return None, str(e)

    def display_tasks(self, tasks):
        self.clear_display()

        # Task 1
        t1_header = tasks[0][0]
        t1_info = tasks[0][1]
        self.text.insert(tk.END, t1_header + "\n")
        for info in t1_info:
            self.text.insert(tk.END, f"- {info}\n")
        self.text.insert(tk.END, "\n")

        # Task 2
        t2_header = tasks[1][0]
        t2_pics = tasks[1][1]
        self.text.insert(tk.END, t2_header + "\n")

        picCnt = 1
        for pic in t2_pics:
            self.text.insert(tk.END, f"- Slika: {picCnt}\n")
            # Try load and insert image where previously printed the path
            photo, err = self._load_image_for_display(pic)
            if photo:
                # keep ref
                self.image_refs.append(photo)
                self.text.image_create(tk.END, image=photo)
                self.text.insert(tk.END, "\n")
            else:
                # If cannot load image, show the path or error
                self.text.insert(tk.END, f"{pic} {err or ''}\n")
            picCnt += 1
        self.text.insert(tk.END, "\n")

        # Task 3
        self.text.insert(tk.END, tasks[2])


def main():
    root = tk.Tk()
    root.geometry("760x560")
    app = ExamGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

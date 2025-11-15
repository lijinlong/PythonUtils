import os
import argparse
from PyPDF2 import PdfReader, PdfWriter
from pdf2docx import Converter

def pdf_to_docx(pdf_path, docx_path):
    try:
        cv = Converter(pdf_path)
        # preserve_layout=True 尽量保持原排版
        cv.convert(docx_path, start=0, end=None, 
                   layout_mode='exact', # 保留布局
                   table_structure=True, # 保留表格
                   preserve_font=True)   # 保留字体信息
        cv.close()
        print(f"[OK] {pdf_path} → {docx_path}")
    except Exception as e:
        print(f"[ERROR] {pdf_path} 转换失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a PDF file to DOCX using pdf2docx."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        default="wordlist.pdf",
        help="Path to the PDF file to convert (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output DOCX filename. If omitted, derived from the PDF filename.",
    )

    args = parser.parse_args()

    pdf_name = args.pdf
    # If the user provided an explicit output name, use it; otherwise replace the PDF extension with .docx
    docx_name = args.output if args.output else os.path.splitext(pdf_name)[0] + ".docx"

    pdf_to_docx(pdf_name, docx_name)
    print(f"Done. Converted: {pdf_name} → {docx_name}")

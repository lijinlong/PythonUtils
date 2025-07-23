import asyncio
import pysrt
import os
import argparse
import glob
from googletrans import Translator

### 需要安装 googletrans 库 ·pip install googletrans·

# 设置置信度阈值
ACCEPT_CONFIDENCE = 0.9  

async def translate_text(text, src_lang='auto', target_lang=None, sub=None):
    if target_lang is None:
        target_lang = 'en'  # 默认目标语言为英语

    async with Translator() as translator:
        print(f"Translating [{sub.index}][{sub.start}]: '{text}' ...")
        if sub is not None:
            result = await translator.translate(text, src=src_lang, dest=target_lang)
            print(f"{result.src}->{result.dest}:\t{result.text}")
            # print(f"Pronunciation: {result.pronunciation}")
            confidence = float(result.extra_data.get('confidence') or 0)
            # print(f"Confidence: {confidence}")

            # 如果 confidence 大于 0.9，记录翻译结果
            if confidence < ACCEPT_CONFIDENCE:
                result.text = f"?{confidence:.2f}?" + result.text + "??"
                confidence = ACCEPT_CONFIDENCE

            if confidence >= ACCEPT_CONFIDENCE:
                sub.text = result.text
            

# 用户交互部分
async def main():
     # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Google Translate CLI Tool")
    parser.add_argument("-src", help="源语言代码 (默认 'sl')", default=None)
    parser.add_argument("-dst", help="目标语言代码列表 (用逗号分隔，默认 'en,zh-CN')", default=None)
    parser.add_argument("file", nargs="?", help="要翻译的srt文件路径", default=None)
    args = parser.parse_args()

    # 如果命令行参数提供了源语言和目标语言，则使用它们
    src_lang = args.src or input("请输入源语言代码(默认 'sl' 斯洛文尼亚语):") or 'sl'
    target_langs = args.dst or input("请输入目标语言代码列表(用逗号分隔，默认 'en,zh-CN'):") or 'en,zh-CN'
    target_langs = target_langs.split(',')


    input_sub_str = args.file or input(f"请输入字幕文件名:") or "DzunglskiRompompom.srt"
    # src_lang = 'sl'
    # target_lang = 'zh-CN' #['en', 'zh-CN']  # 默认目标语言为英语和中文

    input_subs = []
    if '*' in input_sub_str:
        lrc_files = glob.glob(input_sub_str)
        dotNum = input_sub_str.count('.')
        if dotNum < 1:
            dotNum = 1
        input_subs = [f for f in lrc_files if f.count('.') == dotNum]
    else:
        if not os.path.exists(input_sub_str):
            print(f"文件 {input_sub_str} 不存在，请检查路径。")
            return
        input_subs.append(input_sub_str)

    for input_sub in input_subs:
        for target_lang in target_langs:
            print(f"====正在处理 {input_sub}，目标语言：{target_lang}\n\n")
            name, ext = os.path.splitext(input_sub)
            output_sub = f"{name}.{target_lang}{ext}"
            # 加载字幕文件
            subs = pysrt.open(input_sub, encoding='utf-8')

            # 遍历每一条字幕进行翻译
            for sub in subs:
                await translate_text(sub.text, src_lang=src_lang, target_lang=target_lang, sub=sub)

            # 保存为新文件
            subs.save(output_sub, encoding='utf-8')
            print(f"翻译完成，已保存为 {output_sub}")


# 运行程序
asyncio.run(main())

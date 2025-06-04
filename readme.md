# GoogleTrans.py
对输入文本进行谷歌翻译

按提示输入源语言，目标语言，翻译文本进行翻译，最后提示置信度高的文本进行保存（json和md）
`python GoogleTrans.py`

从命令行直接输入源语言，目标语言和翻译文本
`python GoogleTrans.py -src sl -dst en,zh-CN <file>`

# RemoveDupFiles.py
移除重复文件，目标目录可根据提示输入也可作为参数输入
`python RemoveDupFiles.py`
`python RemoveDupFiles.py .`

# GatherRes.py
生成资源列表，用法详见GatherRes.py
`python GatherRes.py e:\\Book_tbd\\res\\res.json MyRes.json`

# SearchRes.py
从Resources.json中进行关键字搜索，关键字支持普通文本、与、或及正则表达式
`python SearchRes.py Resources.json 关键字`


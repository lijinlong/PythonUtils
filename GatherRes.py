import json
import os
import sys

def print_help():
    print("用法: python GatherRes.py <res.json路径> [输出文件名]")
    print("  <res.json路径>    必填，资源配置json文件路径")
    print("  [输出文件名]      可选，输出json文件名，默认Resources.json")
    print("示例:")
    print("  python GatherRes.py e:\\Book_tbd\\res\\res.json MyRes.json")
    print("  python GatherRes.py e:\\Book_tbd\\res\\res.json")
    print("  python GatherRes.py   # 交互输入路径")
    print("\n[res.json] 配置文件格式示例：")
    print('''{
    "Books": {
        "desc": "Books",
        "dirs": ["G:\\\\Books"]
    },
    "Movies": {
        "desc": "Movies",
        "dirs": ["G:\\\\Entertainment"],
        "exceptions": [
            "百家讲坛",
            "广播剧有声书",
            "评书"
        ]
    },
    "Music": {
        "desc": "Music",
        "dirs": "G:\\\\Music",
        "filter": [
            ".mp3",
            ".flac"
        ]
    }
}''')
    print("\n输出文件格式示例（每个资源为一个键，值为列表，列表元素为包含目录和内容的对象）：")
    print('''{
    "Books": [
        {
            "dir": "G:\\\\Books",
            "contents": [
                ["SubDir1", [
                    "file1.pdf",
                    "file2.txt"
                ]],
                "rootfile1.txt"
            ]
        }
    ],
    "Music": [
        {
            "dir": "G:\\\\Music",
            "contents": [
                "song1.mp3",
                ["专辑A", [
                    "track1.flac"
                ]]
            ]
        }
    ]
}''')

def scan_dir(root, filters, exceptions):
    # 返回紧凑嵌套列表结构，不包含root本身
    result = []
    for entry in os.scandir(root):
        if entry.is_dir():
            if any(exc in entry.path for exc in exceptions):
                continue
            sub = scan_dir(entry.path, filters, exceptions)
            if sub:
                result.append([entry.name, sub])
        elif entry.is_file():
            ext = os.path.splitext(entry.name)[1].lower()
            if not filters or ext in filters:
                result.append(entry.name)
    return result

def scan_resource(name, resource):
    dirs = resource.get("dirs")
    if isinstance(dirs, str):
        dirs = [dirs]
    filters = resource.get("filter", [])
    exceptions = set(resource.get("exceptions", []))
    all_results = []
    for base_dir in dirs:
        all_results.append({
            "dir": base_dir,
            "contents": scan_dir(base_dir, filters, exceptions)
        })
    return all_results

def parse_res_json(filepath, outpath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result_dict = {}
    for name, resource in data.items():
        res = scan_resource(name, resource)
        if res:
            result_dict[name] = res
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)
    print(f"已保存到 {outpath}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "/?"):
        print_help()
        sys.exit(0)
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = input("请输入res.json路径: ").strip()
        if not json_path:
            print("未输入路径，程序退出。")
            print_help()
            sys.exit(1)
    if not os.path.exists(json_path):
        print(f"文件不存在: {json_path}，程序退出。")
        print_help()
        sys.exit(1)
    if len(sys.argv) > 2:
        out_path = sys.argv[2]
    else:
        out_path = "Resources.json"
    parse_res_json(json_path, out_path)
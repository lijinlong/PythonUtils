import json
import sys
import os
import re

def match_keyword(filename, keyword):
    """
    支持多种搜索方式：
    1. 普通子串（默认，忽略大小写）
    2. 多关键字与（&分隔，全部包含，忽略大小写）
    3. 多关键字或（|分隔，任意包含，忽略大小写）
    4. 正则表达式（以re:开头，后跟正则表达式）
    """
    if keyword.startswith("re:"):
        pattern = keyword[3:]
        try:
            return re.search(pattern, filename, re.IGNORECASE) is not None
        except re.error:
            return False
    elif "|" in keyword:
        # 多关键字或（|分隔）
        keys = [k.strip().lower() for k in keyword.strip().split("|") if k.strip()]
        return any(k in filename.lower() for k in keys)
    elif "&" in keyword:
        # 多关键字与（&分隔）
        keys = [k.strip().lower() for k in keyword.strip().split("&") if k.strip()]
        return all(k in filename.lower() for k in keys)
    else:
        # 普通子串
        return keyword.lower() in filename.lower()

def search_in_tree(tree, keyword, base_dir, path=""):
    """递归在紧凑嵌套列表结构中查找文件名，返回匹配的完整路径列表"""
    results = []
    for item in tree:
        if isinstance(item, str):
            if match_keyword(item, keyword):
                full_path = os.path.abspath(os.path.join(base_dir, path, item))
                results.append(full_path)
        elif isinstance(item, list) and len(item) == 2 and isinstance(item[1], list):
            subdir, sublist = item
            results += search_in_tree(sublist, keyword, base_dir, os.path.join(path, subdir))
    return results

def main():
    if len(sys.argv) < 3:
        print("用法: python SearchRes.py <Resources.json路径> <关键字>")
        print("关键字支持：普通子串、多关键字与（&分隔）、多关键字或（|分隔）、正则（re:pattern）")
        sys.exit(1)
    json_path = sys.argv[1]
    keyword = sys.argv[2]
    if not os.path.exists(json_path):
        print(f"文件不存在: {json_path}")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    found = False
    for name, resource_list in data.items():
        # resource_list 是一个列表，每个元素是 {"dir": ..., "contents": [...]}
        for resource in resource_list:
            base_dir = resource.get("dir", "")
            tree = resource.get("contents", [])
            matches = search_in_tree(tree, keyword, base_dir)
            if matches:
                found = True
                print(f"[{name}] ({base_dir})")
                for m in matches:
                    print("  " + m)
    if not found:
        print("未找到匹配文件。")

if __name__ == "__main__":
    main()
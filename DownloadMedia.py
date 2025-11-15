import os, sys
import re
import json
import requests
import argparse

def download_file(url, save_path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True, None
        else:
            return False, f"Failed: {url} ({r.status_code})"
    except Exception as e:
        return False, f"Error downloading {url}: {e}"

def load_fileset_from_json(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {json_file}: {e}")
        sys.exit(1)

def validate_fileset(fileset):
    required_fields = ["title", "save_dir", "num_files", "base_url", "web_file_pattern", "save_file_pattern"]
    for fs in fileset:
        missing_fields = [field for field in required_fields if field not in fs]
        if missing_fields:
            raise ValueError(f"Fileset validation failed. Missing fields: {', '.join(missing_fields)} in {fs}")

def main(download_fileset, validate=True):
    failed_files = []
    if validate:
        validate_fileset(download_fileset)
    
    for fs in download_fileset:
        save_dir = fs["save_dir"] or "audio"
        title = fs["title"]
        #print(f"Create Dir: {save_dir} for {len(files)} files")
        os.makedirs(save_dir, exist_ok=True)
        num_files = fs["num_files"]
        for sid in range(1, num_files+1):
            filename = fs["save_file_pattern"].format(title=title, sid=sid)
            fileOnWeb = fs["web_file_pattern"].format(title=title, sid=sid)
            url = f"{fs['base_url']}{fileOnWeb}"
            save_path = os.path.join(save_dir, filename)
            if not os.path.exists(save_path):
                print(f"Downloading {url} to {save_path}")
                success, reason = download_file(url, save_path)
                if not success:
                    failed_files.append((filename, reason))

    if failed_files:
        print(f"\n下载失败的文件: (count={len(failed_files)})")
        for fname, reason in failed_files:
            print(f"{fname}: {reason}")
    else: 
        print(f"所有文件下载成功！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download media files based on a fileset configuration.")
    parser.add_argument("-mf", "--manifest", type=str, help="Path to the JSON file containing the download_fileset.")
    args = parser.parse_args()

    if args.manifest:
        download_fileset = load_fileset_from_json(args.manifest)
    else:
        default_fileset = [
            {
                "title": "Title",
                "save_dir": "audio",
                "num_files": 24,
                "base_url": "localhost:8080/contents/uploads/",
                "web_file_pattern": "{title}-{sid}.mp3",
                "save_file_pattern": "{title}-{sid:02d}.mp3",
            }
        ]
        default_json_path = "download_fileset.json"
        with open(default_json_path, "w", encoding="utf-8") as f:
            json.dump(default_fileset, f, indent=4, ensure_ascii=False)
        print(f"默认的下载配置已保存到 {default_json_path}。请修改该文件内容，并使用 -mf download_fileset.json 参数重新运行程序。")
        sys.exit(0)

    validate_fileset(download_fileset)
    main(download_fileset, False)
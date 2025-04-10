import os
import hashlib
import sys

def calculate_file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_func = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def find_duplicate_files(directory):
    """查找指定目录中的重复文件"""
    if not os.path.isdir(directory):
        print(f"目录 {directory} 不存在或不是一个有效的目录。")
        return []

    file_hashes = {}
    duplicates = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_file_hash(file_path)

            if file_hash in file_hashes:
                existing_file = file_hashes[file_hash]
                # 比较文件名长度，保留文件名较短的文件
                if len(file) < len(os.path.basename(existing_file)):
                    duplicates.append((existing_file, file_hash))
                    file_hashes[file_hash] = file_path
                else:
                    duplicates.append((file_path, file_hash))
            else:
                file_hashes[file_hash] = file_path

    return duplicates, file_hashes

def remove_files(file_list):
    """删除文件列表中的文件"""
    for file_path, file_hash in file_list:
        try:
            os.remove(file_path)
            print(f"已删除: {file_path}")
        except Exception as e:
            print(f"无法删除 {file_path}: {e}")

if __name__ == "__main__":
    # 从命令行参数读取目录路径
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
    else:
        # 如果未提供路径，提示用户输入
        target_directory = input("请输入要扫描的目录路径: ").strip()

    duplicates, file_hashes = find_duplicate_files(target_directory)

    if duplicates:
         # 按哈希值对重复文件排序
        duplicates.sort(key=lambda x: x[1])

        print("\n以下是检测到的重复文件：")
        tmpHash = 0
        for file, hash in duplicates:
            if tmpHash != hash:
                tmpHash = hash
                print(f"\n与{file_hashes[hash]}重复的文件:\nMD5: {hash}")
            print(f"\t{file}")

        confirm = input("\n是否确认删除以上文件？(y/n): ").strip().lower()
        if confirm == 'y':
            remove_files(duplicates)
        else:
            print("操作已取消，未删除任何文件。")
    else:
        print("未发现重复文件。")
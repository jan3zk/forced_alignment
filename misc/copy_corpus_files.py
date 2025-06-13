import sys
import os
import shutil

def load_keywords(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        keywords = [line.strip() for line in file if line.strip()]
    return keywords

def find_and_copy_files(search_dirs, keywords, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    total_copied = 0

    for keyword in keywords:
        matched = False
        for search_dir in search_dirs:
            for root, _, files in os.walk(search_dir):
                for filename in files:
                    if keyword in filename:
                        src_path = os.path.join(root, filename)
                        dest_path = os.path.join(output_dir, filename)

                        if not os.path.exists(dest_path):
                            shutil.copy2(src_path, dest_path)
                            print(f"[COPYING] {filename}")
                            total_copied += 1
                        else:
                            print(f"[SKIPPED] {filename} (already exists)")
                        matched = True
        if not matched:
            print(f"[WARNING] No file found for keyword: {keyword}")
    
    print(f"\n[SUMMARY] Total files copied: {total_copied}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python copy_matching_files.py <keywords.txt> <search_dir1> [<search_dir2> ...] <output_dir>")
        sys.exit(1)

    txt_path = sys.argv[1]
    output_dir = sys.argv[-1]
    search_dirs = sys.argv[2:-1]

    keywords = load_keywords(txt_path)
    find_and_copy_files(search_dirs, keywords, output_dir)

if __name__ == "__main__":
    main()

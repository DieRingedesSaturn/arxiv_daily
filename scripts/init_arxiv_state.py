import os
import re
import json
import glob

POSTS_DIR = "./docs/posts"
STATE_FILE = os.path.join(POSTS_DIR, "state.json")

def initialize_state():
    processed_ids = set()
    
    # 匹配 arXiv 链接的正则表达式
    # 示例: http://arxiv.org/abs/2603.02993v1
    arxiv_pattern = re.compile(r'https?://arxiv\.org/abs/[\d.a-z/v]+', re.IGNORECASE)
    
    # 遍历所有总结文件
    summary_files = glob.glob(os.path.join(POSTS_DIR, "Arxiv_Summary_*.md"))
    print(f"找到 {len(summary_files)} 个历史总结文件。")
    
    for file_path in summary_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = arxiv_pattern.findall(content)
            for match in matches:
                # 统一转为 https 并去除可能的末尾空格/括号
                entry_id = match.strip().replace("http://", "https://")
                processed_ids.add(entry_id)
                
    print(f"共提取到 {len(processed_ids)} 个唯一的论文 ID。")
    
    # 保存到 state.json
    state = {"processed_ids": list(processed_ids)}
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)
    
    print(f"已将 ID 写入 {STATE_FILE}。")

if __name__ == "__main__":
    initialize_state()

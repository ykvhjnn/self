import sys

# 结尾匹配黑名单
REMOVE_END = {
    "gh-proxy.com", "outlook.com"
}

# 包含关键词黑名单
REMOVE_KEYWORD = {
    "jsdelivr", "bilibili"
}

# 匹配域名黑名单
REMOVE_DOMAIN = {
}

def is_remove_end(domain: str) -> bool:
    for suffix in REMOVE_END:
        if domain.endswith(suffix):
            return True
    return False

def is_remove_keyword(line: str) -> bool:
    for keyword in REMOVE_KEYWORD:
        if keyword in line:
            return True
    return False

def is_remove_domain(domain: str) -> bool:
    return domain in REMOVE_DOMAIN

def main():
    if len(sys.argv) < 2:
        print("请提供输入文件路径作为参数")
        return
    file_name = sys.argv[1]
    result = []
    with open(file_name, "r", encoding="utf8") as f:
        for line in f:
            line = line.rstrip("\n")
            if is_remove_keyword(line):
                continue
            # 只做简单的行处理，提取域名
            domain = line
            if is_remove_end(domain):
                continue
            if is_remove_domain(domain):
                continue
            result.append(line)
    with open(file_name, "w", encoding="utf8") as f:
        for domain in result:
            f.write(f"{domain}\n")
    print(f"去除域名完成，保留的规则总数为：{len(result)}")

if __name__ == "__main__":
    main()
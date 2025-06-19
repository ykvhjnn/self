import sys

# 结尾匹配黑名单
REMOVE_END = {
    ".jp", ".kr", ".in", ".id", ".th", ".sg", ".my", ".ph", ".vn",
    ".pk", ".bd", ".lk", ".np", ".mn", ".uz", ".kz", ".kg", ".bt", ".mv", ".mm",
    ".uk", ".de", ".fr", ".it", ".es", ".ru", ".nl", ".be", ".ch", ".at", ".pl",
    ".cz", ".se", ".no", ".fi", ".dk", ".gr", ".pt", ".ie", ".hu", ".ro", ".bg",
    ".sk", ".si", ".lt", ".lv", ".ee", ".is", ".md", ".ua", ".by", ".am", ".ge",
    ".us", ".ca", ".mx", ".br", ".ar", ".cl", ".co", ".pe", ".ve", ".uy", ".py",
    ".bo", ".ec", ".cr", ".pa", ".do", ".gt", ".sv", ".hn", ".ni", ".jm", ".cu",
    ".za", ".eg", ".ng", ".ke", ".gh", ".tz", ".ug", ".dz", ".ma", ".tn", ".ly",
    ".ci", ".sn", ".zm", ".zw", ".ao", ".mz", ".bw", ".na", ".rw", ".mw", ".sd",
    ".au", ".nz", ".fj", ".pg", ".sb", ".vu", ".nc", ".pf", ".ws", ".to", ".ki",
    ".tv", ".nr", ".as",
    ".sa", ".ae", ".ir", ".il", ".iq", ".tr", ".sy", ".jo", ".lb", ".om", ".qa",
    ".ye", ".kw", ".bh",
    "ms.bdstatic.com"
}

# 包含关键词黑名单
REMOVE_KEYWORD = {
    # 这里可以添加需要去除的具体域名
}

# 匹配域名黑名单
REMOVE_DOMAIN = {
    # 这里可以添加需要去除的具体域名
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
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
    # 这里可以添加需要去除的具体关键词
}

# 匹配域名黑名单
REMOVE_DOMAIN = set([
    # 请在这里添加需要屏蔽的域名，如：
    # "example.com",
    # "adserver.test"
])

def is_remove_end(domain: str) -> bool:
    """判断域名是否以黑名单的后缀结尾"""
    return any(domain.endswith(suffix) for suffix in REMOVE_END)

def is_remove_keyword(line: str) -> bool:
    """判断行内是否含有黑名单关键词"""
    return any(keyword in line for keyword in REMOVE_KEYWORD)

def is_remove_domain(domain: str) -> bool:
    """判断域名是否在域名黑名单中"""
    return domain in REMOVE_DOMAIN

def process_lines(lines):
    """处理所有行，返回过滤后的新列表"""
    result = []
    for line in lines:
        line = line.rstrip("\n")
        if is_remove_keyword(line):
            continue
        domain = line  # 只做简单处理
        if is_remove_end(domain):
            continue
        if is_remove_domain(domain):
            continue
        result.append(line)
    return result

def main():
    if len(sys.argv) < 2:
        print("请提供输入文件路径作为参数")
        return
    file_name = sys.argv[1]
    try:
        with open(file_name, "r", encoding="utf8") as f:
            lines = f.readlines()
        result = process_lines(lines)
        with open(file_name, "w", encoding="utf8") as f:
            f.writelines(f"{domain}\n" for domain in result)
        print(f"去除域名完成，保留的规则总数为：{len(result)}")
    except Exception as e:
        print(f"处理文件时出错: {e}")

if __name__ == "__main__":
    main()

import sys
import asyncio

# 结尾匹配黑名单（REMOVE_END）
REMOVE_END = {
    "."
}

# 包含关键词黑名单
REMOVE_KEYWORD = {
    "payload:", "rules:", "regexp", "IP-CIDR,", "DOMAIN-KEYWORD,", "PROCESS-NAME,",
    "IP-SUFFIX,", "GEOIP,", "GEOSITE,",
    "#", "*", "!", "/", "【", "】", "[", "]", "$"
}

def clean_line(line: str) -> str:
    """
    清理行中的无效字符
    """
    for ch in " \"'|^":
        line = line.replace(ch, "")
    return line

def is_remove_keyword(line: str) -> bool:
    """
    判断行内是否含有黑名单关键词
    """
    return any(keyword in line for keyword in REMOVE_KEYWORD)

def is_remove_end(domain: str) -> bool:
    """
    判断域名是否以黑名单结尾
    """
    return any(domain.endswith(suffix) for suffix in REMOVE_END)

def prefilter_line(line: str) -> bool:
    """
    行预过滤，包含黑名单关键词或@@的直接丢弃
    """
    if is_remove_keyword(line):
        return False
    if "@@" in line:
        return False
    return True

def extract_domain(line: str) -> str | None:
    """
    提取有效域名，支持多种前缀
    """
    line = clean_line(line.strip())
    prefixes = [
        ("DOMAIN,", 7),
        ("DOMAIN-SUFFIX,", 14),
        ("+.", 2),
        (".", 1),
        ("-DOMAIN,", 8),
        ("-DOMAIN-SUFFIX,", 15),
        ("-+.", 3),
        ("-.", 2)
    ]
    for prefix, offset in prefixes:
        if line.startswith(prefix):
            domain = line[offset:]
            break
    else:
        domain = line if "." in line else None

    if not domain:
        return None
    domain = domain.strip(".")  # 去除首尾多余点
    if not domain or "." not in domain:
        return None
    return domain

def process_chunk(chunk: list[str]) -> set[str]:
    """
    处理一块文件内容
    """
    result = set()
    for line in chunk:
        if not prefilter_line(line):
            continue
        domain = extract_domain(line)
        if not domain:
            continue
        if is_remove_end(domain):
            continue
        result.add(domain)
    return result

async def read_lines(file_path: str):
    """
    异步读取文件，分块返回行列表
    """
    with open(file_path, "r", encoding="utf8") as f:
        while True:
            lines = f.readlines(10000)
            if not lines:
                break
            yield lines

async def main():
    if len(sys.argv) < 2:
        print("请提供输入文件路径作为参数")
        return
    file_name = sys.argv[1]
    all_domains = set()
    async for chunk in read_lines(file_name):
        all_domains.update(process_chunk(chunk))
    with open(file_name, "w", encoding="utf8") as f:
        for domain in sorted(all_domains):
            f.write(f"{domain}\n")
    print(f"合并规则数：{len(all_domains)}")

if __name__ == "__main__":
    asyncio.run(main())

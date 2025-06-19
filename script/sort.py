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

# 匹配域名黑名单
REMOVE_DOMAIN = {
    # 这里可以添加需要去除的具体域名
}

def clean_line(line: str) -> str:
    for ch in " \"'|^":
        line = line.replace(ch, "")
    return line

def is_remove_keyword(line: str) -> bool:
    for keyword in REMOVE_KEYWORD:
        if keyword in line:
            return True
    return False

def is_remove_end(domain: str) -> bool:
    for suffix in REMOVE_END:
        if domain.endswith(suffix):
            return True
    return False

def is_remove_domain(domain: str) -> bool:
    return domain in REMOVE_DOMAIN

# 先FILTER_KEYWORDS，再去除@@
def prefilter_line(line: str) -> bool:
    if is_remove_keyword(line):
        return False
    if "@@" in line:
        return False
    return True

# 提取有效域名
def extract_domain(line: str) -> str | None:
    line = clean_line(line.strip())
    for prefix, offset in [
        ("DOMAIN,", 7),
        ("DOMAIN-SUFFIX,", 14),
        ("+.", 2),
        (".", 1),
        ("-DOMAIN,", 8),
        ("-DOMAIN-SUFFIX,", 15),
        ("-+.", 3),
        ("-.", 2)
    ]:
        if line.startswith(prefix):
            return line[offset:]
    if "." in line:
        return line
    return None

# 处理一块文件内容
def process_chunk(chunk: list[str]) -> set[str]:
    result = set()
    for line in chunk:
        if not prefilter_line(line):
            continue
        domain = extract_domain(line)
        if not domain:
            continue
        # REMOVE_END
        if is_remove_end(domain):
            continue
        # REMOVE_DOMAIN
        if is_remove_domain(domain):
            continue
        result.add(domain)
    return result

# 异步读取文件，分块返回行列表
async def read_lines(file_path: str):
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

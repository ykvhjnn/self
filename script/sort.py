import sys
import asyncio

REMOVE_END = {
    "."
}

REMOVE_KEYWORD = {
    "payload:", "rules:", "regexp", "IP-CIDR,", "DOMAIN-KEYWORD,", "PROCESS-NAME,",
    "IP-SUFFIX,", "GEOIP,", "GEOSITE,",
    "#", "*", "!", "/", "【", "】", "[", "]", "$"
}

def clean_line(line: str) -> str:
    # 只去除明确无关的符号，不动点和域名内容
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

def prefilter_line(line: str) -> bool:
    if is_remove_keyword(line):
        return False
    if "@@" in line:
        return False
    return True

def extract_domain(line: str) -> str | None:
    # 不对域名内容做任何更改，仅提取
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

def process_chunk(chunk: list[str]) -> set[str]:
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

async def read_lines(file_path: str, chunk_size: int = 100000) -> list[list[str]]:
    """
    异步读取大文件，按chunk_size分块返回，提升I/O效率
    """
    chunks = []
    chunk = []
    async def _read():
        with open(file_path, "r", encoding="utf8") as f:
            for line in f:
                chunk.append(line)
                if len(chunk) >= chunk_size:
                    chunks.append(chunk[:])
                    chunk.clear()
            if chunk:
                chunks.append(chunk[:])
    await asyncio.get_event_loop().run_in_executor(None, _read)
    return chunks

async def main():
    if len(sys.argv) < 2:
        print("请提供输入文件路径作为参数")
        return
    file_name = sys.argv[1]
    all_domains = set()
    chunks = await read_lines(file_name)
    for chunk in chunks:
        all_domains.update(process_chunk(chunk))
    with open(file_name, "w", encoding="utf8") as f:
        for domain in sorted(all_domains):
            f.write(f"{domain}\n")
    print(f"合并规则数：{len(all_domains)}")

if __name__ == "__main__":
    asyncio.run(main())

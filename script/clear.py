import sys
import asyncio

def filter_parent_domains(domains: set[str]) -> set[str]:
    sorted_domains = sorted(domains, key=lambda d: d[::-1])
    result = []
    for domain in sorted_domains:
        if not result or not domain.endswith("." + result[-1]):
            result.append(domain)
    return set(result)

def sort_by_second_last(domain: str):
    parts = domain.strip().split('.')
    if len(parts) >= 2:
        return (parts[-2], parts[-1], '.'.join(parts[:-2]))
    else:
        return (domain, '', '')

async def read_lines(file_path: str):
    with open(file_path, "r", encoding="utf8") as f:
        while True:
            lines = f.readlines(10000)
            if not lines:
                break
            yield lines

def process_chunk(chunk: list[str]) -> set[str]:
    return set(line.strip() for line in chunk if line.strip())

async def main():
    if len(sys.argv) < 2:
        print("请提供输入文件路径作为参数")
        return
    file_name = sys.argv[1]
    all_domains = set()
    async for chunk in read_lines(file_name):
        all_domains.update(process_chunk(chunk))
    filtered_domains = filter_parent_domains(all_domains)
    sorted_domains = sorted(filtered_domains, key=sort_by_second_last)
    with open(file_name, "w", encoding="utf8") as f:
        for domain in sorted_domains:
            f.write(f"{domain}\n")
    print(f"💰去重完成，最终规则数：{len(filtered_domains)}")

if __name__ == "__main__":
    asyncio.run(main())
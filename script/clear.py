import sys
import asyncio

# 常用及规范的顶级域名（TLD）集合
COMMON_TLDS = {
    # 通用TLD
    "com", "org", "net", "edu", "gov", "mil", "int", "biz", "info", "name", "pro", "coop", "aero", "museum", "idv", "xyz", "top", "site", "online", "club", "shop", "app", "io", "dev", "art", "inc", "vip", "store", "tech", "blog", "wiki", "link", "live", "news", "run", "fun", "cloud", "one", "world", "group", "life", "today", "agency", "company", "center", "team", "email", "solutions", "network", "systems", "media", "digital", "works", "design", "finance", "plus", "studio",
    # 国家和地区TLD
    "cn", "us", "uk", "jp", "de", "fr", "ru", "au", "ca", "br", "it", "es", "nl", "se", "ch", "no", "fi", "be", "at", "dk", "pl", "hk", "tw", "kr", "in", "sg", "cz", "il", "ie", "tr", "za", "mx", "cl", "ar", "nz", "gr", "hu", "pt", "ro", "bg", "sk", "si", "lt", "lv", "ee", "hr", "rs", "ua", "by", "kz", "ge", "md", "ba", "al", "me", "is", "lu", "li", "mt", "cy", "mc", "sm", "ad", "va",
    # 多级TLD（中国及部分国家）
    "com.cn", "net.cn", "gov.cn", "org.cn", "edu.cn", "ac.cn", "bj.cn", "sh.cn", "tj.cn", "cq.cn", "he.cn", "nm.cn", "ln.cn", "jl.cn", "hl.cn", "js.cn", "zj.cn", "ah.cn", "fj.cn", "jx.cn", "sd.cn", "ha.cn", "hb.cn", "hn.cn", "gd.cn", "gx.cn", "hi.cn", "sc.cn", "gz.cn", "yn.cn", "xz.cn", "sn.cn", "gs.cn", "qh.cn", "nx.cn", "xj.cn",
    # 英联邦/其他常用多级TLD
    "co.uk", "org.uk", "gov.uk", "ac.uk", "sch.uk",
    "com.au", "net.au", "org.au", "edu.au", "gov.au", "asn.au", "id.au",
    "co.jp", "ne.jp", "or.jp", "go.jp", "ac.jp", "ed.jp", "gr.jp", "lg.jp",
    "com.hk", "net.hk", "org.hk", "idv.hk", "gov.hk", "edu.hk",
    "co.nz", "ac.nz", "geek.nz", "maori.nz", "net.nz", "org.nz", "school.nz", "govt.nz",
    # 国际化域名TLD（IDN）
    "xn--fiqs8s", "xn--fiqz9s", "xn--55qx5d", "xn--io0a7i",
}

def extract_full_tld(parts):
    """
    从域名分段中，提取最长匹配的顶级域名（支持多级TLD）。
    :param parts: 域名分段列表
    :return: (主域部分, 完整TLD)
    """
    for i in range(4, 0, -1):
        if len(parts) >= i:
            tld = ".".join(parts[-i:]).lower()
            if tld in COMMON_TLDS:
                return parts[:-i], tld
    return parts[:-1], parts[-1].lower() if parts else ""

def sort_key_ignore_tld(domain: str):
    """
    域名排序关键字生成函数，排序时忽略完整TLD，只按主域和子域排序，TLD仅在主域完全相同时才参与排序。
    """
    parts = domain.strip().split('.')
    if not parts or not any(parts):
        return ("", "", "", 0)
    rest, tld = extract_full_tld(parts)
    max_rest_len = 3
    rest_parts = list(rest[::-1])
    while len(rest_parts) < max_rest_len:
        rest_parts.append('')
    return (*rest_parts[:max_rest_len], tld, len(parts))

def process_chunk(chunk: list[str]) -> set[str]:
    """
    处理读取到的每个块，去除空行及空白字符，并转为小写集合去重。
    """
    return set(line.strip().lower() for line in chunk if line.strip())

def normalize_domain(domain: str):
    """
    规范化域名，移除多余点号和空白，全部小写。
    """
    return domain.strip().strip('.').lower()

def filter_parent_domains_fast(domains: set[str]) -> set[str]:
    """
    高效父域名去重逻辑：保留最长的子域，去除其所有祖先域名。
    采用Trie结构，O(N*L)。
    """
    class TrieNode:
        __slots__ = ['children', 'is_end']
        def __init__(self):
            self.children = dict()
            self.is_end = False

    root = TrieNode()
    domains_sorted = sorted(domains, key=lambda d: (-len(d), d))  # 长的在前
    result = set()

    for domain in domains_sorted:
        parts = domain.split('.')
        node = root
        new_branch = False
        # 逆序插入Trie，顶级域在根
        for part in reversed(parts):
            if part not in node.children:
                node.children[part] = TrieNode()
                new_branch = True
            node = node.children[part]
            # 如果某祖先已标记为end，当前域名是其子域，应跳过
            if node.is_end:
                new_branch = False
                break
        if new_branch:
            node.is_end = True
            result.add(domain)
    return result

async def read_lines(file_path: str, chunk_size: int = 100000):
    """
    分块异步读取文件，节省内存，提高大文件处理效率。
    """
    try:
        with open(file_path, "r", encoding="utf8") as f:
            while True:
                lines = f.readlines(chunk_size)
                if not lines:
                    break
                yield lines
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return

async def main():
    """
    主程序入口，完成文件读取、去重、父域名过滤、排序和写回，确保健壮性和高效性。
    """
    try:
        if len(sys.argv) < 2:
            print("请提供输入文件路径作为参数")
            return
        file_name = sys.argv[1]
        all_domains = set()
        async for chunk in read_lines(file_name):
            all_domains.update(process_chunk(chunk))
        if not all_domains:
            print("文件为空或读取失败。")
            return
        # 二次规范化，彻底移除重复点号等异常
        all_domains = set(normalize_domain(d) for d in all_domains if d)
        # 高效父域名去重
        filtered_domains = filter_parent_domains_fast(all_domains)
        sorted_domains = sorted(filtered_domains, key=sort_key_ignore_tld)
        try:
            with open(file_name, "w", encoding="utf8") as f:
                for domain in sorted_domains:
                    f.write(f"{domain}\n")
            print(f"💰去重完成，最终规则数：{len(filtered_domains)}")
        except Exception as e:
            print(f"写入文件时出错: {e}")
    except Exception as e:
        print("处理过程中发生错误：")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

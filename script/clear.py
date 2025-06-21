import sys
import asyncio

# 常用及规范的顶级域名（TLD）集合，包含常见单级和多级TLD，部分IDN编码TLD
# 如需更全TLD可从 https://publicsuffix.org/list/public_suffix_list.dat 动态加载
COMMON_TLDS = {
    # 通用顶级域
    "com", "org", "net", "edu", "gov", "mil", "int", "biz", "info", "name", "pro", "coop", "aero", "museum", "idv", "xyz", "top", "site", "online", "club", "shop", "app", "io", "dev", "art", "inc", "vip", "store", "tech", "blog", "wiki", "link", "live", "news", "run", "fun", "cloud", "one", "world", "group", "life", "today", "agency", "company", "center", "team", "email", "solutions", "network", "systems", "media", "digital", "works", "design", "finance", "plus", "studio",
    # 国家和地区顶级域
    "cn", "us", "uk", "jp", "de", "fr", "ru", "au", "ca", "br", "it", "es", "nl", "se", "ch", "no", "fi", "be", "at", "dk", "pl", "hk", "tw", "kr", "in", "sg", "cz", "il", "ie", "tr", "za", "mx", "cl", "ar", "nz", "gr", "hu", "pt", "ro", "bg", "sk", "si", "lt", "lv", "ee", "hr", "rs", "ua", "by", "kz", "ge", "md", "ba", "al", "me", "is", "lu", "li", "mt", "cy", "mc", "sm", "ad", "va",
    # 常见多级TLD（中国及部分国家）
    "com.cn", "net.cn", "gov.cn", "org.cn", "edu.cn", "ac.cn", "bj.cn", "sh.cn", "tj.cn", "cq.cn", "he.cn", "nm.cn", "ln.cn", "jl.cn", "hl.cn", "js.cn", "zj.cn", "ah.cn", "fj.cn", "jx.cn", "sd.cn", "ha.cn", "hb.cn", "hn.cn", "gd.cn", "gx.cn", "hi.cn", "sc.cn", "gz.cn", "yn.cn", "xz.cn", "sn.cn", "gs.cn", "qh.cn", "nx.cn", "xj.cn",
    # 国际化域名TLD（IDN）
    "xn--fiqs8s", "xn--fiqz9s", "xn--55qx5d", "xn--io0a7i",
    # 英联邦常用TLD
    "co.uk", "org.uk", "gov.uk", "ac.uk", "sch.uk",
    # 澳大利亚
    "com.au", "net.au", "org.au", "edu.au", "gov.au", "asn.au", "id.au",
    # 加拿大
    "ca",
    # 新西兰
    "co.nz", "ac.nz", "geek.nz", "maori.nz", "net.nz", "org.nz", "school.nz", "govt.nz", "parliament.nz", "cri.nz", "health.nz", "iwi.nz", "kiwi.nz", "mil.nz",
    # 其他常见多级TLD
    "co.jp", "ne.jp", "or.jp", "go.jp", "ac.jp", "ed.jp", "gr.jp", "lg.jp",
    "com.hk", "net.hk", "org.hk", "idv.hk", "gov.hk", "edu.hk"
}

def filter_parent_domains(domains: set[str]) -> set[str]:
    """
    过滤掉属于父域名的子域名，只保留最顶层的域名。
    例如，保留 a.com，过滤掉 b.a.com。
    :param domains: 域名集合
    :return: 筛选后的域名集合
    """
    sorted_domains = sorted(domains, key=lambda d: d[::-1])
    result = []
    for domain in sorted_domains:
        if not result or not domain.endswith("." + result[-1]):
            result.append(domain)
    return set(result)

def extract_full_tld(parts):
    """
    从域名分段中，提取最长匹配的顶级域名（支持多级TLD）。
    :param parts: 域名分段列表
    :return: (主域部分, 完整TLD)
    """
    # 最多支持4级TLD（如 gov.uk, com.cn, co.jp, 但不会超出此范围）
    for i in range(4, 0, -1):
        if len(parts) >= i:
            tld = ".".join(parts[-i:]).lower()
            if tld in COMMON_TLDS:
                return parts[:-i], tld
    # 未匹配到则最后一级作为TLD
    return parts[:-1], parts[-1].lower() if parts else ""

def sort_key_ignore_tld(domain: str):
    """
    域名排序关键字生成函数，排序时忽略完整TLD，只按主域和子域排序，TLD仅在主域完全相同时才参与排序。
    :param domain: 域名字符串
    :return: 排序所用的元组（保证长度一致，避免TypeError）
    """
    parts = domain.strip().split('.')
    if not parts or not any(parts):
        # 保证返回四元组
        return ("", "", "", 0)
    rest, tld = extract_full_tld(parts)
    # 保证返回长度一致的元组（主域、次主域、子域、TLD、总长度）
    max_rest_len = 3  # 最多保留3级子域
    rest_parts = list(rest[::-1])
    while len(rest_parts) < max_rest_len:
        rest_parts.append('')
    return (*rest_parts[:max_rest_len], tld, len(parts))

async def read_lines(file_path: str, chunk_size: int = 10000):
    """
    异步分块读取文件，节省内存，提高大文件处理效率。
    :param file_path: 文件路径
    :param chunk_size: 每次读取的最大字符数
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

def process_chunk(chunk: list[str]) -> set[str]:
    """
    处理读取到的每个块，去除空行及空白字符，并转为集合去重。
    :param chunk: 行列表
    :return: 去重后的域名集合
    """
    return set(line.strip() for line in chunk if line.strip())

async def main():
    """
    主程序入口，依次完成文件读取、去重、父域名过滤、规范排序及结果写回。
    避免所有常见错误，遇到异常时友好提示。
    """
    try:
        if len(sys.argv) < 2:
            print("请提供输入文件路径作为参数")
            return
        file_name = sys.argv[1]
        all_domains = set()
        # 读取文件并去重
        async for chunk in read_lines(file_name):
            all_domains.update(process_chunk(chunk))
        if not all_domains:
            print("文件为空或读取失败。")
            return
        # 过滤父域名
        filtered_domains = filter_parent_domains(all_domains)
        # 排序，忽略完整TLD
        sorted_domains = sorted(filtered_domains, key=sort_key_ignore_tld)
        # 写回文件（覆盖原文件）
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

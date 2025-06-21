import sys
import time

# ==============================
# 日志模块
# ==============================
def log_event(event: str, major=False):
    """
    简单日志：输出事件和当前时间
    :param event: 事件内容
    :param major: 是否大事件（决定是否加前缀）
    """
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    if major:
        print(f"[{now}] [重要] {event}")
    else:
        print(f"[{now}] {event}")

# ==============================
# 黑名单配置
# ==============================
REMOVE_END = {"."}  # 结尾黑名单
REMOVE_KEYWORD = {
    "payload:", "rules:", "regexp", "IP-CIDR,", "DOMAIN-KEYWORD,", "PROCESS-NAME,",
    "IP-SUFFIX,", "GEOIP,", "GEOSITE,",
    "#", "*", "!", "/", "【", "】", "[", "]", "$"
}

# ==============================
# 工具函数
# ==============================
def clean_line(line: str) -> str:
    """
    清理行无效字符
    """
    for ch in " \"'|^":
        line = line.replace(ch, "")
    return line

def is_remove_keyword(line: str) -> bool:
    """
    判断行是否含有黑名单关键词
    """
    return any(keyword in line for keyword in REMOVE_KEYWORD)

def is_remove_end(domain: str) -> bool:
    """
    判断域名是否以黑名单结尾
    """
    return any(domain.endswith(suffix) for suffix in REMOVE_END)

def prefilter_line(line: str) -> bool:
    """
    预过滤无效行
    """
    if is_remove_keyword(line):
        return False
    if "@@" in line:
        return False
    return True

def extract_domain(line: str):
    """
    提取域名，支持多种前缀
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
    domain = domain.strip(".")
    if not domain or "." not in domain:
        return None
    return domain

def process_lines_fast(lines):
    """
    处理所有行（加速版，不做排序和去重，仅按出现顺序输出）
    :param lines: 读入的所有行
    :return: 域名生成器
    """
    for line in lines:
        if not prefilter_line(line):
            continue
        domain = extract_domain(line)
        if not domain:
            continue
        if is_remove_end(domain):
            continue
        yield domain

# ==============================
# 主函数
# ==============================
def main():
    # 参数检查
    if len(sys.argv) < 2:
        print("请提供输入文件路径作为参数")
        return

    file_name = sys.argv[1]
    log_event(f"开始处理文件: {file_name}", major=True)

    # 快速读取全部文件
    try:
        with open(file_name, "r", encoding="utf8") as f:
            lines = f.readlines()
        log_event("文件读取完毕")
    except Exception as e:
        log_event(f"文件读取失败: {e}", major=True)
        return

    # 快速处理并写回
    try:
        with open(file_name, "w", encoding="utf8") as f:
            count = 0
            for domain in process_lines_fast(lines):
                f.write(f"{domain}\n")
                count += 1
        log_event(f"域名输出完毕，共写入{count}条", major=True)
    except Exception as e:
        log_event(f"文件写入失败: {e}", major=True)
        return

    log_event("脚本处理完成", major=True)

if __name__ == "__main__":
    main()

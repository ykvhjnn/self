import sys
import time

# ========== 黑名单配置部分 ==========

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
    # 可添加
}

# 匹配域名黑名单
REMOVE_DOMAIN = {
    # 可添加
}

# 匹配域名白名单（新增：ADD_DOMAIN，强制保留/添加）
ADD_DOMAIN = {
    # 可添加
}

# ========== 工具函数 ==========

def log(event: str, major: bool = False):
    """
    简化日志输出
    :param event: 日志内容
    :param major: 是否为重要事件（重要事件加强显示）
    """
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    if major:
        print(f"[{now}] [重要] {event}")
    else:
        print(f"[{now}] {event}")

def is_remove_end(domain: str) -> bool:
    """
    检查域名是否以指定结尾的黑名单后缀结尾
    """
    for suffix in REMOVE_END:
        if domain.endswith(suffix):
            return True
    return False

def is_remove_keyword(line: str) -> bool:
    """
    检查行是否包含黑名单关键词
    """
    for keyword in REMOVE_KEYWORD:
        if keyword in line:
            return True
    return False

def is_remove_domain(domain: str) -> bool:
    """
    检查是否为黑名单域名
    """
    return domain in REMOVE_DOMAIN

def is_add_domain(domain: str) -> bool:
    """
    检查是否为白名单强制添加域名
    """
    return domain in ADD_DOMAIN

# ========== 主处理流程 ==========

def process_file(file_name: str):
    """
    处理文件，去除黑名单内容，添加白名单内容
    """
    log(f"开始处理文件：{file_name}", major=True)

    # 用集合加速查找与去重
    result_set = set()
    add_set = set(ADD_DOMAIN)  # 需要额外添加的域名集
    
    # 读取文件内容并处理
    with open(file_name, "r", encoding="utf8") as f:
        lines = (line.rstrip("\n") for line in f)
        for line in lines:
            if not line or line.startswith("#"):
                continue  # 跳过空行和注释
            # 白名单优先，强制保留
            if is_add_domain(line):
                result_set.add(line)
                continue
            if is_remove_keyword(line):
                continue
            if is_remove_end(line):
                continue
            if is_remove_domain(line):
                continue
            result_set.add(line)
    
    # 合并白名单，确保 ADD_DOMAIN 中每个都在
    result_set.update(add_set)

    # 写回新文件
    with open(file_name, "w", encoding="utf8") as f:
        for domain in sorted(result_set):
            f.write(f"{domain}\n")

    log(f"处理完成，保留的规则总数为：{len(result_set)}", major=True)

def main():
    """
    主入口，参数校验与调用处理
    """
    if len(sys.argv) < 2:
        print("请提供输入文件路径作为参数")
        return
    process_file(sys.argv[1])

if __name__ == "__main__":
    main()

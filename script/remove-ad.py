#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本功能说明：
- 用于过滤输入列表中的不需要的行（如广告/无用域名）
- 支持三种黑名单规则过滤：域名、关键词、结尾
- 支持可选白名单规则添加
- 日志简洁明了，突出关键流程，弱化细节
- 分模块设计，结构清晰，适合新手理解和维护
"""

import sys
import time
from typing import List, Set

# ========================== 配置区 ==========================
# 黑名单：完全匹配或结尾匹配的域名
REMOVE_DOMAIN = set([
    # 例如： 'example.com', 'ads.example.org'
])

# 黑名单：包含关键词
REMOVE_KEYWORD = set([
    # 例如： 'adserver', 'track'
])

# 黑名单：以这些结尾的行
REMOVE_END = set([
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
])

# 白名单（可选）：这些域名会被加回去
ADD_DOMAIN = set([
    # 例如： 'allow.example.com'
])

# ========================== 日志模块 ==========================
def log(event: str, major: bool = False):
    """
    日志输出，包含时间戳。
    major=True 为关键流程，大写前缀，其他为简洁弱化显示。
    """
    prefix = "[{}]".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    if major:
        print(f"{prefix} [!]{event}")
    else:
        print(f"{prefix} - {event}")

# ========================== 黑名单过滤工具 ==========================
def match_domain(line: str, domains: Set[str]) -> bool:
    """
    判断行是否完全等于或以黑名单域名结尾
    """
    if not domains: return False
    s = line.strip()
    return s in domains or any(s.endswith(f".{d}") or s.endswith(d) for d in domains)

def match_keyword(line: str, keywords: Set[str]) -> bool:
    """
    判断行是否包含黑名单关键词
    """
    if not keywords: return False
    s = line.strip()
    return any(k in s for k in keywords)

def match_end(line: str, ends: Set[str]) -> bool:
    """
    判断行是否以黑名单结尾
    """
    if not ends: return False
    s = line.strip()
    return any(s.endswith(e) for e in ends)

def need_add(line: str, add_domains: Set[str]) -> bool:
    """
    判断行是否为需要加回的白名单域名
    """
    if not add_domains: return False
    s = line.strip()
    return s in add_domains or any(s.endswith(d) for d in add_domains)

# ========================== 主处理流程 ==========================
def filter_lines(lines: List[str]) -> List[str]:
    """
    过滤输入行：黑名单过滤，白名单加回
    返回过滤后新列表
    """
    filtered = []
    seen = set()

    log("过滤开始", major=True)
    for line in lines:
        s = line.strip()
        if not s or s in seen:
            continue
        if match_domain(s, REMOVE_DOMAIN):
            continue
        if match_keyword(s, REMOVE_KEYWORD):
            continue
        if match_end(s, REMOVE_END):
            continue
        filtered.append(s)
        seen.add(s)
    log(f"黑名单过滤完成，剩{len(filtered)}行", major=True)

    # 白名单加回
    if ADD_DOMAIN:
        add_set = ADD_DOMAIN - set(filtered)
        if add_set:
            filtered += sorted(add_set)
            log(f"白名单加回{len(add_set)}行", major=True)
    return filtered

# ========================== 主入口 ==========================
def main():
    """
    主程序入口，命令行参数读取文件，处理并输出结果
    """
    if len(sys.argv) < 2:
        print(f"用法: python {sys.argv[0]} <输入文件> [输出文件]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        log(f"读取输入文件，共{len(lines)}行")
    except Exception as e:
        log(f"读取文件失败:{e}", major=True)
        sys.exit(1)

    result = filter_lines(lines)

    # 输出
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for line in result:
                    f.write(line + "\n")
            log(f"已写入输出文件({output_file})", major=True)
        except Exception as e:
            log(f"写入文件失败:{e}", major=True)
            sys.exit(1)
    else:
        for line in result:
            print(line)
    log("处理完成", major=True)

# ========================== 程序入口 ==========================
if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本功能：
- 根据黑名单规则（域名、关键词、结尾）过滤输入列表
- 支持添加新域名白名单规则，并在去除黑名单后再添加
- 优化处理速度：只处理必要的行，返回过滤后新列表
- 支持规则为空的情况，避免误删
- 日志记录：时间+简要事件，突出主要流程
- 代码结构：模块化、注释规范、便于维护和理解
"""

import sys
import re
import time
from typing import List, Set

# ========================== 配置区域 ==========================
# 黑名单规则
REMOVE_DOMAIN = set([
])

REMOVE_KEYWORD = set([
])

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

# 新增白名单规则（去除黑名单后再添加）
ADD_DOMAIN = set([
])

# ========================== 日志工具 ==========================
def log(event: str, major: bool = False):
    """
    日志输出，包含时间戳。大事件高亮显示。
    """
    prefix = "[{}]".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    if major:
        print(f"{prefix} [重要] {event}")
    else:
        print(f"{prefix} {event}")

# ========================== 规则检查工具 ==========================
def is_match_domain(line: str, domains: Set[str]) -> bool:
    """
    判断一行是否包含黑名单域名（完全匹配或以域名为结尾）。
    支持列表为空。
    """
    if not domains:
        return False
    return any(line.strip().endswith(domain) or line.strip() == domain for domain in domains)

def is_match_keyword(line: str, keywords: Set[str]) -> bool:
    """
    判断一行是否包含黑名单关键词。
    支持列表为空。
    """
    if not keywords:
        return False
    return any(keyword in line for keyword in keywords)

def is_match_end(line: str, ends: Set[str]) -> bool:
    """
    判断一行是否以黑名单结尾。
    支持列表为空。
    """
    if not ends:
        return False
    return any(line.strip().endswith(ending) for ending in ends)

def is_add_domain(line: str, add_domains: Set[str]) -> bool:
    """
    判断一行是否为需要添加的白名单域名。
    支持列表为空。
    """
    if not add_domains:
        return False
    return any(line.strip().endswith(domain) or line.strip() == domain for domain in add_domains)

# ========================== 主处理函数 ==========================
def filter_lines(lines: List[str]) -> List[str]:
    """
    过滤输入行，去除黑名单，添加白名单。
    返回过滤后新列表。
    """
    filtered = []
    add_lines = set()

    log("开始过滤黑名单...", major=True)

    for line in lines:
        line_strip = line.strip()
        # 跳过空行
        if not line_strip:
            continue
        # 域名黑名单过滤
        if is_match_domain(line_strip, REMOVE_DOMAIN):
            continue
        # 关键词黑名单过滤
        if is_match_keyword(line_strip, REMOVE_KEYWORD):
            continue
        # 结尾黑名单过滤
        if is_match_end(line_strip, REMOVE_END):
            continue
        filtered.append(line_strip)

    log(f"黑名单过滤完成，剩余 {len(filtered)} 行。", major=True)

    # 添加白名单
    if ADD_DOMAIN:
        log("开始添加白名单...", major=True)
        # 只添加不在filtered中的ADD_DOMAIN
        existing = set(filtered)
        for add_domain in ADD_DOMAIN:
            if add_domain not in existing:
                add_lines.add(add_domain)
        filtered.extend(sorted(add_lines))
        log(f"添加白名单完成，总计 {len(filtered)} 行。", major=True)

    return filtered

# ========================== 主执行入口 ==========================
def main():
    """
    主程序入口，读取输入文件，处理并输出过滤结果。
    """
    if len(sys.argv) < 2:
        print(f"用法: python {sys.argv[0]} <输入文件> [输出文件]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        log(f"读取输入文件 {input_file}，共 {len(lines)} 行。", major=True)
    except Exception as e:
        log(f"读取文件失败: {e}", major=True)
        sys.exit(1)

    # 过滤处理
    result = filter_lines(lines)

    # 输出结果
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for line in result:
                    f.write(line + "\n")
            log(f"已写入输出文件 {output_file}。", major=True)
        except Exception as e:
            log(f"写入输出文件失败: {e}", major=True)
            sys.exit(1)
    else:
        # 控制台输出
        for line in result:
            print(line)

    log("处理完成。", major=True)

# ========================== 程序入口 ==========================
if __name__ == "__main__":
    main()

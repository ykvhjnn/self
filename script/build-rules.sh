#!/bin/bash
# ============================================================================
# 通用规则生成脚本，支持多种规则类型（如 Proxy、Directfix、Ad、自定义等）
# 用法示例：bash build-rules.sh Proxy|Directfix|Ad|自定义组名
# ============================================================================

set -euo pipefail   # 严格模式：遇到错误立即退出，变量未定义即报错

# ----------------------------------------------------------------------------
# 【步骤1】函数：错误输出并退出
# ----------------------------------------------------------------------------
function error_exit() {
    echo "[ERROR] $1" >&2
    exit 1
}

# ----------------------------------------------------------------------------
# 【步骤2】进入脚本目录，确保相对路径有效
# ----------------------------------------------------------------------------
cd "$(cd "$(dirname "$0")"; pwd)" || error_exit "无法进入脚本目录"

# ----------------------------------------------------------------------------
# 【步骤3】（已移除，原为检查输入参数，必须指定规则类型）
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# 【步骤4】定义全部规则源组（可自定义添加新组，组名为key，规则url为value，多行可加）
# ----------------------------------------------------------------------------
declare -A urls_map

# 预置Proxy组
urls_map["Proxy"]="
https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/tld-proxy.list
https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/proxy.list
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Global/Global_Domain_For_Clash.txt
https://raw.githubusercontent.com/peasoft/NoMoreWalls/refs/heads/master/snippets/region.yml
https://raw.githubusercontent.com/ykvhjnn/mihomo-rule/refs/heads/main/self/Proxy-fix.yaml
"

# 预置Directfix组
urls_map["Directfix"]="
https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/private.list
https://raw.githubusercontent.com/ykvhjnn/mihomo-rule/refs/heads/main/self/Direct-fix.yaml
"

# 预置Ad组
urls_map["Ad"]="
https://raw.githubusercontent.com/ghvjjjj/adblockfilters/refs/heads/main/rules/adblockdomain.txt
https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdnslite.txt
https://raw.githubusercontent.com/Cats-Team/AdRules/main/dns.txt
https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt
https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-adguard.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.xiaomi.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.oppo-realme.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.vivo.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.roku.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.lgwebos.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.tiktok.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.winoffice.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt
https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.huawei.txt
https://raw.githubusercontent.com/ykvhjnn/mihomo-rule/refs/heads/main/self/Ad-fix.yaml
"

# ----------------------------------------------------------------------------
# 【步骤5】每组类型对应的 Python 处理脚本（需与组名一一对应，扩展需同步添加）
# ----------------------------------------------------------------------------
declare -A py_scripts
py_scripts["Proxy"]="sort.py remove-proxy.py clear.py"
py_scripts["Directfix"]="sort.py clear.py"
py_scripts["Ad"]="sort.py remove-ad.py clear.py"

# ----------------------------------------------------------------------------
# 【步骤6】参数校验，组名需在定义的urls_map中
# ----------------------------------------------------------------------------
group="$1"
if [[ -z "${urls_map[$group]:-}" ]]; then
    echo "[ERROR] 未找到组: $group"
    echo "可用组有:"
    for k in "${!urls_map[@]}"; do
        echo "  - $k"
    done
    exit 1
fi

# ----------------------------------------------------------------------------
# 【步骤7】定义所有相关文件名变量
# ----------------------------------------------------------------------------
domain_file="${group}_domain.txt"
tmp_file="${group}_tmp.txt"
mihomo_txt_file="${group}_Mihomo.txt"
mihomo_mrs_file="${mihomo_txt_file%.txt}.mrs"

# ----------------------------------------------------------------------------
# 【步骤8】下载 Mihomo 工具，确保每步都检查结果
# ----------------------------------------------------------------------------
function download_mihomo() {
    wget -q https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/version.txt \
        || error_exit "下载 Mihomo 版本文件失败"
    version=$(cat version.txt)
    mihomo_tool="mihomo-linux-amd64-$version"
    wget -q "https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/$mihomo_tool.gz" \
        || error_exit "下载 Mihomo 工具失败"
    gzip -d "$mihomo_tool.gz" || error_exit "解压 Mihomo 工具失败"
    chmod +x "$mihomo_tool" || error_exit "赋予 Mihomo 工具可执行权限失败"
}
download_mihomo

# ----------------------------------------------------------------------------
# 【步骤9】清空旧临时文件，避免数据混杂
# ----------------------------------------------------------------------------
> "$domain_file"
> "$tmp_file"

# ----------------------------------------------------------------------------
# 【步骤10】批量下载规则源，全部合并到临时文件
# 检查每个URL下载状态，失败只警告不中断
# ----------------------------------------------------------------------------
echo "开始下载规则源列表..."
while read -r url; do
    if [[ -z "$url" ]]; then
        continue
    fi
    echo "拉取: $url"
    if ! curl --http2 --compressed --max-time 30 --retry 3 -sSL "$url" >> "$tmp_file"; then
        echo "[WARN] 拉取失败: $url" >&2
    fi
done <<< "${urls_map[$group]}"
echo "规则源全部下载完毕"

# ----------------------------------------------------------------------------
# 【步骤11】合并临时文件到主文件并处理换行符，清理临时文件
# ----------------------------------------------------------------------------
cat "$tmp_file" >> "$domain_file"
rm -f "$tmp_file"
sed -i 's/\r//' "$domain_file"

# ----------------------------------------------------------------------------
# 【步骤12】依次执行类型对应的 Python 清洗脚本，任何一步出错即中止
# ----------------------------------------------------------------------------
for py in ${py_scripts[$group]}; do
    if [[ ! -f "$py" ]]; then
        error_exit "找不到 Python 脚本: $py"
    fi
    echo "执行清洗脚本: $py"
    if ! python "$py" "$domain_file"; then
        error_exit "Python 脚本 $py 执行失败"
    fi
done

# ----------------------------------------------------------------------------
# 【步骤13】统计最终规则数量，排除空行或注释，输出信息
# ----------------------------------------------------------------------------
rule_count=$(grep -vE '^\s*$|^#' "$domain_file" | wc -l)
echo "生成规则名称: $mihomo_txt_file, $mihomo_mrs_file"
echo "生成文件 $mihomo_txt_file 规则总数: $rule_count"

# ----------------------------------------------------------------------------
# 【步骤14】格式化输出，所有域名加前缀 +.
# ----------------------------------------------------------------------------
sed "s/^/\\+\\./g" "$domain_file" > "$mihomo_txt_file"

# ----------------------------------------------------------------------------
# 【步骤15】调用 Mihomo 工具转换为mrs格式，转换失败立即中止
# ----------------------------------------------------------------------------
if ! ./"$mihomo_tool" convert-ruleset domain text "$mihomo_txt_file" "$mihomo_mrs_file"; then
    error_exit "Mihomo 工具转换 $mihomo_txt_file 失败"
fi

# ----------------------------------------------------------------------------
# 【步骤16】整理输出文件夹，并清理所有生成的中间文件
# ----------------------------------------------------------------------------
mkdir -p ../txt
mv "$mihomo_txt_file" "../txt/$mihomo_txt_file"
mv "$mihomo_mrs_file" "../$mihomo_mrs_file"
rm -rf ./*.txt "$mihomo_tool" version.txt

echo "已完成 $group 规则生成并清理临时文件"

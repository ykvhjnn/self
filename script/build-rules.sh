#!/bin/bash
# =====================================================================
# 通用规则生成脚本（支持 Proxy / Directfix / Ad）
# 用法: bash build-rules.sh [Proxy|Directfix|Ad]
# =====================================================================

# ==================== 1. 进入脚本目录 ====================
cd "$(cd "$(dirname "$0")"; pwd)"

# ==================== 2. 解析参数 ====================
type=${1:-Proxy}
case $type in
  Proxy|Directfix|Ad) ;;
  *) echo "[ERROR] 参数错误，请指定规则类型: Proxy、Directfix、Ad"; exit 1 ;;
esac

# ==================== 3. 变量定义 ====================
name="$type"
domain_file="${name}_domain.txt"
tmp_file="${name}_tmp.txt"
mihomo_txt_file="${name}_Mihomo.txt"
mihomo_mrs_file="${mihomo_txt_file%.txt}.mrs"

# 规则源配置
declare -A rule_urls
rule_urls[Proxy]="
https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/tld-proxy.list
https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/proxy.list
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Global/Global_Domain_For_Clash.txt
https://raw.githubusercontent.com/peasoft/NoMoreWalls/refs/heads/master/snippets/region.yml
https://raw.githubusercontent.com/ykvhjnn/mihomo-rule/refs/heads/main/self/Proxy-fix.yaml
"
rule_urls[Directfix]="
https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/private.list
https://raw.githubusercontent.com/ykvhjnn/mihomo-rule/refs/heads/main/self/Direct-fix.yaml
"
rule_urls[Ad]="
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

# 类型对应的 Python 特殊处理脚本
declare -A python_post
python_post[Proxy]="python remove-proxy.py"
python_post[Directfix]=""
python_post[Ad]="python remove-ad.py"

# ==================== 4. 准备 Mihomo 工具 ====================
echo "[1/7] 正在准备 Mihomo 工具..."
wget -q https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/version.txt || { echo "[ERROR] 下载版本文件失败"; exit 1; }
version=$(cat version.txt)
mihomo_tool="mihomo-linux-amd64-$version"
wget -q "https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/$mihomo_tool.gz" || { echo "[ERROR] 下载 Mihomo 工具失败"; exit 1; }
gzip -d "$mihomo_tool.gz"
chmod +x "$mihomo_tool"

# ==================== 5. 下载与合并规则源 ====================
echo "[2/7] 清理旧的中间文件..."
> "$domain_file"
> "$tmp_file"

echo "[3/7] 下载 $type 规则源并合并..."
echo "${rule_urls[$type]}" | xargs -n1 -P 8 -I {} bash -c \
  'curl --http2 --compressed --max-time 30 --retry 3 -sSL "{}" >> "'"$tmp_file"'"'

cat "$tmp_file" >> "$domain_file"
rm -f "$tmp_file"
sed -i 's/\r//' "$domain_file" # 统一换行符

# ==================== 6. 规则预处理 ====================
echo "[4/7] 排序、去重、特殊处理..."
python sort.py "$domain_file" || { echo "[ERROR] sort.py 执行失败"; exit 1; }
if [[ -n "${python_post[$type]}" ]]; then
  ${python_post[$type]} "$domain_file" || { echo "[ERROR] ${python_post[$type]} 执行失败"; exit 1; }
fi
python clear.py "$domain_file" || { echo "[ERROR] clear.py 执行失败"; exit 1; }

# ==================== 7. 生成 Mihomo 支持格式 ====================
echo "[5/7] 统计与生成 Mihomo 规则..."
rule_count=$(grep -vE '^\s*$|^#' "$domain_file" | wc -l)
echo "生成规则名称: $mihomo_txt_file, $mihomo_mrs_file"
echo "生成文件 $mihomo_txt_file 规则总数: $rule_count"

sed "s/^/\\+\\./g" "$domain_file" > "$mihomo_txt_file"

./"$mihomo_tool" convert-ruleset domain text "$mihomo_txt_file" "$mihomo_mrs_file" || { echo "[ERROR] Mihomo 工具转换失败"; exit 1; }

# ==================== 8. 文件整理与清理 ====================
echo "[6/7] 移动文件到目标目录..."
mkdir -p ../txt
mv "$mihomo_txt_file" "../txt/$mihomo_txt_file"
mv "$mihomo_mrs_file" "../$mihomo_mrs_file"

echo "[7/7] 清理临时文件..."
rm -rf ./*.txt "$mihomo_tool"

echo "全部完成！已生成 $type 规则并清理临时文件。"

# ==================== END ====================
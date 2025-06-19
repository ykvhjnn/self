#!/bin/bash
# 进入脚本目录
cd $(cd "$(dirname "$0")";pwd)

wget -q https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/version.txt || { echo "[ERROR] 下载版本文件失败"; exit 1; }
version=$(cat version.txt)
mihomo_tool="mihomo-linux-amd64-$version"
wget -q "https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/$mihomo_tool.gz" || { echo "[ERROR] 下载 Mihomo 工具失败"; exit 1; }
gzip -d "$mihomo_tool.gz"
chmod +x "$mihomo_tool"

name="Ad"
domain_file="${name}_domain.txt"
tmp_file="${name}_tmp.txt"
mihomo_txt_file="${name}_Mihomo.txt"
mihomo_mrs_file="${mihomo_txt_file%.txt}.mrs"

# 规则源列表
urls=(
    "https://big.oisd.nl"
    "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"
    "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdnslite.txt"
    "https://raw.githubusercontent.com/Cats-Team/AdRules/main/dns.txt"
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-domains.txt"
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/refs/heads/master/anti-ad-adguard.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.xiaomi.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.oppo-realme.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.vivo.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.roku.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.lgwebos.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.tiktok.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.winoffice.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.huawei.txt"
    "https://raw.githubusercontent.com/ykvhjnn/mihomo-rule/refs/heads/main/self/Ad-fix.yaml"
)

> "$domain_file"
> "$tmp_file"

printf "%s\n" "${urls[@]}" | xargs -P 8 -I {} bash -c \
    'curl --http2 --compressed --max-time 30 --retry 3 -sSL "{}" >> "'"$tmp_file"'"'

cat "$tmp_file" >> "$domain_file"
rm -f "$tmp_file"
sed -i 's/\r//' "$domain_file"

python sort.py "$domain_file" || { echo "[ERROR] Python 脚本执行失败"; exit 1; }
python remove-ad.py "$domain_file" || { echo "[ERROR] Python 脚本执行失败"; exit 1; }
python clear.py "$domain_file" || { echo "[ERROR] Python 脚本执行失败"; exit 1; }

# 统计最终规则数量
rule_count=$(grep -vE '^\s*$|^#' "$domain_file" | wc -l)
echo "生成规则名称: $mihomo_txt_file, $mihomo_mrs_file"
echo "生成文件 $mihomo_txt_file 规则总数: $rule_count"

sed "s/^/\\+\\./g" "$domain_file" > "$mihomo_txt_file"

./"$mihomo_tool" convert-ruleset domain text "$mihomo_txt_file" "$mihomo_mrs_file" || { echo "[ERROR] Mihomo 工具转换失败"; exit 1; }

mkdir -p ../txt
mv "$mihomo_txt_file" "../txt/$mihomo_txt_file"
mv "$mihomo_mrs_file" "../$mihomo_mrs_file"
rm -rf ./*.txt "$mihomo_tool"
echo "已完成并清理临时文件"

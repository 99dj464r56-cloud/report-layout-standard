#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客观可读性检测：图内「裸数字」标注扫描

背景：排版除了「越界/断句/泄露」这类结构性硬错误，还有一类**客观可读性**错误——
数据标注只有数字、没有时点/口径/单位，读者单看图无法理解它指什么（如孤零零的
「82.25」「7.89」「-4,700」）。这类问题不属「审美」，而是可判定、可穷举的客观缺陷。

本脚本扫描一个目录下的所有 SVG，找出「裸数字」标注（纯数字、非年份、非轴刻度）。
柱顶标注、数据点旁有图例/脚注说明的，需人工复核后再定是否修，脚本只做第一道筛查。

用法：
    python3 检测裸数字.py <SVG目录> [排除前缀]

输出：每个文件的裸数字标注清单；无裸数字则 PASS。
"""
import re, sys, os, glob

# 常见轴刻度（不算裸数字）
AXIS = {
    '0', '5', '10', '20', '30', '40', '50', '60', '70', '80', '90',
    '100', '150', '200', '250', '300', '400', '500', '600', '700', '800', '900',
    '1000', '2000', '5000', '10000', '20000', '50000', '100000',
    '0.0', '0.00', '0.50', '1.00', '1.5', '2.0', '2.5', '3.0',
    '-5', '-10', '-25', '25', '5%', '10%', '20%', '30%', '50%', '100%',
    '7.5', '8.0', '8.5', '9.0', '9.5', '10.0', '10.5',
    '8000', '11500', '15000', '18500', '22000', '8,000', '11,500', '15,000', '18,500', '22,000',
    '+1.0', '+0.5', '+0.0', '-0.5', '-1.0',
}

def scan_file(path):
    svg = open(path, encoding='utf-8').read()
    hits = []
    for m in re.finditer(r'<text[^>]*>(.*?)</text>', svg, re.S):
        body = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if not body:
            continue
        b = body.replace(' ', '')
        # 纯数字/符号（数字、逗号、小数点、百分号、正负号）
        if not re.fullmatch(r'[0-9,.,%−\-+\s]+', b):
            continue
        # 排除年份
        if re.search(r'(19|20)\d{2}', b):
            continue
        # 排除轴刻度
        if b in AXIS or body in AXIS:
            continue
        # 排除纯整数大刻度（>=1000 且无小数点）
        hits.append(body)
    return hits

def main(directory, exclude_prefixes=('四层图',)):
    files = sorted(glob.glob(os.path.join(directory, '*.svg')))
    files = [f for f in files if not any(os.path.basename(f).startswith(p) for p in exclude_prefixes)]
    total = 0
    print('===== 图内「裸数字」标注扫描 =====')
    for f in files:
        hits = scan_file(f)
        if hits:
            total += len(hits)
            print(f'[{os.path.basename(f)}] {hits}')
    print('-' * 40)
    if total == 0:
        print('结论：未发现裸数字标注（PASS）。')
    else:
        print(f'结论：{len([f for f in files if scan_file(f)])} 个文件含 {total} 处裸数字，'
              '需人工复核是否柱顶标注/有图例脚注解释，再定是否修。')
    return total

if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    sys.exit(main(d))

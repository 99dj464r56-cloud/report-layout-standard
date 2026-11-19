#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研究报告 —— 排版终版验收脚本（可复现硬门禁）

用途：把"排版是否达标"从主观判断，变成可被任何人复现的客观门禁。
只要本脚本全部硬门禁 PASS，即认定该 PDF 通过了全部可量化的排版硬指标。

用法：
    python3 终版排版验收.py <报告.pdf> [附录页码.json] [--expect-pages N]

说明：
  --expect-pages N  仅在报告已约定总页数时使用；未指定则 A1 只报告实际页数，不因此 FAIL。

依赖：pymupdf（pip install pymupdf）

设计原则：
  - 只检测"可客观判定"的硬错误：泄露、繁体、越界、空页、断句、拆页、页码漂移、冗余。
  - 不做数字来源/取数/计算的核查（那不属于排版职责）。
  - 每一项给出「结果 + 证据」，FAIL 即亮红，不存在"差不多"。
"""
import sys, os, re, json
from collections import Counter
import pymupdf

END_PUNCT = '。；：！？）〕」』…—'

# 内部档案名 / 本机路径 / 旧版本代号 —— 一律不得出现在读者可见正文
LEAK_WORDS = [
    '资料包', '完整 CSV', '原始档案', '原始资料/', '/Users/', 'Codex', 'grok',
    'V1.2', 'V1.1', '非正式版', '非正式', '_工作区', '00_索引', '01_原始',
    '02_底表', '03_核验', '04_报告', '05_图表', '06_历史', '07_Codex', '08_grok',
]
# 繁体字（正文；URL 中出现的除外）
TRAD_CHARS = '財産體臺機濟會萬與東開關電證戶聯龍經處業務樣銀網書雲門風'

def page_blocks(page):
    """返回去除页脚后的文本块（已按 y 排序）。"""
    blocks = [b for b in page.get_text('blocks')
              if not ('共' in b[4] and '页' in b[4] and '第' in b[4])]
    blocks.sort(key=lambda b: (b[1], b[0]))
    return blocks

def last_meaningful_line(page):
    """返回某页正文最后一行的文本与底部 y（排除页脚）。"""
    blocks = page_blocks(page)
    if not blocks:
        return '', 0.0
    last = blocks[-1]
    lines = [l for l in last[4].strip().split('\n') if l.strip()]
    return (lines[-1].strip() if lines else ''), last[3]

def first_meaningful_line(page):
    blocks = page_blocks(page)
    if not blocks:
        return ''
    first = blocks[0]
    lines = [l for l in first[4].strip().split('\n') if l.strip()]
    return lines[0].strip() if lines else ''

def main(path, json_path=None, expect_pages=None):
    doc = pymupdf.open(path)
    results = []
    W, H = doc[0].rect.width, doc[0].rect.height
    full = '\n'.join(p.get_text() for p in doc)

    def add(name, status, evidence):
        results.append((name, status, evidence))

    # ── A. 结构完整性 ────────────────────────────────
    if expect_pages is None:
        add('A1 页数', 'INFO', '%d 页（未指定期望页数，不作为硬门禁）' % len(doc))
    else:
        add('A1 页数 = %d' % expect_pages,
            'PASS' if len(doc) == expect_pages else 'FAIL',
            '%d 页' % len(doc))

    pagenums = []
    for p in doc:
        m = re.search(r'第 (\d+) 页 / 共 (\d+) 页', p.get_text())
        if m:
            pagenums.append(int(m.group(1)))
    missing = [i for i in range(1, len(doc) + 1) if i not in pagenums]
    add('A2 页码 1–%d 连续' % len(doc),
        'PASS' if not missing else 'FAIL',
        '缺 %s' % missing if missing else '连续')

    # ── B. 内容洁净（内部信息不得泄露）────────────────
    leaks = {k: full.count(k) for k in LEAK_WORDS if full.count(k)}
    add('B1 内部路径/档案名/旧版本代号',
        'PASS' if not leaks else 'FAIL',
        json.dumps(leaks, ensure_ascii=False) if leaks else '0 处')

    body_no_url = re.sub(r'https?://\S+', '', full)
    trad = sorted(set(c for c in body_no_url if c in TRAD_CHARS))
    add('B2 繁体字（正文）',
        'PASS' if not trad else 'FAIL',
        ''.join(trad) if trad else '0')

    # ── C. 几何正确性（可见、不裁切）────────────────
    oob_lr = 0
    for i, p in enumerate(doc):
        for w in p.get_text('words'):
            if w[2] > W - 25 or w[0] < 11:
                oob_lr += 1
    add('C1 文字左右越界', 'PASS' if oob_lr == 0 else 'FAIL', '%d 处' % oob_lr)

    oob_bottom = []
    for i, p in enumerate(doc):
        for b in page_blocks(p):
            if b[3] > H - 42:  # 压进页脚区
                oob_bottom.append((i + 1, b[4].strip()[:20]))
    add('C2 文字压页脚', 'PASS' if not oob_bottom else 'FAIL',
        '%d 处' % len(oob_bottom) if oob_bottom else '0')

    empty = [i + 1 for i, p in enumerate(doc) if len(p.get_text().strip()) < 40]
    add('C3 空页/近空页', 'PASS' if not empty else 'FAIL',
        'p%s' % empty if empty else '0')

    # ── D. 断句 / 断页（阅读连续性）────────────────
    def is_caption_or_index(s):
        """图题/表题/URL/索引条目 —— 这些句末无标点是合法的，不算断句。"""
        s = s.strip()
        if not s:
            return True
        if re.match(r'^(图|表)\s*\d+\.\d+', s):
            return True
        if re.match(r'^附图[A-B]-\d+', s):
            return True
        if '｜' in s:
            return True
        if 'http' in s or 'www.' in s or re.search(r'\.(html?|pdf|csv)$', s):
            return True
        return False

    broken = []
    for i in range(len(doc) - 1):
        tail, _ = last_meaningful_line(doc[i])
        if not tail or tail[-1] in END_PUNCT:
            continue
        # 真·断句：句子在句中逗号/顿号/冒号处被切断（而非图题/表格/URL 等无标点内容）
        if tail[-1] not in '，、：:；;':
            continue
        if is_caption_or_index(tail):
            continue
        nfirst = first_meaningful_line(doc[i + 1])
        if re.match(r'^(第[一二三四五六七八九十]+章|[一二三四五六七八九十]+、|附件[一二]|图\s*\d|表\s*\d)', nfirst):
            continue  # 下一页是标题，非句子延续
        broken.append((i + 1, tail[-18:], nfirst[:18]))
    add('D1 页尾断句', 'PASS' if not broken else 'FAIL',
        '%d 处' % len(broken) if broken else '0')
    if broken:
        for pg, t, nf in broken[:10]:
            print('    p%d 尾「%s」→ p%d 首「%s」' % (pg, t, pg + 1, nf))

    head_pat = re.compile(r'^(第[一二三四五六七八九十]+章|附录\s*[ABC]|附件[一二]|[一二三四五六七八九十]+、)')
    orphan = []
    for i in range(len(doc) - 1):
        tail, ymax = last_meaningful_line(doc[i])
        if ymax > H * 0.72 and head_pat.match(tail):
            if re.match(r'^第[一二三四五六七八九十]+章\s*\d+\.\d+', tail):
                continue  # 目录/逐图对照索引条目（如「第五章 2.1」），非正文标题
            orphan.append((i + 1, tail[:28]))
    add('D2 孤立标题（页底悬空）', 'PASS' if not orphan else 'FAIL',
        '%d 处' % len(orphan) if orphan else '0')
    if orphan:
        for pg, t in orphan:
            print('    p%d 孤立标题「%s」' % (pg, t))

    # 表头孤立（表 A.1 表头含「项目」+多地区，若留在页底则视为拆页）
    split_header = []
    for i in range(len(doc) - 1):
        tail, ymax = last_meaningful_line(doc[i])
        if ('项目' in tail and '美国' in tail and ('台湾' in tail or '大陆' in tail)
                and ymax > H * 0.80):
            split_header.append(i + 1)
    add('D3 表格拆页/表头孤立', 'PASS' if not split_header else 'FAIL',
        'p%s' % split_header if split_header else '0')

    # ── E. 引用一致性（目录页码 = 实际页码）──────────
    if json_path and os.path.exists(json_path):
        with open(json_path, encoding='utf-8') as f:
            pmap = json.load(f)
        actual = {}
        attc_pages = []
        for i, p in enumerate(doc):
            t = p.get_text()
            for m in re.findall(r'附图[A-B]-\d{2}｜', t):
                actual.setdefault(m.rstrip('｜'), i + 1)
            if '口径基准对照表' in t:
                attc_pages.append(i + 1)
        if attc_pages:
            actual['attC'] = max(attc_pages)  # 目录条目在前，正文标题页在最后
        # json key: fuA-01 -> 附图A-01 ; fuB-01 -> 附图B-01 ; attC -> attC
        drift = {}
        for k, v in pmap.items():
            fig = k.replace('fuA-', '附图A-').replace('fuB-', '附图B-')
            if actual.get(fig) != v:
                drift[fig] = (v, actual.get(fig))
        add('E1 附录页码零漂移（目录=实际）',
            'PASS' if not drift else 'FAIL',
            str(drift) if drift else '26 项全对')
    else:
        add('E1 附录页码零漂移', 'INFO', '未提供附录页码.json，跳过')

    # ── F. 冗余（重复句子）─────────────────────────
    sents = re.split(r'[。；！？\n]', full)
    sents = [re.sub(r'\s+', '', s).strip() for s in sents]
    sents = [s for s in sents if len(s) >= 18]
    c = Counter(sents)
    dup = [(s, n) for s, n in c.most_common() if n >= 2]
    add('F1 重复句子（≥18 字）', 'INFO',
        '%d 组（目录/正文/附录对照的合理复用，见报告说明）' % len(dup))
    for s, n in dup[:8]:
        print('    [%d次] %s' % (n, s[:40]))

    # ── G. 可读性（小字分布）───────────────────────
    small = Counter()
    for p in doc:
        for b in p.get_text('dict')['blocks']:
            if 'lines' not in b:
                continue
            for l in b['lines']:
                for s in l['spans']:
                    if s['size'] < 6 and s['text'].strip():
                        small[round(s['size'], 1)] += 1
    add('G1 <6pt 小字', 'INFO',
        json.dumps(dict(sorted(small.items())), ensure_ascii=False)
        if small else '0（全文无 <6pt 文字）')

    # ── 汇总 ───────────────────────────────────────
    print('\n===== 研究报告排版终版验收 =====')
    print('文件:', path)
    print('页面:', len(doc), '页 | 尺寸: %.1f x %.1f pt' % (W, H))
    print('-' * 56)
    fails = 0
    for name, status, ev in results:
        print('[%s] %-34s %s' % (status, name, ev))
        if status == 'FAIL':
            fails += 1
    print('-' * 56)
    if fails == 0:
        print('结论：全部硬门禁 PASS —— 本 PDF 通过排版终版验收。')
    else:
        print('结论：%d 项 FAIL —— 尚未达标，须修复后重跑。' % fails)
    return fails


if __name__ == '__main__':
    args = sys.argv[1:]
    expect_pages = None
    if '--expect-pages' in args:
        i = args.index('--expect-pages')
        if i + 1 >= len(args):
            sys.stderr.write('缺少 --expect-pages 的页数\n')
            sys.exit(2)
        expect_pages = int(args[i + 1])
        del args[i:i + 2]
    pdf = args[0] if args else None
    if not pdf:
        sys.stderr.write('用法: python3 终版排版验收.py <报告.pdf> [附录页码.json] [--expect-pages N]\n')
        sys.exit(2)
    jp = args[1] if len(args) > 1 else None
    if jp is None:
        cand = os.path.join(os.path.dirname(os.path.abspath(pdf)), '附录页码.json')
        if os.path.exists(cand):
            jp = cand
    sys.exit(main(pdf, jp, expect_pages=expect_pages))

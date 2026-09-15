# charforge 一致性自查：同 style 基础件 bbox 两两对比 ≤20% + 画布贴边/越界清单
# 用法：python bbox_check.py [charforge.html 所在目录]   （缺省 = 脚本上级 app/）
#       加 --strict 时 20% 违例使退出码为 1（默认只报告不失败——发型还原度取舍可豁免）
# 依赖：Python 3.9+ 与 playwright（`pip install playwright`；浏览器用系统 Edge，
#       无 Edge 自动退回 Playwright chromium，需先 `playwright install chromium`）
import glob, pathlib, sys
from itertools import combinations
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
args = [a for a in sys.argv[1:] if not a.startswith('-')]
strict = '--strict' in sys.argv
app = pathlib.Path(args[0]).resolve() if args else here.parent / 'app'
files = sorted(glob.glob(str(app / 'chars' / '*.js'))) or sorted(glob.glob(str(app / '*.js')))
if not files:
    print('!! 未找到角色文件（%s 或其 chars/ 下没有 .js）' % app)
    sys.exit(1)

with sync_playwright() as pw:
    try:
        b = pw.chromium.launch(channel='msedge')
    except Exception:
        b = pw.chromium.launch()
    pg = b.new_context(viewport={'width': 1500, 'height': 1080}).new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('dialog', lambda d: d.dismiss())
    pg.goto((app / 'charforge.html').as_uri())
    pg.wait_for_timeout(600)
    pg.set_input_files('#addFiles', files)
    pg.wait_for_timeout(800)
    n_chars = pg.evaluate("window.__CHARFORGE__.chars.length")

    # CF._items（资源清单）+ CF.measure（bbox 钩子）在页内逐件量
    parts = pg.evaluate("""() => {
      const CF = window.__CHARFORGE__, out = [];
      CF.chars.forEach(d => CF._items(d).forEach(en => {
        if (en.key.indexOf('|face:') >= 0 || en.key.indexOf('|att:') >= 0) return;
        const kind = en.key.indexOf('|head:') >= 0 ? 'head' : en.key.split(':').pop();
        const bb = CF.measure(d, en.item, en.key);
        const c = d.canvas || { w: 128, h: 128 };
        out.push({ char: d.id, style: d.style, kind: kind, name: en.label,
                   x: +bb.x.toFixed(2), y: +bb.y.toFixed(2), w: +bb.w.toFixed(2), h: +bb.h.toFixed(2),
                   edge: bb.x < 0.4 || bb.y < 0.4 || bb.x + bb.w > c.w - 0.4 || bb.y + bb.h > c.h - 0.4 });
      }));
      return out;
    }""")
    b.close()

print('角色 %d 个，基础件 %d 件（head + body 五件；faces/attachments 不参与 20%% 规则）\n' % (n_chars, len(parts)))
print('%-8s %-10s %-22s %7s %7s  %s' % ('角色', '部件类', '名称', '宽', '高', '贴边'))
for p in parts:
    print('%-8s %-10s %-22s %7.1f %7.1f  %s' %
          (p['char'], p['kind'], p['name'], p['w'], p['h'], '⚠ 越出 0~128' if p['edge'] else ''))

groups = {}
for p in parts:
    groups.setdefault((p['style'], p['kind']), []).append(p)
bad = []
print('')
for (style, kind), ps in sorted(groups.items()):
    if len(ps) < 2:
        continue
    for a, c in combinations(ps, 2):
        for dim in ('w', 'h'):
            m = min(a[dim], c[dim])
            if m <= 0:
                continue
            diff = abs(a[dim] - c[dim]) / m
            if diff > 0.20:
                bad.append((style, kind, dim, a, c, diff))
                print('✗ 20%% 违例 [%s] %s %s: %s/%s %.1f vs %s/%s %.1f → 差 %.0f%%' %
                      (style, kind, dim, a['char'], a['name'], a[dim],
                       c['char'], c['name'], c[dim], diff * 100))

edges = [p for p in parts if p['edge']]
if edges:
    print('⚠ 贴边/越界 %d 件（影响：预览舞台看不见超出部分；整体导出按 128 画框会被切；部件导出不受影响）' % len(edges))

print('\n== 20%% 违例 %d 处，贴边 %d 件 ==' % (len(bad), len(edges)))
if errs:
    print('页面错误:', errs[:3])
sys.exit(1 if (strict and bad) or errs else 0)

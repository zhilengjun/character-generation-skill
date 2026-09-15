# character-generation-skill 无头回归验证（153 项）：套装变体模型（头/表情/身体单选 + 分类挂件）+ file:// 加载 + 导出 ZIP
#
# 用法：python verify.py [Editor.html 所在目录]
#   目录缺省 = 本脚本上级目录的 app/（即 skill 自带的 app）。
# 依赖：Python 3.9+，pip install playwright && playwright install chromium
#   （或本机装有 Edge/Chrome：脚本优先用系统 Edge，找不到则退回 Playwright 自带 chromium）
# 产物（截图/导出包/往返目录）写在脚本旁的 _artifacts/，可随时删除。
import pathlib, sys, zipfile, json, shutil
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
art = here / '_artifacts'                    # 截图 / 下载包 / 往返页 都进这里
art.mkdir(exist_ok=True)
app = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else here.parent / 'app'
page_uri = (app / 'Editor.html').as_uri()
shot = lambda name: art / name

results = []
def check(name, cond, extra=''):
    results.append(('PASS' if cond else 'FAIL') + ' ' + name + ((' | ' + str(extra)) if extra else ''))

with sync_playwright() as pw:
    b = None
    try:
        b = pw.chromium.launch(channel='msedge')   # 系统自带的 Edge
    except Exception:
        b = pw.chromium.launch()                   # 退回 Playwright 自带 chromium
    ctx = b.new_context(viewport={'width': 1500, 'height': 1080}, device_scale_factor=1,
                        accept_downloads=True)
    pg = ctx.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    dialogs = []
    pg.on('dialog', lambda dlg: (dialogs.append(dlg.message), dlg.dismiss()))
    pg.goto(page_uri)
    pg.wait_for_timeout(800)

    # 1) file:// 空态 + 手选角色文件（与 HTML 同目录，多选）
    hint = pg.evaluate("document.getElementById('emptyHint').style.display !== 'none'")
    check('file:// 空态提示出现', hint)
    pg.set_input_files('#addFiles', [str(app / 'chars' / 'girl.js'), str(app / 'chars' / 'boy.js')])
    pg.wait_for_timeout(600)
    n = pg.evaluate("window.__CHARFORGE__.chars.length")
    check('同目录角色文件加载数=2', n == 2, n)
    check('无页面 JS 错误', not errors, errors[:3])

    # 2) 翻页工具：按显示名找页（目录输入的文件顺序不保证）
    def goto_char(name):
        for _ in range(6):
            if name in pg.text_content('#pgLabel'):
                return True
            pg.click('#pgNext')
            pg.wait_for_timeout(150)
        return False

    # 3) 女孩页：三组基础部件卡片数
    check('能翻到女孩页', goto_char('女孩'))
    check('手选文件路径提示(仅文件名)',
          'girl.js（手选文件' in pg.text_content('#srcPath'), pg.text_content('#srcPath'))
    stage_len = pg.evaluate("document.getElementById('stage').innerHTML.length")
    check('拼装 SVG 非空', stage_len > 500, stage_len)
    nh = pg.eval_on_selector_all('#gHead .pcard', 'els => els.length')
    nf = pg.eval_on_selector_all('#gFace .pcard', 'els => els.length')
    nb = pg.eval_on_selector_all('#gBody .pcard', 'els => els.length')
    check('女孩 头部卡=2', nh == 2, nh)
    check('女孩 表情卡=2', nf == 2, nf)
    check('女孩 身体卡=2', nb == 2, nb)
    cats = pg.eval_on_selector_all('#attGroups .gtitle b', "els => els.map(e => e.textContent)")
    check('女孩挂件分类=3(帽子/眼镜/武器)', cats == ['帽子', '眼镜', '武器'], cats)
    n_hat = pg.evaluate("document.querySelectorAll('#attGroups .grp:nth-child(1) .pcard').length")
    check('女孩 帽子分类 2 件', n_hat == 2, n_hat)
    check('预览下方无旧开关区', pg.evaluate("!document.getElementById('attToggles')"))

    # 4) 默认套装 = 各组第 1 套（紫上衣），挂件全不选
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('默认紫上衣', '#B48AD6' in stage and '#F2A7C3' not in stage)
    check('默认微笑表情', 'M61.5 45.5' in stage)
    check('头部为正圆 rx=ry=22', '<ellipse cx="64" cy="33" rx="22" ry="22"' in stage)
    check('默认无挂件', 'FFC75F' not in stage and 'M-24 0' not in stage)

    # 5) 文件名标注
    pf = pg.eval_on_selector_all('#gHead .pfile', 'els => els.map(e => e.textContent)')
    check('头部卡含导出文件名', len(pf) == 2 and all('girl_head_' in x and '@2x.png' in x for x in pf), pf)
    en = pg.text_content('#expNames')
    check('整体导出文件名提示', 'girl_full.svg' in en and 'girl_character-generation-skill.zip' in en, en)
    check('部件命名规则提示', '_body_' in en and '_att_' in en and '_face_' in en, en)

    # 6) 身体套装整体切换（紫 → 粉 → 紫）
    pg.evaluate("document.querySelectorAll('#gBody .pcard')[1].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('切粉连衣裙生效', '#F2A7C3' in stage and '#B48AD6' not in stage)
    check('粉套装含白袜', '#FFFFFF' in stage)
    sel_ok = pg.evaluate("document.querySelectorAll('#gBody .pcard')[1].classList.contains('sel')")
    check('粉卡片高亮选中', sel_ok)
    pg.evaluate("document.querySelectorAll('#gBody .pcard')[0].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('切回紫上衣生效', '#B48AD6' in stage and '#F2A7C3' not in stage)
    pg.screenshot(path=str(shot('_pg1_girl.png')), full_page=True)

    # 7) 表情单选（微笑 → 眨眼）
    pg.evaluate("document.querySelectorAll('#gFace .pcard')[1].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('眨眼生效', 'M51.2 36.9' in stage and 'M61.5 45.5' not in stage)
    pg.evaluate("document.querySelectorAll('#gFace .pcard')[0].click()")
    pg.wait_for_timeout(200)

    # 8) 头部单选（短发 → 双马尾）
    pg.evaluate("document.querySelectorAll('#gHead .pcard')[1].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('双马尾生效', 'M84.5 30' in stage)
    pg.evaluate("document.querySelectorAll('#gHead .pcard')[0].click()")
    pg.wait_for_timeout(200)

    # 9) 挂件：帽子分类内单选（贝雷帽 → 发箍）+ 跨分类复选 + 再点取消
    pg.evaluate("document.querySelectorAll('#attGroups .grp:nth-child(1) .pcard')[0].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('贝雷帽挂上', 'M-24 0' in stage)
    pg.evaluate("document.querySelectorAll('#attGroups .grp:nth-child(1) .pcard')[1].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('发箍替换贝雷帽（同类单选）', 'FF4D6D' in stage and 'M-24 0' not in stage)
    pg.evaluate("document.querySelectorAll('#attGroups .grp:nth-child(3) .pcard')[0].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('跨分类复选：法杖+发箍同显', 'FF4D6D' in stage and 'FFC75F' in stage)
    pg.evaluate("document.querySelectorAll('#attGroups .grp:nth-child(1) .pcard')[1].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('再点发箍取消', 'FF4D6D' not in stage and 'FFC75F' in stage)
    pg.screenshot(path=str(shot('_pg2_girl_wand.png')), full_page=True)

    # 10) 男孩页：切换 T恤短裤套装 + 全部挂件
    check('能翻到男孩页', goto_char('男孩'))
    nb_b = pg.eval_on_selector_all('#gBody .pcard', 'els => els.length')
    check('男孩 身体卡=2', nb_b == 2, nb_b)
    cats_b = pg.eval_on_selector_all('#attGroups .gtitle b', "els => els.map(e => e.textContent)")
    check('男孩挂件分类=4', cats_b == ['帽子', '眼镜', '披风', '武器'], cats_b)
    pg.evaluate("document.querySelectorAll('#gBody .pcard')[1].click()")
    pg.wait_for_timeout(200)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('男孩切 T恤短裤生效', '#5FA8D3' in stage and '#C9A66B' not in stage)
    pg.evaluate("""
      document.querySelectorAll('#attGroups .pcard').forEach(c => {
        const grp = c.closest('.grp');
        const cat = grp.querySelector('.gtitle b').textContent;
        const idx = Array.from(grp.querySelectorAll('.pcard')).indexOf(c);
        if (idx === 0) c.click();               // 每分类选第 1 件
      });
    """)
    pg.wait_for_timeout(300)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('男孩 4 类挂件齐上', all(k in stage for k in ('FF4D6D', '5FD3A6', '6B4A2F')),
          {k: (k in stage) for k in ('FF4D6D', '5FD3A6', '6B4A2F')})
    pg.screenshot(path=str(shot('_pg3_boy_all_att.png')), full_page=True)

    # 11) 导出 ZIP 并解包验证（男孩页；监听包裹点击；探针轮询 Promise 链状态）
    with pg.expect_download(timeout=30000) as dl:
        pg.click('#expZip')
        st = None
        for _ in range(50):
            pg.wait_for_timeout(500)
            st = pg.evaluate("window.__lastExport")
            if st and st.get('state') != 'running':
                break
        check('ZIP 导出状态 ok', bool(st) and st.get('state') == 'ok', st)
    d = dl.value
    zpath = art / '_export_boy.zip'
    d.save_as(str(zpath))
    zf = zipfile.ZipFile(zpath)
    names = zf.namelist()
    check('ZIP 含整体 SVG', 'boy_full.svg' in names, names[:4])
    check('ZIP 含整体 PNG', any('full@' in x and x.endswith('.png') for x in names))
    for probe in ('boy_head_bowl.svg', 'boy_head_mush.svg', 'boy_face_grin.svg',
                  'boy_body_jacket_torso.svg', 'boy_body_tee_leg_l.svg', 'boy_att_sword_wood.svg'):
        check('ZIP 含 ' + probe, probe in names)
    n_svg = sum(1 for x in names if x.endswith('.svg') and '_full' not in x)
    check('ZIP 部件 SVG =18(2头+2情+10身+4挂)', n_svg == 18, n_svg)
    pngs = [x for x in names if x.endswith('.png') and '_full' not in x]
    check('ZIP 部件 PNG =18', len(pngs) == 18, len(pngs))
    check('PNG 文件非空(>300B)', all(zf.getinfo(x).file_size > 300 for x in pngs))
    check('PNG 魔数正确', all(zf.open(x).read(8) == b'\x89PNG\r\n\x1a\n' for x in pngs))
    fsvg = zf.open('boy_full.svg').read().decode('utf-8')
    check('整体 SVG viewBox 128', 'viewBox="0 0 128 128"' in fsvg)
    check('整体 SVG 含 xmlns', 'xmlns="http://www.w3.org/2000/svg"' in fsvg)

    # 12) 文件选择器动态再加载（重复 id 报错）
    pg.set_input_files('#addFiles', [str(app / 'chars' / 'girl.js')])
    pg.wait_for_timeout(400)
    dup = pg.evaluate("window.__CHARFORGE__.errors.some(e => e.includes('重复'))")
    check('动态加载+重复 id 报错', dup)
    check('无未捕获错误', not errors, errors[:3])

    # 13) SVG 手动编辑器：打开 / 拖动锚点 / ≥5 步撤销重做 / 保存下载
    check('能翻到女孩页(编辑器)', goto_char('女孩'))
    pg.evaluate("document.querySelector('#gHead .pcard .edt').click()")
    pg.wait_for_timeout(300)
    check('编辑器对话框打开', pg.evaluate("document.getElementById('edDlg').style.display") == 'flex')
    fo = pg.evaluate("document.querySelector('#edStage circle[data-a]').getAttribute('fill-opacity')")
    check('未选锚点半透明(fill-opacity 0.45)', fo == '0.45', fo)
    title = pg.text_content('#edTitle')
    check('编辑器标题=头部', '头部' in title and '编辑' in title, title)
    m0 = pg.evaluate("""() => {
      const ed = window.__CHARFORGE__.getEd();
      const si = ed.shapes.findIndex(s => s.kind === 'path');
      ed.selShape = si;
      const p = ed.shapes[si].cmds[0].p.slice();
      window.__m0 = p; window.__si = si;
      return p;
    }""")
    fmt = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')
    mx, my = fmt(m0[0]), fmt(m0[1])
    pg.evaluate("window.__CHARFORGE__.edApi.select(window.__si, 0)")
    for _ in range(5):
        pg.evaluate("window.__CHARFORGE__.edApi.move(1, 1)")
    hist = pg.evaluate("window.__CHARFORGE__.getEd().hist.length")
    check('历史栈=6(初始+5次)', hist == 6, hist)
    p_now = pg.evaluate("window.__CHARFORGE__.getEd().shapes[window.__si].cmds[0].p")
    check('移动 5 次后坐标 +5', abs(p_now[0] - m0[0] - 5) < 0.01 and abs(p_now[1] - m0[1] - 5) < 0.01, p_now)
    for _ in range(5):
        pg.keyboard.press('Control+z')
    p_undo = pg.evaluate("window.__CHARFORGE__.getEd().shapes[window.__si].cmds[0].p")
    check('Ctrl+z 5 步回到原点', abs(p_undo[0] - m0[0]) < 0.01 and abs(p_undo[1] - m0[1]) < 0.01, p_undo)
    for _ in range(2):
        pg.keyboard.press('Control+y')
    p_redo = pg.evaluate("window.__CHARFORGE__.getEd().shapes[window.__si].cmds[0].p")
    check('Ctrl+y 重做 2 步 +2', abs(p_redo[0] - m0[0] - 2) < 0.01, p_redo)
    pg.screenshot(path=str(shot('_pg4_editor.png')))
    # 保存 = 直接写回原文件（通道 2：现场授权一次）。无头无法弹系统目录框 → 注入 fake picker
    pg.evaluate("""() => {
      window.__saved = {}; window.__dl = [];
      window.showDirectoryPicker = async () => ({
        getFileHandle: async (name) => ({
          createWritable: async () => ({
            write: async t => { window.__saved[name] = t; },
            close: async () => {}
          })
        })
      });
    }""")
    pg.on('download', lambda d: pg.evaluate("window.__dl.push(1)"))
    pg.click('#edApply')
    pg.wait_for_timeout(800)
    saved_text = pg.evaluate("window.__saved.girl || window.__saved['girl.js'] || null")
    check('保存直写原文件(girl.js)', bool(saved_text))
    check('保存未触发下载', pg.evaluate("window.__dl.length") == 0,
          pg.evaluate("window.__dl"))
    check('编辑器已关闭', pg.evaluate("document.getElementById('edDlg').style.display") == 'none')
    expect_m = 'M' + fmt(m0[0] + 2) + ' ' + fmt(m0[1] + 2)
    stage = pg.evaluate("document.getElementById('stage').innerHTML")
    check('override 已生效于舞台', expect_m in stage, expect_m)
    ov = pg.evaluate("window.__CHARFORGE__.chars.find(c=>c.id==='girl').overrides")
    check('overrides 记录 1 处编辑', ov and len(ov) == 1 and list(ov.values())[0].count('<path') >= 1,
          list(ov.keys()) if ov else ov)
    jspath = art / '_edit_girl.js'
    jspath.write_text(saved_text, encoding='utf-8')
    check('补丁行写入文件', '/*__CHARFORGE_EDITS__*/registerEdits' in saved_text and expect_m in saved_text)
    check('源 draw 代码未被改动', 'registerCharacter' in saved_text and saved_text.count('registerCharacter(') == 1)

    # 14) 往返：用保存后的 girl.js 重新建页加载，override 自动生效
    rt = art / '_rt'
    shutil.rmtree(rt, ignore_errors=True)
    rt.mkdir(parents=True)
    shutil.copy2(app / 'Editor.html', rt / 'Editor.html')
    shutil.copy2(app / 'chars' / 'boy.js', rt / 'boy.js')
    shutil.copy2(jspath, rt / 'girl.js')
    pg2 = b.new_context(accept_downloads=True).new_page()
    pg2.goto((rt / 'Editor.html').as_uri())
    pg2.wait_for_timeout(400)
    pg2.set_input_files('#addFiles', [str(rt / 'girl.js'), str(rt / 'boy.js')])
    pg2.wait_for_timeout(600)
    ovr = pg2.evaluate("""() => {
      const def = window.__CHARFORGE__.chars.find(c => c.id === 'girl');
      const loaded = def && def.headsets.some(h => h.__override != null);
      return { loaded: !!loaded, n: def ? Object.keys(def.overrides).length : 0 };
    }""")
    check('往返：override 装载到部件', ovr['loaded'] and ovr['n'] == 1, ovr)
    for _ in range(6):                                   # RT 页初始页可能是男孩，先翻到女孩
        if '女孩' in pg2.text_content('#pgLabel'):
            break
        pg2.click('#pgNext')
        pg2.wait_for_timeout(150)
    stage2 = pg2.evaluate("document.getElementById('stage').innerHTML")
    check('往返：舞台渲染编辑后几何', expect_m in stage2)
    pg2.evaluate("document.querySelectorAll('#gHead .pcard .edt')[0].click()")
    pg2.wait_for_timeout(200)
    check('往返：编辑器标注（已编辑）', '已编辑' in pg2.text_content('#edTitle'))
    pg2.close()

    # 15) file:// FSA 直读/直写（fake 目录句柄驱动真实代码路径）
    fsa = pg.evaluate("'showDirectoryPicker' in window")
    check('file:// 下 showDirectoryPicker 可用（Edge 安全上下文）', fsa)
    pg.evaluate("""() => {
      const CF = window.__CHARFORGE__;
      const GIRL = CF.texts.girl, BOY = CF.texts.boy;      // 先捕获，再清空（fake 读的是快照）
      const fake = {
        name: 'testroot',
        queryPermission: async () => 'granted',
        async *values() {
          yield { kind: 'file', name: 'boy.js' };
          yield { kind: 'file', name: 'girl.js' };
        },
        async getFileHandle(name) {
          return {
            getFile: async () => new File([name.startsWith('girl') ? GIRL : BOY], name),
            createWritable: async () => ({
              write: async t => { fake.captured = t; },
              close: async () => {}
            })
          };
        },
        captured: null
      };
      CF.dirHandle = fake;
      CF._fake = fake;
      CF.chars.length = 0; CF.errors.length = 0;
      delete CF.texts.girl; delete CF.texts.boy;
      delete CF.names.girl; delete CF.names.boy;
      CF.renderAll();                      // 清空后重渲染 → 空态与按钮可见
    }""")
    pg.wait_for_timeout(200)
    pg.click('#pickCharsBtn')
    pg.wait_for_timeout(500)
    n = pg.evaluate("window.__CHARFORGE__.chars.length")
    check('FSA 一键重连加载 2 角色', n == 2, n)
    check('FSA 源文件名已记录', pg.evaluate("window.__CHARFORGE__.names.girl") == 'girl.js',
          pg.evaluate("window.__CHARFORGE__.names"))
    check('FSA 加载后空态隐藏',
          pg.evaluate("document.getElementById('emptyHint').style.display === 'none'"))
    check('能翻到女孩页(路径)', goto_char('女孩'))
    check('FSA 路径提示=授权文件夹/文件名',
          pg.text_content('#srcPath') == '角色文件：testroot/girl.js', pg.text_content('#srcPath'))
    # 15b) 直写路径：编辑 → 保存 → 走 dirHandle.createWritable，零弹窗零下载
    check('能翻到女孩页(直写)', goto_char('女孩'))
    pg.evaluate("document.querySelector('#gHead .pcard .edt').click()")
    pg.wait_for_timeout(200)
    pg.evaluate("window.__CHARFORGE__.edApi.move(2, -1)")
    pg.click('#edApply')
    pg.wait_for_timeout(400)
    cap = pg.evaluate("window.__CHARFORGE__._fake.captured")
    check('FSA 直写捕获补丁行', bool(cap) and '/*__CHARFORGE_EDITS__*/registerEdits' in cap,
          (cap or '')[:80])
    check('FSA 直写文件名=girl.js', pg.evaluate(
        "window.__CHARFORGE__.texts.girl === window.__CHARFORGE__._fake.captured"))

    # 15c) chars/ 子目录自动下潜：授权文件夹顶层无 .js 但有 chars/ → 自动进去读；
    #      保存补丁写回 chars/（srcDir），不能落到上层目录
    pg.evaluate("""() => {
      const CF = window.__CHARFORGE__;
      const GIRL = CF.texts.girl, BOY = CF.texts.boy;      // 清空前快照
      const top = { name: null, text: null };              // 顶层写入桶
      const subb = { name: null, text: null };             // chars/ 写入桶
      const mkFH = (name, bucket) => ({
        getFile: async () => new File([name.startsWith('girl') ? GIRL : BOY], name),
        createWritable: async () => ({
          write: async t => { bucket.name = name; bucket.text = t; },
          close: async () => {}
        })
      });
      const sub = {
        name: 'chars',
        async *values() { yield { kind: 'file', name: 'boy.js' }; yield { kind: 'file', name: 'girl.js' }; },
        getFileHandle: async n => mkFH(n, subb)
      };
      const fake = {
        name: 'testroot',
        queryPermission: async () => 'granted',
        async *values() { yield { kind: 'directory', name: 'chars' }; },   // 顶层无 .js
        getDirectoryHandle: async n => n === 'chars' ? sub : Promise.reject(new Error('no dir')),
        getFileHandle: async n => mkFH(n, top),
        _top: top, _sub: subb
      };
      CF.dirHandle = fake; CF._fake = fake;
      CF.chars.length = 0; CF.errors.length = 0;
      delete CF.texts.girl; delete CF.texts.boy;
      delete CF.names.girl; delete CF.names.boy;
      CF.srcDir = {};
      CF.renderAll();
    }""")
    pg.wait_for_timeout(200)
    pg.click('#pickCharsBtn')
    pg.wait_for_timeout(500)
    n_sub = pg.evaluate("window.__CHARFORGE__.chars.length")
    check('chars/ 下潜自动加载 2 角色', n_sub == 2, n_sub)
    check('srcDir 指向 chars/ 子句柄', pg.evaluate(
        "!!window.__CHARFORGE__.srcDir['girl.js'] && window.__CHARFORGE__.srcDir['girl.js'] !== window.__CHARFORGE__.dirHandle"))
    check('能翻到女孩页(15c路径)', goto_char('女孩'))
    check('chars/ 子目录路径提示=授权文件夹/chars/文件名',
          pg.text_content('#srcPath') == '角色文件：testroot/chars/girl.js', pg.text_content('#srcPath'))
    # 保存 → 补丁写回 chars/（subb 桶），不落顶层（top 桶）
    check('能翻到女孩页(15c)', goto_char('女孩'))
    pg.evaluate("document.querySelector('#gHead .pcard .edt').click()")
    pg.wait_for_timeout(200)
    pg.evaluate("window.__CHARFORGE__.edApi.move(1, 1)")
    pg.click('#edApply')
    pg.wait_for_timeout(500)
    wrote = pg.evaluate("({sub: window.__CHARFORGE__._fake._sub, top: window.__CHARFORGE__._fake._top})")
    check('保存补丁写回 chars/ 子目录',
          wrote['sub']['name'] == 'girl.js' and 'registerEdits' in (wrote['sub']['text'] or ''), 
          {'sub_name': wrote['sub']['name'], 'sub_len': len(wrote['sub']['text'] or '')})
    check('上层目录未被污染', wrote['top']['name'] is None, wrote['top'])

    # 15d) 路径行旁「选择路径」按钮：注入 fake picker → 点击 → 重新加载 + 路径行刷新
    check('路径行旁有选择路径按钮', pg.evaluate(
        "!!document.getElementById('pickSrcBtn') && "
        "document.getElementById('pickSrcBtn').textContent.indexOf('选择路径') === 0"))
    pg.evaluate("""() => {
      const CF = window.__CHARFORGE__;
      const G = CF.texts.girl, B = CF.texts.boy;      // 快照后清空，避免重复 id
      const dir = {
        name: 'newroot',
        async *values() { yield { kind: 'file', name: 'girl.js' }; yield { kind: 'file', name: 'boy.js' }; },
        getFileHandle: async n => ({
          getFile: async () => new File([n.startsWith('girl') ? G : B], n)
        })
      };
      window.showDirectoryPicker = async () => dir;
      CF.chars.length = 0; CF.errors.length = 0;
      delete CF.texts.girl; delete CF.texts.boy;
      delete CF.names.girl; delete CF.names.boy;
      CF.srcDir = {};
    }""")
    pg.click('#pickSrcBtn')
    pg.wait_for_timeout(600)
    check('选择路径按钮重新加载角色', pg.evaluate("window.__CHARFORGE__.chars.length") == 2,
          pg.evaluate("window.__CHARFORGE__.chars.length"))
    check('能翻到女孩页(15d)', goto_char('女孩'))
    check('选择路径后路径行刷新', pg.text_content('#srcPath') == '角色文件：newroot/girl.js',
          pg.text_content('#srcPath'))

    # 15.5) 编辑器新增能力：颜色修改 / 路径增删（线+环）/ 锚点增删 / 撤销栈跨形状重建
    check('能翻到女孩页(编辑工具)', goto_char('女孩'))
    pg.evaluate("document.querySelector('#gHead .pcard .edt').click()")
    pg.wait_for_timeout(200)
    ED_ = "window.__CHARFORGE__.getEd()"
    API_ = "window.__CHARFORGE__.edApi"
    n0 = pg.evaluate(f"{ED_}.shapes.length")
    si0 = pg.evaluate(f"{ED_}.selShape")         # 被改色形状的初始索引
    # 颜色修改
    ok_color = pg.evaluate(f"{API_}.setFill('#FF0000')")
    c0 = pg.evaluate(f"{ED_}.shapes[{ED_}.selShape].attrs.fill")
    check('颜色修改生效', ok_color and c0 == '#FF0000', c0)
    # 描边颜色 + 粗细（设色后应出现「描边宽」数值框）
    ok_st = pg.evaluate(f"{API_}.setStroke('#123456')")
    pg.wait_for_timeout(100)
    has_w = pg.evaluate(
        "Array.from(document.querySelectorAll('#edNums label')).some(l => l.textContent.indexOf('描边宽') >= 0)")
    check('描边颜色+粗细可编辑', ok_st and has_w, (ok_st, has_w))
    # 「无」后可恢复：色块不得 disabled（点击选色即恢复），描边宽框恒显示
    ok_n = pg.evaluate(f"{API_}.setFill('none')")
    fill_state = pg.evaluate("""() => {
      const rows = [...document.querySelectorAll('#edNums .crow')];
      const fill = rows[0].querySelector('input[type=color]');
      return { disabled: fill.disabled, op: fill.style.opacity };
    }""")
    check('设「无」后填充色块仍可点击(不 disabled)',
          ok_n and not fill_state['disabled'] and fill_state['op'] != '', fill_state)
    # 模拟用户在色块里重新选色 → 填充恢复
    pg.evaluate("""() => {
      const fill = document.querySelectorAll('#edNums .crow')[0].querySelector('input[type=color]');
      fill.value = '#00AA00';
      fill.dispatchEvent(new Event('change'));
    }""")
    c_rec = pg.evaluate(f"{ED_}.shapes[{ED_}.selShape].attrs.fill")
    check('「无」状态选色即恢复', str(c_rec).lower() == '#00aa00', c_rec)
    # 新形状（无描边）→ 描边宽框恒显示且为 0；给宽度自动恢复描边色
    pg.evaluate(f"{API_}.addShape('line')")
    li2 = pg.evaluate(f"{ED_}.selShape")
    pg.evaluate(f"{ED_}.shapes[{li2}].attrs.stroke = 'none'; {ED_}.shapes[{li2}].attrs['stroke-width'] = null;")
    pg.evaluate(f"{API_}.select({li2}, null)")   # select 内部已 renderNums
    sw0 = pg.evaluate("""() => {
      const labs = [...document.querySelectorAll('#edNums label')];
      const l = labs.find(x => x.textContent.indexOf('描边宽') >= 0);
      return l ? parseFloat(l.querySelector('input').value) : null;
    }""")
    check('无描边时描边宽框仍显示(值 0)', sw0 == 0, sw0)
    pg.evaluate(f"""(() => {{
      const labs = [...document.querySelectorAll('#edNums label')];
      const inp = labs.find(x => x.textContent.indexOf('描边宽') >= 0).querySelector('input');
      inp.value = '2'; inp.dispatchEvent(new Event('change'));
    }})()""")
    sw_set = pg.evaluate(f"({{st: {ED_}.shapes[{li2}].attrs.stroke, w: {ED_}.shapes[{li2}].attrs['stroke-width']}})")
    check('无描边给宽度 → 自动恢复描边色', sw_set['w'] == 2 and sw_set['st'] == '#123456', sw_set)
    pg.evaluate(f"{API_}.delShape()")             # 清理临时线，形状数复原
    # 新增 线 + 环（环插在选中形状后，记录其索引）
    pg.evaluate(f"{API_}.addShape('line')")
    pg.evaluate(f"{API_}.addShape('loop')")
    n1 = pg.evaluate(f"{ED_}.shapes.length")
    li = pg.evaluate(f"{ED_}.selShape")          # 环的当前索引
    check('新增线/环 → 形状 +2', n1 == n0 + 2, (n0, n1))
    kind_new = pg.evaluate(f"{ED_}.shapes[{li}].kind")
    check('新增环为闭合 path', kind_new == 'path', kind_new)
    # 删除：选中原第一个形状并删掉（环索引随之前移）
    pg.evaluate(f"{API_}.select(0, null)")
    ok_del = pg.evaluate(f"{API_}.delShape()")
    n2 = pg.evaluate(f"{ED_}.shapes.length")
    check('删除形状 → 数量 -1', ok_del and n2 == n0 + 1, n2)
    # 锚点增删（在环上：4 锚 → 5 → 4）
    pg.evaluate(f"{API_}.select({li - 1 if li > 0 else li}, 0)")
    ok_ap = pg.evaluate(f"{API_}.addPt()")
    nanch1 = pg.evaluate(
        f"(() => {{ const s={ED_}.shapes[{ED_}.selShape]; return s.cmds.filter(c=>c.t!=='Z').length; }})()")
    check('新增锚点 → 锚点 +1', ok_ap and nanch1 == 5, nanch1)
    ok_dp = pg.evaluate(f"{API_}.delPt()")
    nanch2 = pg.evaluate(
        f"(() => {{ const s={ED_}.shapes[{ED_}.selShape]; return s.cmds.filter(c=>c.t!=='Z').length; }})()")
    check('删除锚点 → 锚点回 4', ok_dp and nanch2 == 4, nanch2)
    # 手柄增删：环上直段升曲线 / 降回直线（环 = [M,L,L,L,Z]，锚点0 出段=cmds[1]，锚点2 入段=cmds[2]）
    loi = li - 1 if li > 0 else li
    pg.evaluate(f"{API_}.select({loi}, 0)")
    ok_ho = pg.evaluate(f"{API_}.addHandle('out')")
    nx_t = pg.evaluate(f"{ED_}.shapes[{loi}].cmds[1].t")
    check('＋出柄：直段升为 C', ok_ho and nx_t == 'C', nx_t)
    has_ox = pg.evaluate(
        "Array.from(document.querySelectorAll('#edNums label')).some(l => l.textContent.indexOf('出柄X') >= 0)")
    check('＋出柄后出柄数值框出现', has_ox, has_ox)
    hfo = pg.evaluate("document.querySelector('#edStage circle[data-h=\"out\"]').getAttribute('fill-opacity')")
    check('手柄圆点半透明(fill-opacity 0.55)', hfo == '0.55', hfo)
    sfo = pg.evaluate("document.querySelector('#edStage circle[data-a=\"0\"]').getAttribute('fill-opacity')")
    check('选中锚点半透明(fill-opacity 0.7)', sfo == '0.7', sfo)
    ok_hd = pg.evaluate(f"{API_}.delHandle('out')")
    nx_t2 = pg.evaluate(f"{ED_}.shapes[{loi}].cmds[1].t")
    check('－出柄：曲线段降回 L', ok_hd and nx_t2 == 'L', nx_t2)
    pg.evaluate(f"{API_}.select({loi}, 2)")
    ok_hi = pg.evaluate(f"{API_}.addHandle('in')")
    in_t = pg.evaluate(f"{ED_}.shapes[{loi}].cmds[2].t")
    check('＋入柄：入段升为 C', ok_hi and in_t == 'C', in_t)
    ok_hi2 = pg.evaluate(f"{API_}.delHandle('in')")
    in_t2 = pg.evaluate(f"{ED_}.shapes[{loi}].cmds[2].t")
    check('－入柄：入段降回 L', ok_hi2 and in_t2 == 'L', in_t2)
    # 曲线段上加锚点：De Casteljau 细分 → 两段 C，新锚点两侧柄都在（不再拆断）
    pg.evaluate(f"{API_}.select({loi}, 0)")
    pg.evaluate(f"{API_}.addHandle('out')")          # 锚点0 出段变 C（直柄）
    ok_sub = pg.evaluate(f"{API_}.addPt()")
    sub = pg.evaluate(f"""(() => {{
      const s = {ED_}.shapes[{loi}];
      return {{ t1: s.cmds[1].t, t2: s.cmds[2].t, n: s.cmds.filter(c => c.t !== 'Z').length }};}})()""")
    check('曲线段加锚点：细分两段 C', ok_sub and sub['t1'] == 'C' and sub['t2'] == 'C' and sub['n'] == 5, sub)
    hv = pg.evaluate(f"""(() => {{
      const s = {ED_}.shapes[{loi}];
      return {{ ih: s.cmds[1].p[2] !== s.cmds[1].p[4] || s.cmds[1].p[3] !== s.cmds[1].p[5],
                oh: s.cmds[2].p[0] !== s.cmds[2].p[4] || s.cmds[2].p[1] !== s.cmds[2].p[5] }};}})()""")
    check('新锚点入柄保留', hv['ih'], hv)
    check('新锚点出柄保留', hv['oh'], hv)
    # 几何断言（直柄立方细分）：新锚点=原段中点，入柄=1/3 点，出柄=2/3 点
    geo = pg.evaluate(f"""(() => {{
      const s = {ED_}.shapes[{loi}];
      const A0 = s.cmds[0].p, F = s.cmds[1].p, H2 = s.cmds[2].p;
      return {{ l1: F.length, l2: H2.length,
        fx: F[4], fy: F[5], c2x: F[2], ohx: H2[0],
        mx: (A0[0] + H2[4]) / 2, my: (A0[1] + H2[5]) / 2,
        t1x: A0[0] + (H2[4] - A0[0]) / 3,
        t2x: A0[0] + (H2[4] - A0[0]) * 2 / 3 }};}})()""")
    check('细分结构：两段 C 参数个数=6', geo['l1'] == 6 and geo['l2'] == 6, (geo['l1'], geo['l2']))
    check('细分几何：新锚点=原段中点',
          abs(geo['fx'] - geo['mx']) < 0.02 and abs(geo['fy'] - geo['my']) < 0.02, geo)
    check('细分几何：入柄=原段1/3点', abs(geo['c2x'] - geo['t1x']) < 0.02, (geo['c2x'], geo['t1x']))
    check('细分几何：出柄=原段2/3点', abs(geo['ohx'] - geo['t2x']) < 0.02, (geo['ohx'], geo['t2x']))
    # 撤销栈整体重建：撤到栈深 1（保留第一次改色）→ 形状回原数量、颜色保留
    pg.evaluate(f"while ({ED_}.hi > 1) {{ {API_}.undo(); }}")
    n3 = pg.evaluate(f"{ED_}.shapes.length")
    c3 = pg.evaluate(f"{ED_}.shapes[{si0}].attrs.fill")   # 撤销后数组复原，被改色形状回到原索引
    check('撤销跨形状增删重建', n3 == n0, (n0, n3))
    check('撤销后颜色修改保留', c3 == '#FF0000', (c3, si0))
    # 应用保存 → override 含新颜色
    pg.click('#edApply')
    pg.wait_for_timeout(400)
    ok_ov = pg.evaluate("""() => {
      const def = window.__CHARFORGE__.chars.find(c => c.id === 'girl');
      return Object.values(def.overrides || {}).some(v => v.indexOf('#FF0000') >= 0);
    }""")
    check('保存回写含颜色与新增形状', ok_ov)
    check('编辑器已关闭(工具段)', pg.evaluate("document.getElementById('edDlg').style.display === 'none'"))

    # 15.7) 预览拖动部件：真实 mouse 拖 → __pos 提交 → 静默写盘含位移包裹 → 拖回原位还原
    check('能翻到女孩页(拖动)', goto_char('女孩'))
    pg.evaluate("window.__CHARFORGE__.chars.forEach(d => window.__CHARFORGE__._items(d).forEach(en => delete en.item.__pos))")
    # 确保至少选中一个挂件（默认装配不含挂件；无则点第一张挂件卡）
    pg.evaluate("""() => {
      const st = document.getElementById('stage');
      if (!st.querySelector('g[data-cfk*="|att:"]')) {
        const card = document.querySelector('#attGroups .pcard');
        if (card) card.click();
      }
    }""")
    pg.wait_for_timeout(300)
    pt = pg.evaluate("""() => {
      const st = document.getElementById('stage');
      const r = st.getBoundingClientRect();
      const vb = st.viewBox.baseVal;
      const layers = [...st.querySelectorAll('g[data-cfk]')];
      const atts = layers.filter(g => g.getAttribute('data-cfk').indexOf('|att:') >= 0);
      const order = atts.length ? atts.concat(layers) : layers;
      for (const g of order) {
        const bb = g.getBBox();
        const x = r.left + (bb.x + bb.width / 2) / vb.width * r.width;
        const y = r.top + (bb.y + bb.height / 2) / vb.height * r.height;
        const el = document.elementFromPoint(x, y);
        const hit = el && el.closest && el.closest('g[data-cfk]');
        if (hit === g) return { x: x, y: y, key: g.getAttribute('data-cfk') };
      }
      return null;
    }""")
    check('找到可拖部件层', pt is not None, pt)
    if pt is None:
        print('!! 无法定位可拖部件层，终止（附舞台层清单）')
        print(pg.evaluate("[...document.getElementById('stage').querySelectorAll('g[data-cfk]')].map(g => g.getAttribute('data-cfk'))"))
        sys.exit(1)
    # 拖动方向朝画布中心：挂件可能贴边（如魔杖），向外拖会触发越界作废
    pc = pg.evaluate("""(key) => {
      const g = document.querySelector('g[data-cfk="' + key + '"]');
      const bb = g.getBBox();
      return { cx: bb.x + bb.width / 2, cy: bb.y + bb.height / 2 };
    }""", pt['key'])
    sx = 30 if pc['cx'] < 64 else -30
    sy = 18 if pc['cy'] < 64 else -18
    ctm_sc = pg.evaluate("(() => { const s = document.getElementById('stage');"
                         " return Math.min(s.clientWidth, s.clientHeight) / s.viewBox.baseVal.width; })()")
    pg.mouse.move(pt['x'], pt['y'])
    pg.mouse.down()
    pg.mouse.move(pt['x'] + sx, pt['y'] + sy, steps=6)   # 屏幕 ±30/18px → 画布 ∓9.6/5.76 级
    pg.mouse.up()
    pg.wait_for_timeout(500)                              # 等 mouseup 的异步写盘
    pos = pg.evaluate("""() => {
      const d = window.__CHARFORGE__.chars.find(c => c.id === 'girl');
      const en = window.__CHARFORGE__._items(d).find(en => en.key === %s);
      return en && en.item.__pos ? [en.item.__pos.x, en.item.__pos.y] : null;
    }""" % json.dumps(pt['key']))
    check('拖动提交 __pos≈一屏位移',
          pos is not None and abs(pos[0] - sx / ctm_sc) < 1.2 and abs(pos[1] - sy / ctm_sc) < 1.2, pos)
    # client 像素口径：位移应精确 = 光标位移 / 内容缩放（clientWidth 扣边框；CTM 在 CSS zoom 下口径漂移，禁用）
    check('拖动严格跟手(client像素精确换算)',
          pos is not None and abs(pos[0] - sx / ctm_sc) < 0.05 and abs(pos[1] - sy / ctm_sc) < 0.05,
          (pos, ctm_sc))
    cap2 = ''
    for _ in range(20):                        # 轮询等异步写盘（固定等待偶发不够）
        cap2 = pg.evaluate("window.__CHARFORGE__._fake.captured || ''")
        if 'transform="translate(' in cap2 and 'registerEdits' in cap2:
            break
        pg.wait_for_timeout(150)
    check('拖动后静默写盘含位移包裹',
          {'has_tr': 'transform="translate(' in cap2, 'has_re': 'registerEdits' in cap2,
           'len': len(cap2)}, cap2[-120:])
    # 重载归一化：模拟重新注册（wrapped → __pos 还原、__override=inner）
    norm = pg.evaluate("""() => {
      const CF = window.__CHARFORGE__;
      const d = CF.chars.find(c => c.id === 'girl');
      const en = CF._items(d).find(en => en.item.__pos);
      if (!en) return null;
      en.item.__pos = null;
      en.item.__override = null;                   // 模拟重载后的全新条目
      CF.renderAll();
      const en2 = CF._items(d).find(x => x.key === en.key);
      return { pos: en2.item.__pos ? [en2.item.__pos.x, en2.item.__pos.y] : null,
               ovWrapped: (d.overrides[en.key] || '').indexOf('<g transform="translate(') === 0 };
    }""")
    check('重载归一化还原 __pos', norm is not None and norm['pos'] is not None and
          abs(norm['pos'][0] - pos[0]) < 0.6 and abs(norm['pos'][1] - pos[1]) < 0.6, norm)
    # 拖回原位 → __pos 归零（二次拖动：中途中断言所见即所得——部件屏幕位移==光标位移。
    # 该断言专防「实时 transform 叠加旧 __pos 导致双倍位移」回归：内层渲染已含 __pos，
    # 拖动中只能加增量，否则第二次拖动部件多偏一个旧位移量，所见非所得）
    pg.mouse.move(pt['x'] + sx, pt['y'] + sy)
    pg.mouse.down()
    m_grab = pg.evaluate("""(key) => {
      const g = document.querySelector('g[data-cfk="' + key + '"]');
      const bb = g.getBBox(), m = g.getCTM();
      return { x: m.a * bb.x + m.e, y: m.d * bb.y + m.f };
    }""", pt['key'])
    pg.mouse.move(pt['x'] + sx / 2, pt['y'] + sy / 2, steps=3)   # 拖回一半：光标Δ=(-sx/2,-sy/2)
    pg.wait_for_timeout(60)
    m_mid = pg.evaluate("""(key) => {
      const g = document.querySelector('g[data-cfk="' + key + '"]');
      const bb = g.getBBox(), m = g.getCTM();
      return { x: m.a * bb.x + m.e, y: m.d * bb.y + m.f };
    }""", pt['key'])
    check('二次拖动所见即所得(中途位移==光标位移)',
          abs((m_mid['x'] - m_grab['x']) + sx / 2) < 1 and abs((m_mid['y'] - m_grab['y']) + sy / 2) < 1,
          {'part_d': [round(m_mid['x'] - m_grab['x'], 2), round(m_mid['y'] - m_grab['y'], 2)],
           'want_d': [-sx / 2, -sy / 2]})
    pg.mouse.move(pt['x'], pt['y'], steps=3)
    pg.mouse.up()
    pg.wait_for_timeout(400)
    pos2 = pg.evaluate("""() => {
      const d = window.__CHARFORGE__.chars.find(c => c.id === 'girl');
      const en = window.__CHARFORGE__._items(d).find(en => en.key === %s);
      return en && en.item.__pos ? [en.item.__pos.x, en.item.__pos.y] : null;
    }""" % json.dumps(pt['key']))
    check('拖回原位 __pos≈(0,0)', pos2 is not None and abs(pos2[0]) < 1.2 and abs(pos2[1]) < 1.2, pos2)
    # 清理：归零 pos 并从 overrides 移除位移层，避免影响后续导出断言
    pg.evaluate("""() => {
      const CF = window.__CHARFORGE__;
      const d = CF.chars.find(c => c.id === 'girl');
      CF._items(d).forEach(en => {
        if (en.item.__pos && !en.item.__override) delete (d.overrides || {})[en.key];
        delete en.item.__pos;
      });
      CF.renderAll();
    }""")
    # 松手不跳位（独立段，不污染上游状态）：最后一帧 move 在 +100px，pointerup 在 +140px
    # → 提交必须按 +100（最后已应用值），不按 pointerup 位置重算（浏览器合帧时旧代码会前跳）
    nj = pg.evaluate("""(pt) => {
      const CF = window.__CHARFORGE__;
      CF.chars.forEach(d => CF._items(d).forEach(en => delete en.item.__pos));
      CF.renderAll();
      const st = document.getElementById('stage');
      const g = st.querySelector('g[data-cfk]');
      const key = g.getAttribute('data-cfk');
      const fire = (type, x, y) => g.dispatchEvent(new PointerEvent(type,
        { bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0, pointerId: 7 }));
      fire('pointerdown', pt.x, pt.y);
      fire('pointermove', pt.x + 100, pt.y);
      const lastTr = g.getAttribute('transform');
      fire('pointerup', pt.x + 140, pt.y);
      const d = CF.chars.find(c => c.id === 'girl');
      const en = CF._items(d).find(en => en.key === key);
      const tx = parseFloat(lastTr.replace('translate(', '').split(' ')[0]);
      const r = { last: tx, commit: en.item.__pos ? en.item.__pos.x : 0 };
      en.item.__pos = null;                        // 清理，不影响后续导出
      delete (d.overrides || {})[key];
      CF.renderAll();
      return r;
    }""", pt)
    check('松手不跳位(提交最后已应用值, 不按 pointerup 重算)',
          abs(nj['commit'] - nj['last']) < 0.01 and abs(nj['commit'] - 100 / ctm_sc) < 0.2, nj)

    # 拖出预览框 → 本次拖动作废弹回：无残留 transform、__pos 不变、toast 提示
    obs = pg.evaluate("""(pt) => {
      const CF = window.__CHARFORGE__;
      const d = CF.chars.find(c => c.id === 'girl');
      const stKey = [...document.querySelectorAll('#stage g[data-cfk]')]
        .map(x => x.getAttribute('data-cfk')).find(k => k.indexOf('|att:') >= 0);
      if (!stKey) return { fail: true, reason: 'stage 无挂件层' };
      const en = CF._items(d).find(e => e.key === stKey);
      en.item.__pos = null;
      d.__posOk = false;
      CF.renderAll();
      const g = document.querySelector('g[data-cfk="' + en.key + '"]');
      if (!g) return { fail: true, key: en.key,
        curId: (window.__CHARFORGE__.chars[window.__CHARFORGE__.cur] || {}).id,
        stageKeys: [...document.querySelectorAll('#stage g[data-cfk]')].map(x => x.getAttribute('data-cfk')) };
      const fire = (type, x, y) => g.dispatchEvent(new PointerEvent(type,
        { bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0, pointerId: 7 }));
      fire('pointerdown', pt.x, pt.y);
      fire('pointermove', pt.x + 800, pt.y);       // 一大步直接冲出右边界
      const tr = g.getAttribute('transform');
      const pMid = en.item.__pos;
      fire('pointerup', pt.x + 800, pt.y);
      const t = document.getElementById('toast');
      return { tr: tr, pos: en.item.__pos, mid: pMid,
               toast: t && t.style.display !== 'none' ? t.textContent : '' };
    }""", pt)
    if obs.get('fail'):
        print('!! obs 前置态异常:', obs); sys.exit(1)
    check('拖出预览框 → 拖动作废(transform 已移除)',
          obs['tr'] is None and obs['mid'] is None, obs)
    check('拖出预览框 → __pos 未被污染', obs['pos'] is None, obs)
    check('拖出预览框 → toast 提示弹回', '超出预览框' in obs['toast'], obs['toast'])

    # 启动重置：已越界的 __pos 在 renderAll（启动/重载路径）被重置到预览框中心
    sc = pg.evaluate("""() => {
      const CF = window.__CHARFORGE__;
      const d = CF.chars.find(c => c.id === 'girl');
      const stKey = [...document.querySelectorAll('#stage g[data-cfk]')]
        .map(x => x.getAttribute('data-cfk')).find(k => k.indexOf('|att:') >= 0);
      const en = CF._items(d).find(e => e.key === stKey);
      en.item.__pos = { x: 300, y: -80 };
      d.__posOk = false;
      CF.renderAll();
      const bb = document.querySelector('g[data-cfk="' + en.key + '"]').getBBox();
      return { pos: en.item.__pos, cx: bb.x + bb.width / 2, cy: bb.y + bb.height / 2 };
    }""")
    check('启动越界位移重置到预览框中心',
          sc['pos'] is not None and abs(sc['cx'] - 64) < 0.5 and abs(sc['cy'] - 64) < 0.5, sc)
    # 清理：归零 pos，不影响后续导出断言
    pg.evaluate("""() => {
      const CF = window.__CHARFORGE__;
      const d = CF.chars.find(c => c.id === 'girl');
      const stKey = [...document.querySelectorAll('#stage g[data-cfk]')]
        .map(x => x.getAttribute('data-cfk')).find(k => k.indexOf('|att:') >= 0);
      const en = CF._items(d).find(e => e.key === stKey);
      if (en) en.item.__pos = null;
      CF.renderAll();
    }""")

    # 16) 选中部件导出：直接读预览装配（头+表情+身体套5件=7 + 已点挂件）
    check('能翻到女孩页(选中导出)', goto_char('女孩'))
    # 前置态归零：取消此前章节可能点选的挂件（点选中的卡=取消）
    pg.evaluate("document.querySelectorAll('#attGroups .pcard.sel').forEach(c => c.click())")
    pg.wait_for_timeout(200)
    cnt = pg.text_content('#selCount')
    check('默认预览装配计数=7', '7' in cnt, cnt)
    check('选中按钮恒可用', not pg.evaluate("document.getElementById('expSelZip').disabled"))
    # 选中 ZIP 下载并解包验证（默认装配 7 资源 ×2 格式）
    with pg.expect_download(timeout=30000) as dl2:
        pg.click('#expSelZip')
    d3 = dl2.value
    check('选中 ZIP 文件名', d3.suggested_filename == 'girl_selected.zip', d3.suggested_filename)
    zsel = art / '_export_sel.zip'
    d3.save_as(str(zsel))
    zf2 = zipfile.ZipFile(zsel)
    ns2 = zf2.namelist()
    check('选中 ZIP 无整体文件', not any('_full' in n for n in ns2), len(ns2))
    check('选中 ZIP SVG=7 + PNG=7', len([x for x in ns2 if x.endswith('.svg')]) == 7 and
          len([x for x in ns2 if x.endswith('.png')]) == 7, ns2[:6])
    # 点第一个挂件卡 → 预览装配 +1 → 计数 8；再点取消 → 回 7
    pg.click('#attGroups .pcard')
    pg.wait_for_timeout(200)
    cnt2 = pg.text_content('#selCount')
    check('点挂件后计数=8', '8' in cnt2, cnt2)
    pg.click('#attGroups .pcard')
    pg.wait_for_timeout(200)
    check('再点挂件后计数回 7', '7' in pg.text_content('#selCount'),
          pg.text_content('#selCount'))

    # 17) PNG 倍率：枚举下拉 → 浮点输入框（1 位小数，区间 (0,10]，读取时门闩归一化）
    ps = pg.evaluate("""() => {
      const el = document.getElementById('pngScale');
      return { tag: el.tagName, type: el.type, val: el.value,
               min: el.min, max: el.max, step: el.step };
    }""")
    check('倍率控件=number 输入框(默认2, 0.1~10, 步0.1)',
          ps['tag'] == 'INPUT' and ps['type'] == 'number' and ps['val'] == '2'
          and ps['min'] == '0.1' and ps['max'] == '10' and ps['step'] == '0.1', ps)

    def set_scale(v):
        pg.evaluate("""(v) => {
          const el = document.getElementById('pngScale');
          el.value = v;
          el.dispatchEvent(new Event('change'));
        }""", v)

    def scale_state():
        return pg.evaluate("""() => {
          const v = document.getElementById('pngScale').value;
          const pf = document.querySelector('#gHead .pfile');
          return { v: v, pf: pf ? pf.textContent : '' };
        }""")

    set_scale('1.5')
    st = scale_state()
    check('1.5x 生效且文件名跟随 @1.5x.png',
          st['v'] == '1.5' and '@1.5x.png' in st['pf'], st)
    set_scale('2.5')
    check('2.5x 生效', scale_state()['v'] == '2.5', scale_state())
    set_scale('10')
    check('上限 10 允许', scale_state()['v'] == '10', scale_state())
    set_scale('12')
    check('超上限 12 → 门闩回 10', scale_state()['v'] == '10', scale_state())
    set_scale('0.05')
    check('下限以下 0.05 → 门闩回 0.1', scale_state()['v'] == '0.1', scale_state())
    set_scale('1.25')
    check('两位小数 1.25 → 舍入 1.3', scale_state()['v'] == '1.3', scale_state())
    set_scale('0')
    check('0 → 非法回默认 2', scale_state()['v'] == '2', scale_state())
    set_scale('-3')
    check('负数 → 非法回默认 2', scale_state()['v'] == '2', scale_state())
    set_scale('abc')
    check('非数字 → 非法回默认 2', scale_state()['v'] == '2', scale_state())
    # 真实导出：1.5x 整体 PNG → 128*1.5=192px，文件名 @1.5x
    set_scale('1.5')
    with pg.expect_download(timeout=30000) as dl3:
        pg.click('#expFullPng')
    d4 = dl3.value
    check('1.5x 整体 PNG 文件名', d4.suggested_filename == 'girl_full@1.5x.png',
          d4.suggested_filename)
    png1 = art / '_export_full_15.png'
    d4.save_as(str(png1))
    raw = png1.read_bytes()
    w, h = int.from_bytes(raw[16:20], 'big'), int.from_bytes(raw[20:24], 'big')
    check('1.5x PNG 实际尺寸 192x192(不截断)', w == 192 and h == 192, (w, h))
    set_scale('2')
    check('恢复默认 2x', scale_state()['v'] == '2', scale_state())

    b.close()

    print('\n'.join(results))
    if dialogs: print('DIALOGS:', dialogs)
    fails = sum(1 for r in results if r.startswith('FAIL'))
    print(f'\n== {len(results) - fails}/{len(results)} PASS ==')
    sys.exit(1 if fails else 0)

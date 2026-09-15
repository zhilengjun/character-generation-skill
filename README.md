# CharForge · 部件化 2D 游戏角色生成与导出

一套「**一个 HTML + 每角色一个 .js**」的部件化角色资产生产线：角色 128px 高、纯 SVG 矢量、
无骨骼无动画，部件可单独导出，同 Style 部件尺寸差异强制 ≤20%（换装 / 换皮不穿帮）。

本仓库同时是一个 **Claude 技能包**（`skill/charforge/`）和一套**可直接运行的 Web 应用**
（`skill/charforge/app/charforge.html`），配套开发 / 验收测试（`tests/`）。

## 这是什么

- **部件化拼装**：基础部件三组单选（头部 `headsets` / 表情 `faces` / 身体 `bodies`）
  + 分类挂件 `attachments`（跨分类复选、分类内单选）。身体一套 = `legL/legR/torso/armL/armR`
  5 件整体替换。
- **存档即文件**：每个角色一个自包含 `.js`，调用 `registerCharacter(def)` 注册。
  双击 `app/charforge.html` 即可预览 / 导出（file:// 直开，免服务器）。
- **可视化微调**：预览舞台拖拽定位、SVG 手动编辑器（锚点 / 曲线手柄 / 颜色，Ctrl+Z/Y 撤销重做），
  保存作为 override 写回角色 `.js`。
- **一键导出**：全部资源 / 选中装配 / 整角色 × SVG / PNG（尺寸倍率可调）/ ZIP。
- **一致性护栏**：同 Style 角色的基础件 bbox 宽高差异 ≤20%，保证换装 / 换皮不穿帮、部件可互换。

## 目录结构

```
char-forge/
├── README.md                        # 本文件
├── AGENTS.md                        # 编码代理工作指引（改这个仓库先读）
├── .gitignore
├── skill/charforge/
│   ├── SKILL.md                     # 技能说明：30 秒决策表、新建角色流程、红线、坑
│   ├── references/
│   │   └── format-spec.md           # 角色存档格式规范（真源）
│   └── app/
│       ├── charforge.html           # 单页应用（预览 / 拼装 / 编辑器 / 导出）
│       └── chars/
│           ├── girl.js              # 样例角色：女孩
│           └── boy.js               # 样例角色：男孩
├── tests/
│   ├── README.md                    # 测试工具说明
│   ├── verify.py                    # 功能回归（153 项，Playwright）
│   └── bbox_check.py                # 20% 一致性自查 + 贴边/越界清单
└── assets/                          # 预留素材目录（参考图 / 导出包等）
```

## 快速开始

1. **预览**：直接双击打开 `skill/charforge/app/charforge.html`。
   - file:// 下点「📂 选择角色文件夹」授权一次（句柄存 IndexedDB，之后静默直读）；
   - 或点「加载角色文件」手动多选 `.js`。
2. **加新角色**：
   - 读 `skill/charforge/references/format-spec.md` 与 `girl.js` / `boy.js` 样例；
   - 写 `<角色名>.js`（自包含绘图原语 + `registerCharacter`）放进 `app/chars/`；
   - **不改 charforge.html**——角色发现是全自动的（同目录与 `chars/` 下的 `.js`）。
3. **验收**：
   - `node --check app/角色名.js`
   - `python tests/bbox_check.py`（一致性）与 `python tests/verify.py`（功能回归）
   - 打开页面肉眼验收 + 导出 ZIP 解包验证。
4. **交付**：把 `app/` 整个目录交给用户（html 与 `chars/` 一起拷走）。

## 角色文件格式（要点）

自包含 `.js`，顶层 `{ id, name, style, canvas:{w,h}, height, palette, anchors, headsets[],
faces[], bodies[], attachments[] }`。绘图原语（`stroked/limb/shape/ell/circ/rrect/dot`）每文件内联。
**风格 = 平涂无描边**，`LINE #4A3B42` 只用于五官 / 细节线；身体 5 件 key 固定
`legL/legR/torso/armL/armR`；挂件 `draw` **只能用挂点局部坐标**作画。

完整规范与比例基准见 [`references/format-spec.md`](skill/charforge/references/format-spec.md)。

## 文档速览

| 用途 | 文件 |
|---|---|
| 技能用法 / 30 秒决策 / 红线 / 已踩过的坑 | [`SKILL.md`](skill/charforge/SKILL.md) |
| 角色文件格式真源 | [`references/format-spec.md`](skill/charforge/references/format-spec.md) |
| 测试工具（verify.py / bbox_check.py） | [`tests/README.md`](tests/README.md) |
| 编码代理工作指引 | [`AGENTS.md`](AGENTS.md) |

## 许可与风格

- 风格基准：`chibi-3head-warmline-128`（128×128，头约 y10~55，同 Style 勿动纵向节奏）。
- 能力边界：能做到 128px chibi、同风格批量角色、挂件无限扩展、SVG/PNG/ZIP 导出；
  做不到骨骼 / 帧动画、位图 / 厚涂、大于 128 的精细立绘。

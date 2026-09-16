# AGENTS.md — character-generation-skill 仓库工作指引

给**在这个仓库里工作**的编码代理（改 `Editor.html`、批量改角色、加新角色、维护测试）。
先读本文件再动手；完整的能力边界、决策表和「已踩过的坑」见 [`SKILL.md`](skill/character-generation-skill/SKILL.md)，
角色文件格式真源见 [`references/format-spec.md`](skill/character-generation-skill/references/format-spec.md)。

> 只「用工具做角色 / 加角色 / 导出素材」的话不需要本目录——那是技能使用场景，走 SKILL.md。

## 项目速览

- 一套「一个 HTML + 每角色一个 .js」的部件化 2D 角色资产生产线：128px chibi、纯 SVG、无动画。
- 基础部件三组单选（`headsets` 头部 / `faces` 表情 / `bodies` 身体=5 件整体替换）+ 分类挂件
  `attachments`（跨分类复选、分类内单选）。
- 存档即文件：每个角色一个自包含 `.js`，调用全局 `registerCharacter(def)` 注册。
- **角色发现全自动**（Editor.html 同目录与下层 `chars/` 的 `.js`）：加 / 减角色**只放文件，
  绝不该改 Editor.html**——HTML 里没有挂载清单。

## 关键文件地图

| 路径 | 作用 | 要不要改 |
|---|---|---|
| `skill/character-generation-skill/app/Editor.html` | 单页应用（预览 / 拼装 / 编辑器 / 导出） | 只改 bug / 加交互；**勿动主逻辑与挂载机制** |
| `skill/character-generation-skill/app/chars/*.js` | 角色存档 | 加角色就加这里 |
| `skill/character-generation-skill/references/format-spec.md` | 角色文件格式**真源** | 写角色前必读 |
| `skill/character-generation-skill/SKILL.md` | 决策表 + 红线 + 坑 | 改前先看 |
| `tests/verify.py` | 功能回归（162 项，Playwright） | 改 HTML / 批量改角色后跑 |
| `tests/bbox_check.py` | 20% 一致性 + 贴边/越界自查 | 加角色后跑 |

## 加新角色的固定流程

1. **问 Style**（如没给）：新风格 → 让用户给参考；同风格追加 → 读现有角色文件拿
   palette + anchors + 比例。
2. **写角色文件**：严格按 `skill/character-generation-skill/references/format-spec.md`，**以现有角色文件为锚**
   （例：`skill/character-generation-skill/app/chars/girl.js`），自包含绘图原语内联。**同风格比例基准别动**。
3. **收纳**：写进 `skill/character-generation-skill/app/chars/`（默认角色文件夹）即完成——HTML 自动发现，
   **不改 Editor.html**。
4. **验收**：
   - `node --check skill/character-generation-skill/app/chars/<角色名>.js`
   - 打开 `skill/character-generation-skill/app/Editor.html` 肉眼验收 + 每套/挂件切一遍
   - `python tests/bbox_check.py`（一致性）与 `python tests/verify.py`（功能回归）
   - 导出 ZIP 解包验证：**SVG / PNG 各一份，文件数 = 头部套数 + 表情数 + 身体套数×5 + 挂件数**（另含整体 2 件）
5. **交付**：把 `skill/character-generation-skill/app/`（Editor.html 与 chars/ 一起）整个目录拷给用户。

## 硬规则（红线）

- **加 / 减角色不改 Editor.html**（自动发现同目录与 `chars/`）。file:// 下 fetch 目录被
  CORS 拦是预期，页面走「选择文件夹」授权。
- **挂件 `draw` 只能用挂点局部坐标**，不能写画布绝对坐标——页面会把挂件整体 translate 到锚点上。
  换算：局部 = 绝对 − anchors[slot]。复用的基础件辅助函数同理（`bigEye(72.8)` → `bigEye(8.8)`）。
- **身体 5 件 key 固定** `legL/legR/torso/armL/armR`，缺件该件不画；除了
  `headsets/faces/bodies/attachments` 四组，不存在其他部件概念——想「再加一种基础件」先质疑需求。
- **角色 id 全局唯一**，重复 id 会在「加载问题」面板报错。
- **`/*__CHARFORGE_EDITS__*/registerEdits(...)` 单行补丁是保留行**：是手动编辑的 override。
  更新它是**编辑器的事**——手动编辑器点「完成并保存」时工具会**自动整行替换**该补丁；人工直接改
  角色文件时**不要动它**，想还原就删掉整行即恢复 draw 输出。
- **同一文件多处修改必须串行做**——并行 Edit 可能静默丢一处。
- **20% 一致性规则**：同 style 基础件（head + body 五件）bbox 宽高两两差异 ≤20%；
  faces/attachments 不参与。页面不展示数据表，写角色时自查。**有意取舍**（如垂发 vs 短发）
  可豁免并在交付说明里写明——样例 girl/boy 有 6 处已知违例属设计决定。

## 改 / 维护 HTML 的注意（坑）

- **每个 render 分支开头 `if (!def) return`**：0 角色时 `renderAll` 也会跑全部 renderXxx，
  缺防御会在空态抛错、炸掉后续面板（只 console 露出）。
- **页面内没有角色文件的原语**（ell/shape 等）：卡片预览要画脸底等直接内联
  `<ellipse .../>` 字符串，别调角色文件的 helper（`ell is not defined`）。
- **`buildZip` 只吃 `Uint8Array`**：塞 `ArrayBuffer` 或 PNG `Blob` 会 `offset is out of bounds`——
  文本用 `TextEncoder().encode()`，PNG 先 `blob.arrayBuffer()` 再包 `Uint8Array`。
- **PNG 导出防 NaN**：画布尺寸必须 `isFinite && >0`，画布 0 尺寸时 `toBlob` 返回 null 零报错。
- **`exportZip` 只打包当前页角色**：双角色要翻页各导一次。
- **编码**：`Editor.html` 是 **UTF-8（无 BOM）**，标题等中文均为正常 UTF-8 字节。改动时保持
  UTF-8 写入，**勿用 ANSI/GBK 编码覆盖写**（否则中文会变乱码）。

## 测试 / 验收

- 语法：`node --check skill/character-generation-skill/app/chars/*.js`
- 功能回归（162 项）：`python tests/verify.py`（Playwright，产物在 `tests/_artifacts/`）
- 一致性自查：`python tests/bbox_check.py`（默认只报告不阻断；`--strict` 时违例退出码 1）
- 无头测试的坑（加载两条通道 / 无头 alert 挂死 / 点击后 DOM 重建）见 [`tests/README.md`](tests/README.md)。

## Git 提交规范

- **格式 `type: 中文摘要`**：type 按**本次主要改动**选（一个提交以修 bug 为主就写 `fix`，不堆多个前缀），
  摘要用中文、结尾不带句号：

  | type | 何时用 |
  |---|---|
  | `feat` | 新功能：加角色、加挂件、编辑器新交互 |
  | `fix` | 修 bug：渲染 / 导出 / 交互缺陷、坐标越界 |
  | `docs` | 只改文档（SKILL.md、format-spec.md、本文件等） |
  | `refactor` | 不改行为的整理：改名、挪结构 |
  | `test` | 只改 `tests/` |
  | `chore` | 杂项：重命名、清理、配置 |

- **一个任务一个提交**：一次会话有多个功能改动时**分批提交**，同一次提交只装**同一个任务**的改动
  （例：「新增角色 X」的角色文件一个 `feat:` 提交；「编辑器修 bug」另起一个 `fix:` 提交——即使同天完成）。
  为该任务顺手改的测试 / 文档可随该任务一起提交。
- **拆分手法**：按文件 `git add <路径>` 分批暂存；同一文件混了两个任务的改动用 `git add -p` 按 hunk 拆；
  提交前 `git diff --staged` 复核暂存区只含本任务内容。

## 常见命令速查

```bash
# 语法检查
node --check skill/character-generation-skill/app/chars/girl.js

# 一致性 + 功能回归
python tests/bbox_check.py --strict
python tests/verify.py

# 分批提交：按任务分批暂存，同一任务的改动一起提交
git add skill/character-generation-skill/app/chars/<角色名>.js
git commit -m "feat: 新增角色 <角色名>"

# 交付物 = app/ 整个目录（html 与 chars/ 一起交付）
```

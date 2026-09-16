# character-generation-skill tests · 开发与验收工具

本目录脚本服务于 character-generation-skill **本身的开发与验收**——改 `app/Editor.html`、批量改角色、
排查行为问题时防回归用。只是「用工具做角色 / 加角色 / 导出素材」的话，不需要本目录。

## 环境依赖（两个脚本一致）

- Python 3.9+ 与 playwright：`pip install playwright`
- 浏览器优先用系统 Edge；没有 Edge 自动退回 Playwright chromium（需先 `playwright install chromium`）
- 用法：`python <脚本> [Editor.html 所在目录]`，缺省 = 仓库自带 `app/`
- verify.py 的产物（截图 / 下载包 / 往返页）写在 `tests/_artifacts/`，可随时删

## verify.py — 功能回归（162 项）

覆盖：加载成功 / 拼装非空 / 三组卡片数 / 文件名标注（随 PNG 尺寸倍率）/ 身体套装整体切换 /
表情与头部单选 / 挂件同类替换·跨类并存·反选 / ZIP 下载解包验 PNG 魔数与文件数 /
编辑器（打开·锚点移动·≥5 步撤销重做·保存直写·override 生效·补丁行写回·往返加载·
颜色修改·形状增删·锚点/手柄增删·De Casteljau 细分几何）/ 预览拖动体系（跟手·松手不跳位·
越界作废弹回·启动重置·静默写盘）/ PNG 尺寸倍率门闩（含真实导出尺寸断言）/ 来源路径行三种格式 /
chars/ 下潜与 FSA 直写。

**改 Editor.html 或批量改角色后应跑一遍**；写新测试可仿照它裁剪。

## bbox_check.py — 一致性自查

- 同 style 基础件（head + body 五件；faces/attachments 不参与）bbox 宽高两两对比 ≤20%
  + 画布贴边/越界清单。
- **默认只报告不阻断**；加 `--strict` 时 20% 违例使退出码为 1。
- 例外政策：发型还原度等有意取舍（如垂发 vs 短发）可豁免——自带样例 girl/boy 有 6 处
  已知违例（双马尾头宽 +33%、男外套躯干 +38% 等），属保留还原度的设计决定。

## 页面自动化钩子（Editor.html「自动化 / LLM 调试钩子」区）

- `__CHARFORGE__.chars / texts / names / errors / srcDir / dirHandle`——注册器与状态
- `__CHARFORGE__.renderAll()`——强制重渲染
- `__CHARFORGE__._items(def)`——全部可导出资源清单 `[{item, key, base, label}]`
- `__CHARFORGE__.measure(def, item, key)`——部件紧凑 bbox（含缓存）
- `__CHARFORGE__.getEd()` / `.edApi`——编辑器自动化
  （select/move/push/undo/redo/addShape/delShape/addPt/delPt/addHandle/delHandle/setFill/setStroke）
- `__CHARFORGE__.sanitizePos(def)`——越界位移重置逻辑（拖动体系用）

## 无头测试已踩过的坑

- **加载角色两条通道**：手选 = `set_input_files('#addFiles', [<.js 路径数组>])`；
  FSA = 注入 fake 目录句柄（**必须带 `name` 属性**，路径行显示要用），
  保存 / 「选择路径」注入 fake `showDirectoryPicker`（写法见 verify.py 第 13/15 节），断言直写且零下载事件。
- **无头模式 `alert()` 会挂死**：必须挂 `page.on('dialog', dismiss)`。
- **别嵌套 `sync_playwright`**（第二次进入同进程报 asyncio loop 错）：
  多场景复用同一 browser 实例开 `new_context()`；`b.close()` 之前跑完所有页面。
- **点击卡片后 DOM 全部重建**（renderAll）：别抓元素句柄循环点击，会报
  `Element is not attached`——在页面内 `querySelectorAll(...).click()` 一次性完成。
- **`exportZip` 只打包当前页角色**：验证双角色要翻页各导一次
  （每次文件数 = 头部套数+表情数+身体套数×5+挂件数，SVG/PNG 各一份，另加整体 2 件）。

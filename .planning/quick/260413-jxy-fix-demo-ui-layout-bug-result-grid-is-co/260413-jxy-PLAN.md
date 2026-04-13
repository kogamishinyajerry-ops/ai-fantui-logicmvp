---
phase: quick
plan: 260413-jxy
type: execute
wave: 1
depends_on: []
files_modified:
  - src/well_harness/static/demo.css
autonomous: true
requirements:
  - FIX-LAYOUT-OVERLAP-01

must_haves:
  truths:
    - "result-grid (推理结果区) 不再被 sticky chain-panel 遮盖"
    - "chain-panel 保持 sticky 行为，右列从头到底贴屏顶"
    - "左列：lever-panel 上方，result-grid 下方，垂直堆叠"
    - "小屏（≤1100px / ≤780px）响应式布局保持单列，area 名称一致"
  artifacts:
    - path: src/well_harness/static/demo.css
      provides: "修正后的 showcase-grid 布局"
      contains: '"result chain"'
  key_links:
    - from: ".showcase-grid grid-template-areas"
      to: ".result-grid"
      via: "grid-area: result"
      pattern: 'grid-area:\s*result'
---

<objective>
修复 demo UI 布局 bug：`.result-grid` 在滚动时被 sticky `.chain-panel` 遮盖。

Purpose: 推理结果区（.result-grid）当前位于 grid-area "answer"（第二行，全宽），
而右列的 .chain-panel 设置了 `position: sticky; top: 10px`，导致滚动时
chain-panel 浮在 result-grid 之上，用户看不到结果。

Output: 修改 demo.css，将 result-grid 移至左列（lever-panel 下方），
与右列 sticky chain-panel 并排，彻底消除遮盖问题。
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@src/well_harness/static/demo.css
@src/well_harness/static/demo.html
</context>

<tasks>

<task type="auto">
  <name>Task 1: 修改 showcase-grid CSS 布局，消除 sticky chain-panel 遮盖</name>
  <files>src/well_harness/static/demo.css</files>
  <action>
在 demo.css 中执行以下 4 处精确修改（CSS-only，不动 HTML）：

**修改 1 — 主布局 grid-template-areas（约 line 322-325）：**
将：
```css
  grid-template-areas:
    "prompt chain"
    "answer answer";
```
改为：
```css
  grid-template-areas:
    "prompt chain"
    "result chain";
```
说明：result-grid 现在占据第二行左列，chain-panel 占据整个右列（从第一行延伸到第二行）。

**修改 2 — .result-grid grid-area 声明（约 line 331）：**
将：
```css
.showcase-grid .result-grid { grid-area: answer; }
```
改为：
```css
.showcase-grid .result-grid { grid-area: result; }
```

**修改 3 — 响应式 ≤1100px breakpoint（约 line 2062-2067）：**
将：
```css
  .showcase-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "prompt"
      "chain"
      "answer";
  }
```
改为：
```css
  .showcase-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "prompt"
      "chain"
      "result";
  }
```

**修改 4 — 响应式 ≤780px breakpoint（约 line 2192-2197）：**
将：
```css
  .showcase-grid {
    grid-template-areas:
      "prompt"
      "chain"
      "answer";
  }
```
改为：
```css
  .showcase-grid {
    grid-template-areas:
      "prompt"
      "chain"
      "result";
  }
```

不修改任何其他 CSS 规则，不改动 demo.html，不改动 .chain-panel 的 sticky 行为。
  </action>
  <verify>
    <automated>
grep -n 'grid-area' "/Users/Zhuanz/20260407 YJX AI FANTUI LogicMVP/src/well_harness/static/demo.css" | grep -E 'result|answer|chain|prompt'
    </automated>
  </verify>
  <done>
- demo.css 中不再出现 `grid-area: answer` 或 `"answer answer"` 字符串
- 主布局 grid-template-areas 第二行为 `"result chain"`
- .result-grid 的 grid-area 为 `result`
- 两个响应式 breakpoint（≤1100px、≤780px）中 area 名称均为 `result`（单列布局时保持垂直堆叠顺序）
- chain-panel 的 `position: sticky` 保持不变
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| static CSS | 纯样式文件，无动态输入，无安全边界 |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-quick-01 | Tampering | demo.css | accept | CSS-only 修改，无逻辑变更，无安全风险 |
</threat_model>

<verification>
1. 在浏览器访问 http://localhost:7890/
2. 向下滚动页面，确认 .result-grid（推理结果区）出现在左列 lever-panel 下方
3. 确认 sticky chain-panel 停留在右列，不遮盖左列 result-grid
4. 缩窄浏览器到 ≤1100px，确认单列布局顺序正确（prompt → chain → result）
</verification>

<success_criteria>
- demo.css 中 `grid-area: answer` 已替换为 `grid-area: result`
- 主 grid-template-areas 第二行为 `"result chain"`（非 `"answer answer"`）
- 两处响应式 breakpoint area 名称对应更新
- 无其他 CSS 规则改动
</success_criteria>

<output>
完成后创建 `.planning/quick/260413-jxy-fix-demo-ui-layout-bug-result-grid-is-co/260413-jxy-SUMMARY.md`

内容包含：
- 修改的文件和具体行号
- 4 处 CSS 变更摘要
- 验证结果
</output>

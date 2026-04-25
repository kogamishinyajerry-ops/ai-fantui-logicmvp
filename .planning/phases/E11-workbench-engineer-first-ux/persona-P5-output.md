PERSONA: P5 (HUANG Jianhua, Apps Engineer, customer-facing)
VERDICT: CHANGES_REQUIRED

## Reproduction outcome
我先按客户话术做 landing config 探针：`TRA=-32`, `RA=2 ft`, `engine_running=true`, `aircraft_on_ground=true`, `reverser_inhibited=false`, `eec_enable=true`, `n1k=35`, `feedback_mode=auto_scrubber`。结果没有复现“L4 灰灯”。服务端返回 `time_s=4.4`, `deploy_position_percent=100.0`, `deploy_90_percent_vdt=true`, `logic2=true`, `logic3=true`, `logic4=true`, `thr_lock=true`，摘要直接写的是“L4 已满足，THR_LOCK release command 已触发”。

客户抱怨只在 `manual_feedback_override` 且 `deploy_position_percent < 90` 时才像他说的那样出现。我用 `deploy_position_percent=50` 复跑，返回 `effective_tra=-14.0`（深拉区被锁住）、`deploy_90_percent_vdt=false`, `logic4=false`, `thr_lock=false`，摘要明确写“L4 还在等待 deploy_90_percent_vdt”。所以这单我不会先报 controller bug，我会先追问客户他们的 simulator 显示的是不是 manual override 路径，而不是 auto scrubber。

## Customer hand-off readiness 1-line summary
with-friction - 我能在 30 分钟内人工拼出 ticket，但 `/workbench` 不是一个能直接给客户截图、给工程队交票、并避免误诊的单一工作面。

## Findings (5-10 numbered, severity BLOCKER|IMPORTANT|NIT)

1. [BLOCKER] `/workbench` surface - 这页不是客户症状复现台，而是 P7 bundle/archive 验收台。
   Customer scenario where this hurts: 客户说“L4 灰灯”，我打开 `/workbench` 却看到 annotation、approval、archive，不会先看到 TRA/RA/VDT 复现控件，30 分钟窗口已经浪费掉。
   Suggested mitigation: 在 `/workbench` 直接挂一个 symptom reproduction panel，至少能调 `TRA / RA / on_ground / feedback_mode / deploy_position_percent`，并显示服务端原始 verdict。

2. [BLOCKER] feedback_mode disambiguation - 页面没有清楚显示当前快照到底是 `auto_scrubber` 还是 `manual_feedback_override`，也没解释两者差异。
   Customer scenario where this hurts: 客户给我一张 simulator 手机图，我如果转发“L4 灰灯是 bug”，开发会回问“你跑的是哪种 feedback_mode”，这张票要重写。
   Suggested mitigation: 把当前 `feedback_mode` 做成常驻 badge，并附一句业务话说明：`auto_scrubber` 会在单次快照内把 VDT 推到约 4.4s / 100%，`manual_feedback_override` 取决于人工给的 deploy feedback。

3. [IMPORTANT] screenshot cleanliness - 当前页面默认可见 top bar、annotation toolbar、Approval Center，而且还有 expert/dev 工具入口，不是可直接转客户的干净画面。
   Customer scenario where this hurts: 如果我把这张图发给客户，对方第一句会问“Approval Center 是什么，为什么你们在看内部审签面板？”
   Suggested mitigation: 给 `/workbench` 增加 `customer_view` 或 `clean_capture` 模式，一键隐藏 annotation / approval / JSON / expert chrome，只保留复现参数和结果卡。

4. [IMPORTANT] reproduction recipe export - 现在能导出的是 workbench browser workspace，不是这类症状的一键复现 recipe；URL `intake=` 也只带 packet，不带 lever/feedback 参数。
   Customer scenario where this hurts: 我想让客户在他们本地重跑“TRA=-32, RA=2, manual override=50”时，没法直接发一个短 URL 或 JSON recipe，对方只能抄参数。
   Suggested mitigation: 为 symptom reproduction 单独生成 shareable URL / JSON，至少固化 `tra_deg`, `radio_altitude_ft`, `feedback_mode`, `deploy_position_percent` 和服务端返回摘要。

5. [IMPORTANT] ticket payload fidelity - 当前 ticket payload 没有客户原话字段，也没有复现参数、服务端响应快照、截图路径。
   Customer scenario where this hurts: 客户原邮件是“L4 in our airline's simulator stays gray...”，如果我转给开发后只剩一个 generic proposal note，团队会重新问我客户到底怎么说的。
   Suggested mitigation: ticket schema 里强制带 `customer_quote`, `repro_recipe`, `observed_response`, `engineer_assessment`, `screenshot_refs`。

6. [IMPORTANT] similar-case lookup - 页面只有最近 6 个 archive 恢复，没有 past tickets / duplicate search。
   Customer scenario where this hurts: 如果这是上周已经调查过的 “manual override<90 keeps L4 gray” 老问题，我现在看不出来，只能再做一遍重复劳动。
   Suggested mitigation: 至少按 `system + symptom + logic gate + feedback_mode` 做本地 searchable index，把相似 ticket / archive / verdict 拉出来。

7. [NIT] customer wording - 页面主文案还是 “bundle / clarification / archive / second-system onboarding”，不是客户故障语言。
   Customer scenario where this hurts: 如果我 forward 给客户，他们会问“clarification gate 跟我这盏 L4 灯不亮有什么关系？”
   Suggested mitigation: 给 P5 视角加一层 customer-language copy，把 “L4 灰灯 / THR_LOCK 未释放 / 深拉区未开放” 放到首屏。

## feedback_mode disambiguation check

Does the Workbench clearly show:
- which feedback_mode is currently active in the displayed snapshot? No.
- the difference between auto_scrubber (server-driven plant feedback) and manual_feedback_override? No.

This is CHANGES_REQUIRED. Apps engineers will mis-route customer issues if the page keeps these two paths混在一起。

## Anti-bias check

P1/P2/P3/P4 可能会盯着“controller 真值对不对”或“页面结构是否完整”。我这里会额外抓到的是：即便真值是对的，如果 ticket 里没有客户原话、没有可转发截图、没有 duplicate lookup，我每周都会把同一类客户邮件重新翻译一遍。这是 customer-facing 工程位的真实损耗，不是纯技术视角会先报出来的问题。

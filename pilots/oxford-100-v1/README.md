# 首批 100 词情景对话试验

日期：2026-10-22。范围由用户明确指定为 100 个词，目标是先验证“选词 → 义项 → 场景 → 文本 → 逐词证据 → 审核”的闭环，而不是直接生成完整课程。

## 从哪里开始看

- [selection.csv](selection.csv)：可用电子表格打开的跟踪表，每个词一行。
- [selection.json](selection.json)：权威结构化样本，保留来源目标 ID 和所有状态。
- [dialogues.md](dialogues.md)：编号英文对话、中文场景说明和逐词用法映射。
- `dialogues/*.json`：可供下一阶段程序使用的原始对话。
- [reviews.json](reviews.json)：独立 AI 审阅者的逐词判断，不是人工专家认证。
- [validation.json](validation.json)：可重新运行的形式校验结果，不能代替语义审核。

## 为什么选这 100 个词

先选可完成真实沟通任务的语义组，再从固定来源中找确实存在且词性吻合的词，并确定本次教学义项。样本不是按字母顺序取前 100 个，也不是随机抽样或按频率排名。选择涵盖具体事物、通用动作、抽象概念和容易混淆的常用义项，用以暴露流程问题。它不是已测定适合用户水平的正式课程。

来源固定为 `ppqun88-agent/wordlists@3043da14627ed3c6168b598479bc110ce6b34736`。同一词形有多条记录时，选与本批词性相符的最低来源等级记录；同等级按来源名称、目标 ID 稳定排序。源等级仅说明该词性记录，不能证明具体义项或整篇文章的 CEFR 难度。复数 ingredients、nuts 显式登记为对应词形的变体，不重复计数。

本批 100 个不同词形，来源记录分布 A1 21、A2 31、B1 16、B2 24、C1 8；Oxford3000 90 条、Oxford5000 10 条。这里只统计选中的记录，不把两个原始列表当成互斥词形集合。

10 个情景涵盖预订、报修、饮食沟通、交通、预算、调查证据、账单、同事反馈、社区设施、项目协调。当前每篇列出 10 个目标是便于审查的小批次编排，不是未来生产约束；下一批应允许不同场景承载不同数量词，不能为配额硬塞。辅助词可以超出目标清单；覆盖 100 词不意味着全文仅有 100 词，也不意味着全部 Oxford 义项已覆盖。

## 状态与复查

selected、assigned、written、formal_checked、semantic_reviewed 分列。formal_checked 由客观检查后写入；semantic_reviewed 表示已有审核，不等于审核通过，通过/退回以 reviews.json 为准；return_reason 保留退回原因。每个词引用具体场景和句子，可回查词性、语义与搭配。未通过不得假称已采纳完成。

运行：

```sh
python3 tools/pipeline.py import --source-dir ../wordlists-source
python3 -m unittest discover -s tests -v
python3 tools/check_pilot.py --pilot-dir pilots/oxford-100-v1 --targets build/targets.jsonl
python3 tools/render_pilot.py
```

导入校验固定来源哈希，完整候选清单仍只在被 Git 忽略的 build/ 下。形式检查核对 100 个唯一词形、来源记录、逐句词形、唯一分配、映射和审核记录完整性；语义由独立 AI 逐项读上下文核对。本批不宣称人工专家认证、学习效果验证、词典音标审定或用户掌握程度。

## 下一步与边界

先由用户试读若干篇，判断文本难度、场景兴趣及中文提示是否够用；反馈后修改对应句子与审核记录，再决定是否扩大。扩大时优先补未覆盖词性/义项与场景缺口，不按固定篇数铺量。音频暂缓，不调用付费 API，不引入外部表格服务。材料仅本仓库独立分支提交，不合并或部署。

文本和简短中文教学说明为原创。所选 100 词保留来源可追溯性，不重新分发完整 Oxford 词表或 PDF，不复制长篇词典释义。来源权利说明见 ../../docs/resource-integration.md；不能将 Oxford 原始内容宣称为 MIT。

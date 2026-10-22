# 分阶段情景对话生产结案

更新于 2026-10-22。本轮十二阶段均已走完分类、原创、独立审阅、修订和本地验收；“全部处置”不等于“全部接受”。

- 固定范围：5,062 个不同词形、6,187 条来源词性/等级记录。
- 已接受：5,061 / 5,062 个词形，其中首批 100 个原样保留；新十二阶段接受 4,961 个。
- 明确暂缓且未覆盖：1 个词形；尚未进入阶段处置的词形：0 个。分母未缩减。
- 可读材料：首批 10 篇，加十二阶段 1,131 篇，共 1,141 篇对话。接受状态只说明材料通过本轮检查，不代表学习者已经掌握。

## 从哪里开始阅读

[按主题与具体情景浏览](../corpus/staged-v1/scene-index.md) · [阶段总目录](../corpus/staged-v1/README.md) · [覆盖统计](../corpus/staged-v1/coverage.json) · [当前版本校验清单](../corpus/staged-v1/manifest.json)。

下表的正文、单词反查与最终审阅链接可对应到具体台词、选定义项和当前文件哈希。各阶段按来源等级与字母稳定分配工作量，**不是课程难度排序，也不是情景分类规则**。

| 阶段 | 分配词形 | 接受词形 | 对话 | 暂缓词形 | 对应来源记录 | 阅读与追踪 |
|---|---:|---:|---:|---:|---:|---|
| 首批试验 | 100 | 100 | 10 | 0 | 141 | [入口](../pilots/oxford-100-v1/README.md) · [分类与反查](../pilots/oxford-100-v1/classification.md) · [最终审阅](../pilots/oxford-100-v1/reviews.json) |
| phase-01 | 413 | 413 | 59 | 0 | 578 | [正文](../corpus/staged-v1/phase-01/dialogues.md) · [单词反查](../corpus/staged-v1/phase-01/words.md) · [最终审阅](../corpus/staged-v1/phase-01/reviews.json) |
| phase-02 | 414 | 414 | 60 | 0 | 601 | [正文](../corpus/staged-v1/phase-02/dialogues.md) · [单词反查](../corpus/staged-v1/phase-02/words.md) · [最终审阅](../corpus/staged-v1/phase-02/reviews.json) |
| phase-03 | 413 | 413 | 75 | 0 | 546 | [正文](../corpus/staged-v1/phase-03/dialogues.md) · [单词反查](../corpus/staged-v1/phase-03/words.md) · [最终审阅](../corpus/staged-v1/phase-03/reviews.json) |
| phase-04 | 414 | 414 | 89 | 0 | 575 | [正文](../corpus/staged-v1/phase-04/dialogues.md) · [单词反查](../corpus/staged-v1/phase-04/words.md) · [最终审阅](../corpus/staged-v1/phase-04/reviews.json) |
| phase-05 | 413 | 413 | 99 | 0 | 523 | [正文](../corpus/staged-v1/phase-05/dialogues.md) · [单词反查](../corpus/staged-v1/phase-05/words.md) · [最终审阅](../corpus/staged-v1/phase-05/reviews.json) |
| phase-06 | 414 | 414 | 83 | 0 | 487 | [正文](../corpus/staged-v1/phase-06/dialogues.md) · [单词反查](../corpus/staged-v1/phase-06/words.md) · [最终审阅](../corpus/staged-v1/phase-06/reviews.json) |
| phase-07 | 413 | 413 | 92 | 0 | 487 | [正文](../corpus/staged-v1/phase-07/dialogues.md) · [单词反查](../corpus/staged-v1/phase-07/words.md) · [最终审阅](../corpus/staged-v1/phase-07/reviews.json) |
| phase-08 | 414 | 414 | 105 | 0 | 460 | [正文](../corpus/staged-v1/phase-08/dialogues.md) · [单词反查](../corpus/staged-v1/phase-08/words.md) · [最终审阅](../corpus/staged-v1/phase-08/reviews.json) |
| phase-09 | 413 | 413 | 102 | 0 | 465 | [正文](../corpus/staged-v1/phase-09/dialogues.md) · [单词反查](../corpus/staged-v1/phase-09/words.md) · [最终审阅](../corpus/staged-v1/phase-09/reviews.json) |
| phase-10 | 414 | 413 | 119 | 1 | 432 | [正文](../corpus/staged-v1/phase-10/dialogues.md) · [单词反查](../corpus/staged-v1/phase-10/words.md) · [最终审阅](../corpus/staged-v1/phase-10/reviews.json) |
| phase-11 | 413 | 413 | 116 | 0 | 442 | [正文](../corpus/staged-v1/phase-11/dialogues.md) · [单词反查](../corpus/staged-v1/phase-11/words.md) · [最终审阅](../corpus/staged-v1/phase-11/reviews.json) |
| phase-12 | 414 | 414 | 132 | 0 | 450 | [正文](../corpus/staged-v1/phase-12/dialogues.md) · [单词反查](../corpus/staged-v1/phase-12/words.md) · [最终审阅](../corpus/staged-v1/phase-12/reviews.json) |
| 合计 | 5,062 | 5,061 | 1,141 | 1 | 6,187 | 首批与十二阶段互不重复计词形 |

每个已接受词形仅选择一个来源记录和在对话中实际使用的明确义项。表中的接受词形数在本轮也等于已选、已接受来源记录数，但不表示该词的全部词性、全部来源等级记录或全部词义均已覆盖。

## 全来源记录核对：不要把记录数当作词形数

固定来源提交为 `3043da14627ed3c6168b598479bc110ce6b34736`。结案核对逐一检查来源目标 ID、选用关系、词形互斥、最终接受记录和当前文件哈希，而不只把阶段总数相加。

**6,187 = 5,061 条已选且接受记录 + 1 条暂缓来源记录 + 1,125 条其他未选用记录。**

- 5,061 条接受记录对应 5,061 个不同词形，包含首批 100 条。
- 1 条暂缓记录对应上述 1 个未覆盖词形，不获得教材接受状态。
- 1,125 条其他记录属于已接受词形的额外来源词性/等级条目；本轮没有把它们另行作为目标验收。它们不是另外 1,125 个尚未完成的词形。
- 因而“未选用/未取得接受用例的来源记录”合计为 1,126，其中暂缓和额外未选记录必须分开。来源记录本身也不是词典中全部词义的穷尽清单。

机器统计的口径也要区分：带 `staged` 的已选/接受字段只算新十二阶段，原试验的 100 条仍另外统计，因此 `source_records_not_selected_in_staged_count` 不是全库未选记录数。全库未选用口径见 `other_unselected_source_target_count`，包含上述暂缓记录；`inventory_deferred_form_count` 只统计分批前暂缓，不能用它的 0 否认后续生产阶段记录的来源冲突暂缓。

原始完整来源清单、PDF、私有过程档案和逐 ID 核对台账未复制到公开教材目录。公开内容保留原创教材必要的来源引用、选定义项、最终审阅及汇总；来源与复现边界见[资源整合说明](resource-integration.md)和[词库来源](vocabulary-sources.md)。

## 暂缓清单与来源问题

可单独下载或用表格软件读取[暂缓项处置清单（UTF-8 CSV）](staged-deferred-dispositions.csv)。此清单只记录当前未覆盖项、来源引用与后续处置，不包含私有原始词库或过程审计档案。

| 词形 | 来源目标 ID | 所属阶段 | 类别与处置 |
|---|---|---|---|
| diplomatic | ox-8bf56a9ac5e0f019 | phase-10 | source_pos_conflict：固定上游名词标注与同源形容词释义冲突；未覆盖，保留待来源勘误与显式迁移。 |

`diplomatic` 的固定来源追踪：[`data/en/archive/Oxford.json` 第 3630 行](https://github.com/ppqun88-agent/wordlists/blob/3043da14627ed3c6168b598479bc110ce6b34736/data/en/archive/Oxford.json#L3630) 为 C1 名词记录；[`data/en/definitions.json` 第 6302 行](https://github.com/ppqun88-agent/wordlists/blob/3043da14627ed3c6168b598479bc110ce6b34736/data/en/definitions.json#L6302) 给出形容词标记与释义。两份固定 Oxford5000 PDF 的第 3 页也印作名词。独立复核检查了原始字节、PDF 文字与画面、上游解析代码和本仓库导入器；解析链保留已有的名词标注，没有把形容词转换成名词。因此定位为固定上游注记异常，而不是本仓库提取时新引入的词性错误。 上游 [`tools/oxford.py`](https://github.com/ppqun88-agent/wordlists/blob/3043da14627ed3c6168b598479bc110ce6b34736/tools/oxford.py) 的解析与词性规范化保留 `n.`，再合并两份 PDF 的相同记录；本仓 [`tools/pipeline.py`](../tools/pipeline.py) 的 `import_source` 校验固定来源哈希后读取 `rec[0]`，并用来源组、词形、等级和原始记录计算目标 ID，独立重算仍得到 `ox-8bf56a9ac5e0f019`。没有重新导出或篡改原始来源。

本轮没有修改固定来源、强行采用罕见名词解释，或把普通形容词用法计作该名词目标的覆盖。后续若处理此项，需要另行核对来源勘误、明确版本及目标 ID 迁移，再原创用例、独立审阅和验收；不能直接把暂缓状态改为接受。[第十阶段记录](../corpus/staged-v1/phase-10/production-notes.md)保留这一边界。

## 审阅指标及其证据边界

审阅由与作者不同的 AI 审阅者完成，逐篇通读并逐目标说明理由，绑定具体文件字节的 SHA-256。作者修订后，由原独立审阅者重新完整阅读受影响对话和每个目标；不能只换哈希。标题、情景标签、目标、实体、说话人、材料范围及讨论/请求/承诺/约定/完成状态都属于核查范围。

**第一至第六阶段没有完整保存的全阶段初稿与初审档案，严格首轮整篇通过率无法从现存档案独立重建。** 早期生产记录记载的修订对话数依次为 2、3、5、7、6、0；这些历史数不是首轮接受率，也不能从第六阶段“修订 0 篇”反推首轮全部通过。最终接受记录只证明记录对应的最终版本通过了本轮审阅。

第七至第十二阶段保存了完整初稿及三组完整初审记录，可以在本次工作区按原始/当前哈希重新计算以下数据。过程档案未随公开仓库发布；公开最终 reviews.json 与 manifest 可核对当前版本，但不能单独重建未公开的首轮历史。

| 阶段 | 首轮整篇通过 | 首轮可用目标 | 个别词汇拒绝 | 公开文件修订数 | 复审目标（去重） |
|---|---:|---:|---:|---:|---:|
| [phase-07 记录](../corpus/staged-v1/phase-07/production-notes.md) | 87/92（94.6%） | 392/413（94.9%） | 1 | 5 | 21 |
| [phase-08 记录](../corpus/staged-v1/phase-08/production-notes.md) | 82/105（78.1%） | 321/414（77.5%） | 2 | 23 | 93 |
| [phase-09 记录](../corpus/staged-v1/phase-09/production-notes.md) | 88/102（86.3%） | 357/413（86.4%） | 0 | 14 | 56 |
| [phase-10 记录](../corpus/staged-v1/phase-10/production-notes.md) | 110/119（92.4%） | 382/413（92.5%） | 0 | 9 | 31 |
| [phase-11 记录](../corpus/staged-v1/phase-11/production-notes.md) | 106/116（91.4%） | 376/413（91.0%） | 1 | 7 | 37 |
| [phase-12 记录](../corpus/staged-v1/phase-12/production-notes.md) | 119/132（90.2%） | 372/414（89.9%） | 0 | 8 | 42 |

“首轮可用目标”要求整篇对话与该篇全部个别目标同时通过；个别词汇用法正确，不能抵消整篇拒绝。分母为实际进入首轮审阅的目标，第十阶段的 1 个暂缓项没有进入该分母，但始终保留在总体 5,062 分母中。

公开文件修订按初稿与最终对话字节差异计数；私有结果证据纠错不自动增加该数。第十一阶段修改 7 个公开文件、涉及 28 个目标，另有 3 个仅证据修订；实际完整复审为 10 篇、37 个不同目标。复审目标列去重计数，不是复审轮次或累计阅读次数。第十二阶段实际修改 8 个公开文件，涉及 26 个目标；完整复审 13 篇、42 个目标，其中 5 篇公开字节未变。具体原作者修订与证据问题见各行生产记录。

从第九阶段起的条款级自检记录只帮助表达与核对主张；结构检查不证明语义正确。不同阶段指标如实报告，不能据此推断自检清单造成质量改善，更不能用最终接受率替代初审成绩。独立 AI 判断仍可能漏错，**不是人工语言专家认证**。

## 本地验收、保留范围与后续边界

最终阶段完成严格生成、无写入复验、92 项单元测试，以及原 100 词试验和分类检查。此前冻结教材保持原样；后期修订只作用于当时尚未冻结的本阶段文件。当前接受记录全部对应当前文件字节，未审阅、拒绝和暂缓项不计覆盖。

本轮只完成文本及其追踪材料，没有生成音频、开发或部署应用、合并分支，也不声称远端 CI 成功。后续首先单列处理上述来源冲突；若扩大到更多义项、人工抽检、音频或应用，应作为新的明确范围，不能把本次单义项覆盖当作那些工作已完成。原执行规则见[分阶段生产计划](staged-production.md)。

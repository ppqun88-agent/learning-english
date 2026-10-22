# 情景分类与义项映射规范

## 当前可读入口与范围

[主题目录与单词反查](../pilots/oxford-100-v1/classification.md)覆盖首批已有的 100 个目标词形、100 个选定义项和 10 篇对话。共 7 个主题大类、10 个具体情景；这是可扩展的起点，不是完整 Oxford 词库分类，也不声称其他义项已覆盖。

原始 selection.json / CSV、dialogues/*.json、dialogues.md、reviews.json 和既有覆盖记录原样保留。新增分类层不改句子、不增加新词或音频，不调用付费 API，不覆盖语义审核。

## 三层身份，不把单词锁死在一个场景

1. 主题 topic：较宽的生活或沟通领域，例如“出行与住宿”。
2. 情景 scenario：可复用的具体沟通任务，例如“修改旅馆预订”。情景归属一个主题；不同批次的多篇对话可以复用同一情景。一篇对话可以关联多个情景，只有实际需要时才添加。
3. 义项 sense：来源 target_id + 词性 + 本次教学含义，以稳定 sense_id 区分。来源 target_id 不是义项 ID，不能假定同一词性只存在一种意思。一个义项可以关联多个情景；一个情景可以关联多个义项。

例如 bank 在本批指“银行”，不是“河岸”；statement 指“银行账单”，不是一般声明；argument 指“论证”，不是争吵。将来新增另一义项时创建新的 sense_id，保留来源 target_id，不修改或覆盖旧义项。

情景 ID 与对话 ID 分离：accommodation-change 是情景，pilot01-booking 是一篇具体对话。不要从旧 scene_id 字段推断永久类别；它在原试验中实际保存对话 ID。

## 事实与建议严格分开

- attested：已有目标映射支持的用例，必须含 dialogue_id 和 sentence_ids，并落在该对话已登记的情景内。只从既有目标映射继承，不因为辅助词碰巧出现就自动计入覆盖。
- suggested：同一义项可以自然使用的候选情景，必须写 rationale_zh，禁止附 evidence。当前有 8 条示范性建议，不是穷举、不代表已写对话或已审用法，不计覆盖，不承诺补写。

例如 date（日期）已有旅馆预订用例，项目交付是建议关联；access（进入的机会或权限）已有报修用例，公共空间是建议关联。不会为了把建议变成“已覆盖”而强塞词或规定重复次数。

一条义项—情景关联保存一个状态。若以后已有用例替代建议，将状态改为 attested 并添加真实逐句证据；不同情景仍可处于不同状态。一个已有关联可以包含多篇对话的证据，不按篇数或重复次数增加独立词形覆盖率。校验输出的 attested_evidence_link_count 统计关联证据条目，同一用例可在不同情景关联下计入多次；它不是独立用例数或词形覆盖数。

## 文件与权威来源

- data/scene-taxonomy.json：主题及具体情景字典。
- pilots/oxford-100-v1/classification.json：对话归类、义项身份及多对多关联。
- schemas/scene-taxonomy.schema.json、schemas/classification.schema.json：JSON Schema 2020-12 结构契约。
- tools/classify_pilot.py：离线结构与引用校验，生成可读目录和按字母排序的单词反查。仅实现上述 schema 实际使用的有限关键字，不是通用 JSON Schema 引擎；不联网、不需第三方包。
- selection.json、dialogues/*.json：既有目标选择与逐句证据仍是权威来源；新分类不重新计算语义审阅结论。

已有 100 个选定义项带 pilot_id，必须逐项匹配原始目标、词性、中文义项和证据，不能遗漏或重复。未来同一来源词的其他义项可以省略 pilot_id，使用新 sense_id；本版本对不带 pilot_id 的新增义项强制只允许 suggested，防止借用同一来源词其他义项的证据。要升级为 attested，须先增加独立的义项级审阅与证据绑定机制，不能直接复用原目标映射。增加新来源目标或批次需要单独扩展该批次范围及校验，不可偷偷扩大当前 100 词的分母。

旧 check_pilot.py 的“exactly once”只冻结原试验选词分配，防止误改已有台账，不是通用分类约束。新分类校验和测试允许一个义项关联多个情景、同一情景关联多篇对话、同一来源目标具有不同义项。将来扩批时另建可支持多用例的选择台账，不把旧试验检查器当成全量课程规则。

## 校验和维护

从仓库根目录运行：

```sh
python3 tools/classify_pilot.py --write
python3 tools/classify_pilot.py
python3 -m unittest discover -s tests -v
python3 tools/check_pilot.py --targets build/targets.jsonl
```

前三条只需仓库文件。最后一条需按 resource-integration.md 从固定来源本地导入 build/targets.jsonl；完整候选词库仍不发布。

检查包括 schema 形状、重复身份、未知主题/情景/对话/目标、义项一致性、原证据保留、建议与事实分离、可读页是否过期。测试使用合成夹具证明多对多结构，不把测试夹具写入教材。结构通过不能证明新语境语义正确，也不能证明用户已经掌握。

添加或调整分类时先确认沟通任务，再复用或创建稳定情景 ID；修改分类文件后重新生成目录并运行测试。已有文本若确需修改，应按原工作流另做语义审阅和证据核对。不要用词性、CEFR 或主题标签代替具体语义判断。

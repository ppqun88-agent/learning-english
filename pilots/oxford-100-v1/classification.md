# 首批情景分类与单词反查

范围：现有 100 个目标词形、100 个已选义项、10 篇对话。不是全量 5,000 词分类。

按主题找情景；按单词找具体义项和原句。建议关联不是已有用例，不计覆盖，不要求补写或重复。

结构与扩展规则见 [分类规范](../../docs/scene-classification.md)。本页由 tools/classify_pilot.py 生成。

## 主题与具体情景

### 出行与住宿

交通、住宿及行程沟通

- 修改旅馆预订（accommodation-change）：调整入住日期并确认房型与到店安排。
  - 对话：[修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)
- 改用替代交通（transport-alternative）：错过火车后询问路线、票价及换乘。
  - 对话：[错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)

### 居家生活

居住环境、设施与维修

- 报修漏水（home-repair）：说明漏水情况并约定安全检查与维修。
  - 对话：[报修漏水](dialogues.md#报修漏水-pilot01-repair)

### 饮食沟通

点餐、配料与饮食需求

- 沟通饮食限制（dietary-needs）：核对配料并沟通食物过敏与交叉接触担忧。
  - 对话：[有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)

### 工作与协作

项目、活动、协作及反馈

- 调整活动预算（event-budget）：比较场地方案并明确预算取舍。
  - 对话：[团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)
- 反馈与修改草稿（draft-feedback）：提出可操作反馈并协商修订安排。
  - 对话：[给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)
- 协调项目交付（project-delivery）：澄清依赖、范围、风险与承诺。
  - 对话：[协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)

### 研究与论证

调查、证据与推理边界

- 讨论调查证据（survey-evidence）：核对样本、局限与结论的依据。
  - 对话：[讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)

### 消费与服务

账单、订阅及消费争议

- 核对账单与争议（billing-dispute）：核对不熟悉的扣费并询问后续处理。
  - 对话：[核对银行账单](dialogues.md#核对银行账单-pilot01-bank)

### 社区与公共空间

公共空间、使用需求及维护

- 讨论公共空间方案（public-space-planning）：讨论社区公园的可达性与维护责任。
  - 对话：[讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)

## 单词 → 义项 → 情景 → 对话原句

按字母排序；来源目标 ID 保留在 classification.json 和 selection.json 中。

### access · n. · 进入的机会或权限

义项 ID：p01-w018-sense01；来源目标：ox-c61f1fbf5c474097。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s05：I can give the plumber access tomorrow morning.
- 建议关联（未覆盖）：社区与公共空间 / 讨论公共空间方案。公共空间设计也涉及进入的机会或权限。

### accurate · adj. · 准确的

义项 ID：p01-w060-sense01；来源目标：ox-9513cbba3e62a8d2。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s06：Let us include that distinction in the report so the claim is accurate.

### affect · v. · 影响

义项 ID：p01-w046-sense01；来源目标：ox-c4e7f4158270d4a8。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s03：Would that affect the quality of the event?

### alternative · n. · 替代方案

义项 ID：p01-w095-sense01；来源目标：ox-6eec8b4a761015f2。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s03：Is there an alternative if it does not arrive?

### amount · n. · 金额

义项 ID：p01-w064-sense01；来源目标：ox-3b408396df4a85bf。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s02：Let us check the amount and the name of the company.

### annual · adj. · 每年的

义项 ID：p01-w065-sense01；来源目标：ox-9bb001bfdec9b46e。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s03：It might be my annual subscription, but I thought I had cancelled it.

### appointment · n. · 约定的会面时间

义项 ID：p01-w020-sense01；来源目标：ox-e0354eeffdbd81ed。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s06：Thank you. I will confirm the appointment this afternoon.

### argument · n. · 论证（支持观点的理由）

义项 ID：p01-w076-sense01；来源目标：ox-635cb3b553a111cb。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s04：That is helpful feedback. I was worried that the argument was too brief.

### assess · v. · 评估

义项 ID：p01-w100-sense01；来源目标：ox-599f976dc5971f83。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s06：Agreed. I will assess the impact and send you a realistic timeline.

### assume · v. · 假定

义项 ID：p01-w056-sense01；来源目标：ox-4bc0db422b07e127。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s04：Then we should not assume that cycling caused the difference.

### bank · n. · 银行

义项 ID：p01-w062-sense01；来源目标：ox-e1c642934b59a706。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s01：There is a charge on my bank statement that I do not recognize.

### benefit · n. · 好处

义项 ID：p01-w073-sense01；来源目标：ox-cb7d0a1764dfa56b。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s03：Please explain the benefit to the reader and remove the repeated examples.

### bread · n. · 面包

义项 ID：p01-w023-sense01；来源目标：ox-e18d77e7a1872301。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s01：Shall we share a salad and some bread?

### breakfast · n. · 早餐

义项 ID：p01-w005-sense01；来源目标：ox-a50881cdc4c327d3。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s03：A single room, please. Is breakfast included in the price?

### brief · adj. · 简短的

义项 ID：p01-w077-sense01；来源目标：ox-555badd8cb69cf1e。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s04：That is helpful feedback. I was worried that the argument was too brief.

### budget · n. · 预算

义项 ID：p01-w041-sense01；来源目标：ox-61c635a60158d8f1。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s01：Our budget is limited. Which expense can we reduce?

### charge · n. · 扣收的费用

义项 ID：p01-w061-sense01；来源目标：ox-51c7b82de58458f5。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s01：There is a charge on my bank statement that I do not recognize.

### chef · n. · 厨师

义项 ID：p01-w029-sense01；来源目标：ox-67ec5e876036e824。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s05：Thank you. Could you also check with the chef about cross-contact?

### commitment · n. · 承诺

义项 ID：p01-w099-sense01；来源目标：ox-70bcd2a2ebd16b9c。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s05：Let us clarify the scope before we make a commitment.

### community · n. · 社区

义项 ID：p01-w083-sense01；来源目标：ox-36b8b08ad851b155。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s02：Yes. We want to create a space that the whole community can enjoy.

### compare · v. · 比较

义项 ID：p01-w049-sense01；来源目标：ox-154a8d39cf6abd3e。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s05：Then let us compare the options before we make a decision.
- 建议关联（未覆盖）：出行与住宿 / 改用替代交通。可比较不同交通方案。

### component · n. · 部件

义项 ID：p01-w094-sense01；来源目标：ox-7f16e25407f37792。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s02：There is a risk. We depend on a supplier for one component.

### concern · n. · 担忧

义项 ID：p01-w030-sense01；来源目标：ox-4724dcfa60c8e29d。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s06：Certainly. I will explain your concern before you order.
- 建议关联（未覆盖）：居家生活 / 报修漏水。报修时可表达安全担忧。

### conclusion · n. · 结论

义项 ID：p01-w053-sense01；来源目标：ox-81c1d1f2fe0c87f4。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s02：What evidence supports that conclusion? How large was the sample?

### confirm · v. · 确认

义项 ID：p01-w019-sense01；来源目标：ox-6de7025ea439fa72。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s06：Thank you. I will confirm the appointment this afternoon.

### confirmation · n. · 确认信息

义项 ID：p01-w010-sense01；来源目标：ox-87f2ab6602e3fe93。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s06：Certainly. I will send you a confirmation by email.
- 建议关联（未覆盖）：居家生活 / 报修漏水。维修预约可以需要书面确认信息。

### contain · v. · 含有

义项 ID：p01-w026-sense01；来源目标：ox-03a6827e7887e555。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s03：Excuse me, does the dressing contain any nuts?

### damage · n. · 损坏

义项 ID：p01-w090-sense01；来源目标：ox-404a091df68c9929。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s06：The council. We will publish a schedule and invite residents to report any damage.

### date · n. · 日期

义项 ID：p01-w002-sense01；来源目标：ox-5bd31d3e75d105f5。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s01：I have a reservation for Friday, but I need to change the date to Saturday.
- 建议关联（未覆盖）：工作与协作 / 协调项目交付。交付安排也需要明确日期。

### decision · n. · 决定

义项 ID：p01-w050-sense01；来源目标：ox-e36818f27c626e6d。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s05：Then let us compare the options before we make a decision.

### delay · n. · 延误

义项 ID：p01-w040-sense01；来源目标：ox-bb9872b1e698f9a2。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s06：It is direct. Allow extra time because there is a delay on the main road.

### depend · v. · 依赖

义项 ID：p01-w092-sense01；来源目标：ox-cb87074e3038b571。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s02：There is a risk. We depend on a supplier for one component.

### design · n. · 设计

义项 ID：p01-w093-sense01；来源目标：ox-1a8f34c9f5a2b6cc。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s04：Yes, but we need permission to change the design. That is a separate requirement.

### direct · adj. · 直达的

义项 ID：p01-w037-sense01；来源目标：ox-d18d31dec05cdc15。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s05：Is the service direct, or do I need to transfer?
  - pilot01-journey-s06：It is direct. Allow extra time because there is a delay on the main road.

### dispute · n. · 争议

义项 ID：p01-w070-sense01；来源目标：ox-9a826964a6df4f80。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s06：You can contact the company first. Keep a copy of its response in case you need to raise a dispute.

### distinction · n. · 区别

义项 ID：p01-w059-sense01；来源目标：ox-5d70681ca4aef44a。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s06：Let us include that distinction in the report so the claim is accurate.

### double · adj. · 双人的

义项 ID：p01-w004-sense01；来源目标：ox-60885e9ebbf7c1c4。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s02：Of course. Would you like a single room or a double room?

### draft · n. · 草稿

义项 ID：p01-w071-sense01；来源目标：ox-e7c56948b12ce760。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s01：Could we discuss the draft? The introduction is clear, but the final section needs work.

### driver · n. · 司机

义项 ID：p01-w036-sense01；来源目标：ox-688e2ad31497fefa。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s04：It is opposite the station. You can pay the driver with a card.

### ensure · v. · 确保

义项 ID：p01-w084-sense01；来源目标：ox-2aef217d1094417f。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s03：How will you ensure that people with limited mobility can use it?

### entrance · n. · 入口

义项 ID：p01-w086-sense01；来源目标：ox-32830eb691513074。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s04：The entrance will be level, and the paths will be wide.

### estimate · n. · 估算

义项 ID：p01-w045-sense01；来源目标：ox-253b3444eddb8a4d。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s02：We could choose a smaller venue. The current estimate includes a large hall.

### evidence · n. · 证据

义项 ID：p01-w052-sense01；来源目标：ox-39d5556e1526fec0。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s02：What evidence supports that conclusion? How large was the sample?

### expense · n. · 费用

义项 ID：p01-w042-sense01；来源目标：ox-1b75a3d185b62ba9。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s01：Our budget is limited. Which expense can we reduce?

### extra · adj. · 额外的

义项 ID：p01-w039-sense01；来源目标：ox-b284d675072328c7。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s06：It is direct. Allow extra time because there is a delay on the main road.

### fare · n. · 车费

义项 ID：p01-w033-sense01；来源目标：ox-e4a06efdd1491d8b。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s03：Where is the bus stop, and how much is the fare?

### feedback · n. · 反馈

义项 ID：p01-w075-sense01；来源目标：ox-a1324e777ab5c3c2。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s04：That is helpful feedback. I was worried that the argument was too brief.

### flexible · adj. · 灵活的

义项 ID：p01-w080-sense01；来源目标：ox-920a964508cd7d1e。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s07：Yes. Thank you for being flexible.

### flight · n. · 航班

义项 ID：p01-w008-sense01；来源目标：ox-9d9d98c48f7af2a7。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s05：My flight arrives at midnight. Can I still check in?

### floor · n. · 地面

义项 ID：p01-w014-sense01；来源目标：ox-9bc2fe0abbb2bf85。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s01：There is a leak under the kitchen sink. The floor is wet.

### ingredient · n. · 配料

义项 ID：p01-w025-sense01；来源目标：ox-0562c7a5022bacff。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s02：Yes, but I have an allergy to nuts. Could we ask about the ingredients?

### instead · adv. · 作为替代

义项 ID：p01-w028-sense01；来源目标：ox-b74b1e205eff4d84。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s04：Yes. We can serve the salad without it and bring olive oil instead.

### journey · n. · 旅程

义项 ID：p01-w032-sense01；来源目标：ox-4c142adaa4eb8597。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s02：You can take a bus, but the journey will take longer.

### kitchen · n. · 厨房

义项 ID：p01-w012-sense01；来源目标：ox-5c50f62a4e622ea7。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s01：There is a leak under the kitchen sink. The floor is wet.

### leak · n. · 漏水处或漏水现象

义项 ID：p01-w011-sense01；来源目标：ox-1df0d41b1e6d6d03。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s01：There is a leak under the kitchen sink. The floor is wet.

### level · adj. · 平坦的

义项 ID：p01-w087-sense01；来源目标：ox-90d3f69147f768f1。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s04：The entrance will be level, and the paths will be wide.

### limitation · n. · 局限

义项 ID：p01-w055-sense01；来源目标：ox-dfd33657c3ce558f。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s03：Only forty people replied. That is a limitation.

### maintenance · n. · 维护

义项 ID：p01-w089-sense01；来源目标：ox-6ff4751f7e402065。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s05：Who will be responsible for maintenance?

### midnight · n. · 午夜

义项 ID：p01-w009-sense01；来源目标：ox-1738911668a2097b。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s05：My flight arrives at midnight. Can I still check in?

### mobility · n. · 行动能力

义项 ID：p01-w085-sense01；来源目标：ox-c2ea84005b65bb8b。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s03：How will you ensure that people with limited mobility can use it?

### nut · n. · 坚果

义项 ID：p01-w024-sense01；来源目标：ox-2c0dd018fda30fb7。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s02：Yes, but I have an allergy to nuts. Could we ask about the ingredients?
  - pilot01-lunch-s03：Excuse me, does the dressing contain any nuts?

### opposite · prep. · 在对面

义项 ID：p01-w034-sense01；来源目标：ox-90c5c963686feb89。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s04：It is opposite the station. You can pay the driver with a card.

### passport · n. · 护照

义项 ID：p01-w007-sense01；来源目标：ox-ed2901da05e10c80。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s04：Yes. Your room will be ready after three. Please bring your passport.

### pattern · n. · 规律或模式

义项 ID：p01-w057-sense01；来源目标：ox-6150bb58115eaf8d。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s05：Right. We can describe the pattern, but we need further research.

### permission · n. · 许可

义项 ID：p01-w096-sense01；来源目标：ox-c6fc26466468f7c1。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s04：Yes, but we need permission to change the design. That is a separate requirement.

### price · n. · 价格

义项 ID：p01-w006-sense01；来源目标：ox-ad20770a7aac9e30。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s03：A single room, please. Is breakfast included in the price?

### priority · n. · 优先考虑的事

义项 ID：p01-w048-sense01；来源目标：ox-cadfa135f3766295。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s04：Not necessarily. Our priority is useful discussion, not a large audience.

### proposal · n. · 提议

义项 ID：p01-w081-sense01；来源目标：ox-bc8916750988d9e1。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s01：The proposal would turn this empty site into a public garden.

### quality · n. · 质量

义项 ID：p01-w047-sense01；来源目标：ox-589852eb7d7f2701。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s03：Would that affect the quality of the event?

### reasonable · adj. · 合理的

义项 ID：p01-w079-sense01；来源目标：ox-21ffbcbb90263048。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s06：I will revise it today. Is tomorrow a reasonable deadline?

### record · n. · 书面记录

义项 ID：p01-w067-sense01；来源目标：ox-43e18e1961d09be7。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s04：Do you have a record of the cancellation?
- 建议关联（未覆盖）：研究与论证 / 讨论调查证据。调查证据可以保留书面记录。

### reduce · v. · 减少

义项 ID：p01-w043-sense01；来源目标：ox-8af6173d1bd6530b。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s01：Our budget is limited. Which expense can we reduce?

### remove · v. · 删除

义项 ID：p01-w074-sense01；来源目标：ox-6c4e4a590a0199e1。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s03：Please explain the benefit to the reader and remove the repeated examples.

### repair · n. · 维修

义项 ID：p01-w016-sense01；来源目标：ox-a71a5b3209f11808。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s02：Can you turn off the water? I will arrange a repair.

### request · v. · 请求

义项 ID：p01-w068-sense01；来源目标：ox-d4096d3d8ec4a681。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s05：Yes, I have an email. Can I request a refund?
- 建议关联（未覆盖）：出行与住宿 / 修改旅馆预订。住客可请求调整预订。

### requirement · n. · 要求

义项 ID：p01-w097-sense01；来源目标：ox-bb1a90dc64481eb9。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s04：Yes, but we need permission to change the design. That is a separate requirement.

### research · n. · 研究

义项 ID：p01-w058-sense01；来源目标：ox-18aaba4a646eb3a3。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s05：Right. We can describe the pattern, but we need further research.

### reservation · n. · 预订

义项 ID：p01-w001-sense01；来源目标：ox-1896dd84cff928cb。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s01：I have a reservation for Friday, but I need to change the date to Saturday.

### response · n. · 答复

义项 ID：p01-w069-sense01；来源目标：ox-29dcf5a054b0a590。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s06：You can contact the company first. Keep a copy of its response in case you need to raise a dispute.

### responsible · adj. · 负责的

义项 ID：p01-w088-sense01；来源目标：ox-50fa621ca290e402。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s05：Who will be responsible for maintenance?

### revise · v. · 修改

义项 ID：p01-w078-sense01；来源目标：ox-498e800408a76f6a。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s06：I will revise it today. Is tomorrow a reasonable deadline?

### risk · n. · 风险

义项 ID：p01-w091-sense01；来源目标：ox-4cd27ab4167fdca0。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s02：There is a risk. We depend on a supplier for one component.
- 建议关联（未覆盖）：工作与协作 / 调整活动预算。活动预算取舍可以涉及风险。

### route · n. · 路线

义项 ID：p01-w031-sense01；来源目标：ox-50553bf92fae40c9。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s01：I missed my train. Is there another route to York?

### safe · adj. · 安全的

义项 ID：p01-w017-sense01；来源目标：ox-e1132ee76d3c259d。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s03：Yes. Is it safe to use the socket beside the sink?

### salad · n. · 沙拉

义项 ID：p01-w022-sense01；来源目标：ox-0a3fa36287f80e90。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s01：Shall we share a salad and some bread?
  - pilot01-lunch-s04：Yes. We can serve the salad without it and bring olive oil instead.

### sample · n. · 样本

义项 ID：p01-w054-sense01；来源目标：ox-6d8604e6136523a0。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s02：What evidence supports that conclusion? How large was the sample?

### scope · n. · 范围

义项 ID：p01-w098-sense01；来源目标：ox-c1f051d9b09b929a。
- 已有目标用例：工作与协作 / 协调项目交付 → [协调项目交付](dialogues.md#协调项目交付-pilot01-schedule)。
  - pilot01-schedule-s05：Let us clarify the scope before we make a commitment.

### serve · v. · 端上食物

义项 ID：p01-w027-sense01；来源目标：ox-9f7c3e941eee53a6。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s04：Yes. We can serve the salad without it and bring olive oil instead.

### share · v. · 共同享用

义项 ID：p01-w021-sense01；来源目标：ox-a22a4087d47f6a10。
- 已有目标用例：饮食沟通 / 沟通饮食限制 → [有饮食限制的午餐](dialogues.md#有饮食限制的午餐-pilot01-lunch)。
  - pilot01-lunch-s01：Shall we share a salad and some bread?

### single · adj. · 单人的

义项 ID：p01-w003-sense01；来源目标：ox-a17ad01d2de69d4d。
- 已有目标用例：出行与住宿 / 修改旅馆预订 → [修改旅馆预订](dialogues.md#修改旅馆预订-pilot01-booking)。
  - pilot01-booking-s02：Of course. Would you like a single room or a double room?
  - pilot01-booking-s03：A single room, please. Is breakfast included in the price?

### site · n. · 地点

义项 ID：p01-w082-sense01；来源目标：ox-2699b3e791efbdbc。
- 已有目标用例：社区与公共空间 / 讨论公共空间方案 → [讨论社区公园方案](dialogues.md#讨论社区公园方案-pilot01-park)。
  - pilot01-park-s01：The proposal would turn this empty site into a public garden.

### statement · n. · 银行账单

义项 ID：p01-w063-sense01；来源目标：ox-d25d6b51f26b19f3。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s01：There is a charge on my bank statement that I do not recognize.

### station · n. · 车站

义项 ID：p01-w035-sense01；来源目标：ox-da807c4317cac42a。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s04：It is opposite the station. You can pay the driver with a card.

### subscription · n. · 订阅

义项 ID：p01-w066-sense01；来源目标：ox-acce8f2a46bf8ee8。
- 已有目标用例：消费与服务 / 核对账单与争议 → [核对银行账单](dialogues.md#核对银行账单-pilot01-bank)。
  - pilot01-bank-s03：It might be my annual subscription, but I thought I had cancelled it.

### suggest · v. · 建议

义项 ID：p01-w072-sense01；来源目标：ox-4b3c21acd5ce91a0。
- 已有目标用例：工作与协作 / 反馈与修改草稿 → [给同事反馈](dialogues.md#给同事反馈-pilot01-feedback)。
  - pilot01-feedback-s02：What would you suggest?

### survey · n. · 调查

义项 ID：p01-w051-sense01；来源目标：ox-1eedceb6fb96d13b。
- 已有目标用例：研究与论证 / 讨论调查证据 → [讨论调查结果](dialogues.md#讨论调查结果-pilot01-evidence)。
  - pilot01-evidence-s01：The survey suggests that people who cycle to work feel less stressed.

### transfer · v. · 换乘

义项 ID：p01-w038-sense01；来源目标：ox-ed91b8616abb6677。
- 已有目标用例：出行与住宿 / 改用替代交通 → [错过火车后的替代路线](dialogues.md#错过火车后的替代路线-pilot01-journey)。
  - pilot01-journey-s05：Is the service direct, or do I need to transfer?

### venue · n. · 活动场地

义项 ID：p01-w044-sense01；来源目标：ox-32ba514a6692694c。
- 已有目标用例：工作与协作 / 调整活动预算 → [团队缩减活动预算](dialogues.md#团队缩减活动预算-pilot01-budget)。
  - pilot01-budget-s02：We could choose a smaller venue. The current estimate includes a large hall.
  - pilot01-budget-s06：Agreed. I will ask each venue for a detailed quote.

### water · n. · 水

义项 ID：p01-w013-sense01；来源目标：ox-015a7ee984e777b5。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s02：Can you turn off the water? I will arrange a repair.

### wet · adj. · 湿的

义项 ID：p01-w015-sense01；来源目标：ox-d8362e04b8d757de。
- 已有目标用例：居家生活 / 报修漏水 → [报修漏水](dialogues.md#报修漏水-pilot01-repair)。
  - pilot01-repair-s01：There is a leak under the kitchen sink. The floor is wet.


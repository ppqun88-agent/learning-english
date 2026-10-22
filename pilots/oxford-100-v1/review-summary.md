# 独立 AI 语境审读

审读范围：100 个选定词性/中文义项、全部 usage_note_zh、10 篇完整原创对话及每个目标的所有引用句，不仅审读首个命中句。逐项评语见 reviews.json。来源词性与 build/targets.jsonl 的对应记录另作一致性核对，100 项一致。

这是独立 AI 语言审读，不是人工语言专家认证；也不认证学习者掌握、CEFR 义项级难度或业务建议正确性。没有以字符串命中代替语义审读。特别核查了名词前置修饰语 bank/kitchen、形容词 direct/level、charge/statement/record 的多义，以及已批准复数 nuts/ingredients。single、salad、nut、venue、direct 的全部多句证据也已逐句检查。

## 返工与复审

初审 97 项 pass、3 项 revise，涉及两处修改：
1. booking-s01 原来只提出改日期，未说明新日期却在末尾发送确认。作者已补入 to Saturday。重新审读整篇后，p01-w002（date）、p01-w010（confirmation）均改判 pass，改期任务闭环已补齐。
2. p01-w076（argument）原释义“论点”精度不足。作者已改为“论证（支持观点的理由）”，并同步用法提示。重新核对 too brief / strong enough 的上下文后改判 pass。

最终结果：100 项 pass，0 项 revise。未解决的阻断性语言疑点：无。

## 篇章与使用边界

10 篇对话的提问、回应、指代与后续行动均已审读。午餐对话在去酱后继续核实交叉接触；报修对话未鼓励使用有疑虑的插座；银行对话未作退款保证。这些仅是语境连贯性审读，不构成医疗、电气或金融专业建议。

feedback-s03 的 explain the benefit to the reader 有两种可接受的修饰理解：向读者说明好处，或说明读者所得的好处；两者都符合当前宽泛释义“好处”，因此不阻断本目标通过。若后续专门教“读者获益”，应另写无歧义证据。其他可讨论的风格选择，如英式交通口语 change 与当前 transfer，不构成用法错误。

此评审仅覆盖当前小批样例和选定义项，不等于该词所有义项已采用或已掌握。

## 复审快照 SHA-256

- selection.json: e108a310321ba35d5c53ebd5b16a6a9d94bf94e077e2920f2871389544feb98e
- dialogues/bank.json: ca06e11f754d4759a62c8a78389318a9262600bcf54fe7751bc35e748d523a41
- dialogues/booking.json: 58459a1c387ba308605148a2c100d7dc9431c2f59bca0edf93d9fd136dcff098
- dialogues/budget.json: 289f86025e0f11fd4d8a99e6cd205f6646760a7b685eb81dd545725be67605d8
- dialogues/evidence.json: b854f7f9e73c86061a646691d512d861142ed350cf41084bf2cb30ed564901f0
- dialogues/feedback.json: f86d30e6afe9051e471875b513498890e75fb30bc3e31fbaed4104e90b652d04
- dialogues/journey.json: 840a69aab48c85f281147c8986e7e23dfc41477dbfa9925ff595c3dc9855faed
- dialogues/lunch.json: a63e8a3ac3272d60bdf2bb6f985162c484b590edf7ca75fccf5bba24b965e55b
- dialogues/park.json: 582a1def59567b78f9e6eabeabdc8071d40c3aaadbd7791ce93c3265634e5b19
- dialogues/repair.json: 27c4a849febaf2a619507cca7b28282ea5fa453a7eca681312412435a8313587
- dialogues/schedule.json: a0e889023f6c4b52b240668adf3b29dc78e91bf5cc2f890b30008130f2845bb5

快照说明：上方 selection.json 哈希对应语义复审时、状态汇总前的版本。复审后仅将 formal_checked / semantic_reviewed 汇总为 true，未改动词、义项、用法、对话或证据。最终文件哈希见 progress.json。

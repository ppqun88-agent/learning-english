# 资源整合与可复现导入

## 本次真正整合的内容

- `data/reference/ecdict-definitions.json`：上游结构化 ECDICT 释义与音标原样保留，7,009 个词条（不含 `_meta`）。保留全文件是为了哈希可验证及避免重做词典；不表示把全部词条或其他考试课程纳入学习范围。Oxford 过滤发生在本地导入阶段。
- `licenses/`：保留 wordlists 与其收录 ECDICT 的 MIT 原文。没有替整个学习项目擅自选择许可证。
- `provenance/wordlists.json`：来源仓库、固定 commit、文件 SHA-256、复制映射。
- `tools/pipeline.py`：本项目新写的标准库导入/形式证据检查器，无外部依赖、API 或音频调用。没有复制运行 PDF 解析器，因为已有结构化结果。
- 原先五份讨论档案保留，新增执行计划与本说明。没有合并 main、部署或生成全量教材。

## 许可边界

来源 README 将自整理结构/处理/文档与 ECDICT 标注为 MIT，同时明确 PDF 及其中词表内容属于原作者/出版社。因此不重新发布 Oxford PDF、完整 Oxford.json 或带 Oxford 标签的 categories.json，也不把仓库 MIT 当成出版社内容授权。以下导入只读取用户已有来源副本，生成结果在忽略的 build/ 内；后续公开发布整套派生词表前仍须确认相应权利。此处为遵守上游声明的保守处理，不构成商用授权判断。

来源： https://github.com/ppqun88-agent/wordlists/tree/3043da14627ed3c6168b598479bc110ce6b34736

## 从零复现

需要 Git 与 Python 3（仅标准库），在 learning-english 根目录运行：

```bash
git clone https://github.com/ppqun88-agent/wordlists.git ../wordlists-source
git -C ../wordlists-source checkout --detach 3043da14627ed3c6168b598479bc110ce6b34736
python3 tools/pipeline.py import --source-dir ../wordlists-source
python3 -m unittest discover -s tests -v
```

已有来源目录时无需重新克隆；若存在未提交修改，先保存再选择独立干净副本，不覆盖用户工作。导入用 SHA-256 校验五个来源文件及已复制词典，任何不一致即停止，不静默使用新版本。该 clone 获取上游全部存储内容但不会把它们复制/提交到本仓库；不运行上游代码。

实际试跑：5,062 个独立词形，6,187 条列表/词性/等级/版本原始记录，64 个独立词形无音标。记录数不是词义数，也不是已选学习目标数。所有 sense_status 均为 pending。Oxford3000 与 Oxford5000 在此来源分别是基础及扩展标签，不应简单相加理解成两个独立完整课程。

`build/targets.jsonl` 提供稳定 target_id、lemma、list、CEFR、原始 POS 记录、待选 sense、原始音标及释义、初始 approved_forms、来源 SHA。保留记录中的 US/UK/同形信息，不将原始中文释义直接视为课程义项。目标 ID 以来源元组内容生成；换来源版本需比较迁移，不能假定含义不变。

## 对话形式验证

```bash
python3 tools/pipeline.py validate --dialogues path/to/dialogue.json --targets build/targets.jsonl
```

JSON 契约：文档 id；sentences 为含 id/speaker/text 的数组；targets 为含 target_id/lemma/forms/sentence_ids 的数组。forms 只允许目标清单中已人工审核的 approved_forms。默认不猜测词形变化，不把 stand 算作 understand，不把 May 算作 may。大小写策略保守，专名变体须显式确认。reviews 可记录 target_id/reviewer/status/rationale，但程序不认证其真实性，也不会自动宣布语义通过。

输出 formal_pass/errors；失败退出码 1。这不是完整教材验收器：词性、义项、中文对应、对话连贯、审核者独立性、跨文件完整覆盖及冻结清单仍按执行计划人工或后续工具完成。不要用形式检查通过冒充最终课程合格。

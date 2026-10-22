#!/usr/bin/env python3
"""Render the human-readable pilot and CSV from its versioned JSON sources."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'pilots/oxford-100-v1'
def main():
 rows=json.loads((P/'selection.json').read_text())
 with (P/'selection.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
  writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
 out=['# 第一批情景对话与用法映射','', '原创文本。词源等级不是整篇对话难度；未标注的辅助词不计入本批覆盖。语义审核为 AI 审核，不是人工专家认证。','']
 for path in sorted((P/'dialogues').glob('*.json')):
  d=json.loads(path.read_text());out.extend([f'## {d["title_zh"]} ({d["id"]})','',d['context_zh'],''])
  for s in d['sentences']:out.append(f'{s["id"]}. **{s["speaker"]}:** {s["text"]}')
  out.extend(['','### 本篇目标词及用法',''])
  for r in rows:
   if r['scene_id']==d['id']:out.append(f'- {r["pilot_id"]} **{r["lemma"]}** ({r["pos"]}, {r["cefr"]})：{r["sense_zh"]}。证据：{", ".join(r["sentence_ids"])}。{r["usage_note_zh"]}')
  out.append('')
 (P/'dialogues.md').write_text('\n'.join(out)+'\n')
if __name__=='__main__':main()

# CONTENT_SCHEMA.md

`content_plan.json` 只描述内容结构，不描述排版坐标。

## 顶层结构

```json
{
  "deck_meta": {
    "title": "",
    "subtitle": "",
    "language": "zh-CN",
    "audience": "",
    "scenario": "academic_report | journal_club | thesis_defense | lecture | project_report",
    "target_slide_count": 12,
    "source_files": []
  },
  "slides": [
    {
      "slide_no": 1,
      "section": "",
      "purpose": "",
      "main_message": "",
      "key_points": [],
      "visual_need": "none | formula | figure | table | diagram | comparison | multi_image | takeaway",
      "evidence_refs": [],
      "speaker_notes": ""
    }
  ]
}
```

## 规则

- 每页只有一个 `main_message`。
- 不要复制论文大段原文。
- 关键事实、公式、指标、实验结果必须保留 `evidence_refs`。
- 不确定内容写入 speaker notes 或标记“需要人工确认”。
- 视觉需求只表达内容类型，不表达坐标。

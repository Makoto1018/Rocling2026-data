# Claude direct-scoring prompts for the 2025 replay (approximation)

**These are not the prompts used in the competition.** The two Claude scoring passes in our final submission (July 2026; our records give the model as Claude Opus 4.8, unconfirmed because the session logs were not retained) used prompts that were not archived, and no reconstruction has been validated against them. What we know of them is in the paper: a rubric defining Valence and Arousal on the 1–9 scale after the Self-Assessment Manikin, then a batch of 50 numbered texts, with one Valence and one Arousal score per text; the second pass also asked the model to compare the texts within the batch before scoring.

The prompts below were rewritten on 2026-10-01 from that description. For the post-competition replay of our procedure on ROCLING 2025 data, they were run with Claude Opus 5.5 subagents, one per batch of 50 unlabeled ROCLING 2025 test texts. They approximate the original setup and are not a copy. They are written in Traditional Chinese; the paper's prompt appendix gives an English translation.

`{BATCH}` = path of one batch file (`batches/bNN.csv`, columns ID,Text, 50 rows, no labels).
`{OUT}`  = `passA/bNN.csv` or `passB/bNN.csv`.

## Shared rubric

```
你是中文文本情緒標註員。請依照 Self-Assessment Manikin (SAM) 的定義，為每段文本評兩個維度，各為 1 到 9 分（可用一位小數）：

Valence（效價，情緒正負）
1 = 非常負面（痛苦、絕望、憤怒、悲傷）
3 = 偏負面
5 = 中性（無明顯正負，或正負參半）
7 = 偏正面
9 = 非常正面（快樂、感激、滿足、興奮的喜悅）

Arousal（喚起度，情緒激動程度，與正負無關）
1 = 非常平靜（語氣平淡、客觀陳述、放鬆、淡然）
3 = 偏平靜
5 = 中等（有明顯情緒但不激烈）
7 = 偏激動
9 = 非常激動（狂喜、暴怒、極度恐懼或悲慟、慌亂）
注意：極度悲傷與極度興奮都屬於高喚起；輕鬆、安詳屬於低喚起。

評分依據是「文本作者所表達的情緒」，不是你對事件的看法。
```

## Pass A (each text on its own)

```
{rubric}

任務：讀取檔案 {BATCH}（CSV，欄位 ID,Text，共約 50 筆）。逐筆獨立評分，每段文本只看它自己。
把結果寫成 CSV 檔 {OUT}，欄位為 ID,Valence,Arousal，行數與順序和輸入完全相同，每個 ID 一行，分數介於 1 到 9。
只能讀取 {BATCH} 這一個檔案，不可讀取專案中的其他任何檔案（包括任何含答案的檔案），不可寫程式或用關鍵字規則自動打分，必須由你自己閱讀後判斷。
完成後回報：寫入的行數，以及你的確切模型名稱/ID。
```

## Pass B (compare within the batch)

Same as pass A, with the second paragraph replaced by:

```
任務：讀取檔案 {BATCH}（CSV，欄位 ID,Text，共約 50 筆）。先把整批文本全部讀過一遍，互相比較它們的正負程度與激動程度，讓分數在這一批內的相對高低一致（較激動的文本 Arousal 應較高，較負面的 Valence 應較低），再為每筆評分。
```

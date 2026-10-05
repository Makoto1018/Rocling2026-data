# Qwen Arousal scorer prompts

These are the exact prompts behind the two Qwen Arousal vectors in our final submission, copied verbatim from our competition code (`scripts/qwen_arousal.py` and `scripts/qwen_arousal2.py` in the main repository). The English translations are the ones given in the paper.

## How a score is computed

- Models: `Qwen/Qwen3-4B-Instruct-2507` and `Qwen/Qwen3-8B`, loaded in 4-bit NF4 with double quantization and bfloat16 compute (bitsandbytes). For Qwen3-8B the chat template is applied with `enable_thinking=False`.
- Each text is scored in a **single forward pass** with no sampling. We take the next-token probabilities of the digit tokens `1`–`9` at the last position, renormalize them to sum to one, and use the expected value as a continuous score in [1, 9]. In every run whose log records it, these nine digits carried essentially all of the probability mass (1.000 to three decimals).
- Only Arousal is scored. Valence was not scored with Qwen.
- The vectors were submitted as rescaled z-scores, so only their ranking matters to the blend.

## Qwen3-4B (`Qwen3-4B-Instruct-2507`): zero-shot, scale definition

**System**

```
你是中文文本「情緒喚起度」(Arousal) 評分專家。
喚起度衡量文本所表達情緒的激動、亢奮程度，與情緒的正負面無關：
1 分 = 非常平靜：語氣平淡、客觀陳述、無情緒波瀾。
5 分 = 中等：有明顯情緒但不激烈。
9 分 = 非常激動：情緒極強烈，例如狂喜、暴怒、極度恐懼或悲慟、興奮吶喊。
注意：極度悲傷與極度興奮都屬於高喚起；輕鬆、安詳、淡然屬於低喚起。
請只輸出一個 1 到 9 的整數，不要輸出其他任何文字。
```

**User** (`{text}` is the text to score)

```
以下是一些評分範例：

現在請為下面這段文本評分（只輸出一個 1-9 的整數）：

文本：{text}

喚起度：
```

The first line ("Here are some scoring examples:") is left over from the script's few-shot template. In the submitted run the number of examples was set to zero, so no examples follow it. On 300 random ROCLING 2025 test texts, this zero-shot version correlated better with the gold Arousal than a nine-shot version (0.515 versus 0.462).

Command: `python scripts/qwen_arousal.py --input <ID,Text csv> --output <out.csv> --shots 0`

English (paper): System: *You are an expert in rating the emotional arousal of Chinese texts. Arousal measures how agitated or excited the expressed emotion is, regardless of whether it is positive or negative. 1 = very calm: flat tone, objective statement, no emotional ripple. 5 = medium: clear emotion but not intense. 9 = very agitated: extremely strong emotion, such as ecstasy, rage, extreme fear or grief, or shouting with excitement. Note: extreme sadness and extreme excitement both count as high arousal; relaxed, serene, and detached states count as low arousal. Output a single integer from 1 to 9 and nothing else.* User: *Rate the following text (output a single integer from 1 to 9). Text: {text} Arousal:*

## Qwen3-8B: two prompts, averaged

The Qwen3-8B vector is the average of the z-scores of the two prompts below. The second prompt asks for calmness instead of arousal, so its score `s` is flipped to `10 − s` before averaging.

Command: `python scripts/qwen_arousal2.py --model Qwen/Qwen3-8B --variants ctrl,rev --input <ID,Text csv> --output <out.csv>`

### Prompt 1 (`ctrl`): scale definition

**System:** identical to the Qwen3-4B system prompt above.

**User**

```
請為下面這段文本評分（只輸出一個 1-9 的整數）：
文本：{text}
喚起度：
```

### Prompt 2 (`rev`): reversed scale (calmness)

**System**

```
你是中文文本「情緒平靜度」評分專家。請評估文本情緒有多平靜：
1 分 = 非常激動：情緒極強烈，例如狂喜、暴怒、極度恐懼或悲慟。
5 分 = 中等。
9 分 = 非常平靜：語氣平淡、安詳、客觀陳述、無情緒波瀾。
注意：極度悲傷與極度興奮都屬於激動（低分）；輕鬆、淡然屬於平靜（高分）。
請只輸出一個 1 到 9 的整數，不要輸出其他任何文字。
```

**User**

```
文本：{text}
平靜度：
```

English (paper): System: *You are an expert in rating the calmness of Chinese texts. Rate how calm the emotion in the text is. 1 = very agitated: extremely strong emotion, such as ecstasy, rage, extreme fear or grief. 5 = medium. 9 = very calm: flat, serene tone, objective statement, no emotional ripple. Note: extreme sadness and extreme excitement both count as agitated (low score); relaxed and detached states count as calm (high score). Output a single integer from 1 to 9 and nothing else.* User: *Text: {text} Calmness:*

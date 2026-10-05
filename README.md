# ROCLING 2026 synthetic new-immigrant VA texts (YCW-ntust)

The 300 synthetic texts and their pseudo-labels used by team YCW-ntust in the ROCLING-2026 shared task on Chinese dimensional sentiment analysis of new-immigrant texts, as described in our paper *YCW-ntust at ROCLING-2026 Shared Task: Leaderboard-Feedback Closed-Form Ensembling with LLM Direct Scoring for Chinese Valence–Arousal Regression* (Sections 3.4 and 5.4, Appendices C and D). It also contains the LLM prompts referred to in the paper's prompt appendix.

All texts are fictional, written in Traditional Chinese in the first-person voice of new immigrants in Taiwan. They contain no text from the shared-task data: none of the 300 texts duplicates, or shares any 12-character substring with, any of the 200 ROCLING 2026 validation texts or 1,100 test texts.

## Files

| File | Rows | Columns | Content |
|---|---|---|---|
| `data/synth_labeled_blend_all300.csv` | 300 | `ID,Text,Valence,Arousal` | **The training data used in our final system**: all 300 texts with blended labels |
| `data/synth_labeled_blend.csv` | 207 | `ID,Text,Valence,Arousal` | Teacher-consistency-filtered subset, same blended labels (compared in the paper, not used in the final system) |
| `data/synth_labeled_teacher.csv` | 207 | `ID,Text,Valence,Arousal` | Same 207 texts labeled with the teacher mean only (not used by any model in the paper) |
| `data/gen_a_high_arousal.csv` | 150 | `ID,Text,gen_valence,gen_arousal` | Generator output, batch A (IDs `GA0001`–`GA0150`) with the intended (target) VA |
| `data/gen_b_low_arousal.csv` | 150 | `ID,Text,gen_valence,gen_arousal` | Generator output, batch B (IDs `GB0001`–`GB0150`) |
| `data/_teach_{rb,mb,e5}_{a,b}.csv` | 150 each | `ID,valence_rating,arousal_rating` | Predictions of the three teachers (`rb` RoBERTa, `mb` MacBERT, `e5` e5-SVR) on batch A / B |
| `rebuild_labels.py` | | | Recomputes all three labeled files from the generator targets and teacher predictions and asserts an exact match |
| `prompts/synthetic_generation_reconstructed.md` | | | Post-hoc reconstruction of the generation prompt (see below) |
| `prompts/qwen_arousal.md` | | | Exact prompts and scoring procedure of the Qwen3-4B and Qwen3-8B Arousal scorers in our final submission |
| `prompts/claude_replay_rubric.md` | | | Claude scoring rubric rewritten after the competition for the replay on ROCLING 2025 data (not the lost competition prompt) |

Files are UTF-8 with BOM. Valence and Arousal are on the task's 1–9 scale (Valence 1 = very negative, 9 = very positive; Arousal 1 = very calm, 9 = very agitated).

## Pipeline

```
Claude (2 subagents) ──> 300 texts + target VA (gen_valence, gen_arousal)
                                     │
   RoBERTa, MacBERT, e5-SVR teachers ┤──> teacher mean VA
                                     │
        label = 0.5 × target + 0.5 × teacher mean   (per dimension, rounded to 3 decimals)
                                     │
        ├── all 300 ───────────────> synth_labeled_blend_all300.csv   (used)
        └── |target − teacher mean| ≤ 1.5 on both dimensions ──> 207 texts
                                     ├── blended label ──> synth_labeled_blend.csv
                                     └── teacher mean ───> synth_labeled_teacher.csv
```

### 1. Generation

- **When and how.** 13 July 2026, during the test phase, by two parallel Claude Code subagents dispatched from a Claude Fable 5 session. Our records of the period give the subagent model as **Claude Opus 4.8**, but the session logs that would confirm this were not retained.
- **Batch A** (150 texts): high Arousal. Target Arousal 5.6–8.0, target Valence 2.0–8.5 (high-Arousal negative such as anger, panic, fear; high-Arousal positive such as excitement, joy, pride; a few mixed). Mean length 72.7 characters.
- **Batch B** (150 texts): low to mid Arousal. Target Arousal 2.2–5.5, target Valence 3.0–7.5 (calm negative such as loneliness or resignation; calm neutral daily routine; calm positive such as contentment or gratitude). Mean length 52.0 characters.
- **Style anchor.** Register and topics (marriage and in-laws, work, homesickness, children's education, identity documents) were anchored on the unlabeled ROCLING 2026 validation texts.
- **Prompt.** The original prompts were **not archived**. `prompts/synthetic_generation_reconstructed.md` was reconstructed afterwards from our design notes. A blind 30-text pilot with it (an Opus subagent that had not seen this set) gave target VA values distributed similarly to this set (not tested formally), but shorter texts (48 vs. 62 characters on average); a longer length specification would be needed to match. Running the prompt will produce *a comparable* set, not these texts: LLM generation is not deterministic and Claude Code exposes no temperature or seed.

### 2. Teachers

Following the multi-teacher pseudo-labeling of CYUT-NLP at ROCLING 2025 (Jian et al., 2025), each text is scored by three regressors, all trained on the same 6,531 labeled examples: Chinese EmoBank CVAS (`CVAS_[1-5].csv`) and CVAT (`CVAT_[1-5]_SD.csv`), plus the ROCLING 2025 validation set (994 texts). None of them saw ROCLING 2026 labels (none were released to participants) or any synthetic text.

| Teacher | Base model | Setup |
|---|---|---|
| RoBERTa (`rb`) | `hfl/chinese-roberta-wwm-ext` | Fine-tuned regressor |
| MacBERT (`mb`) | `hfl/chinese-macbert-base` | Fine-tuned regressor, same recipe |
| e5-SVR (`e5`) | `intfloat/multilingual-e5-large-instruct` (frozen) | Embeddings + RBF SVR |

- **RoBERTa and MacBERT.** A linear head on the pooled `[CLS]` representation predicts Valence and Arousal jointly under MSE loss on standardized targets; outputs are mapped back to the 1–9 scale and clipped. 4 epochs, batch size 16, max length 256, learning rate 2e-5, 10% warm-up, weight decay 0.01, fp16, seed 42. A random 10% (654 examples) is held out and the epoch with the highest Valence PCC on it is kept. No calibration is applied to the teacher outputs.
- **e5-SVR.** Texts are encoded without an instruction prefix, truncated to 512 tokens, with masked mean pooling and L2 normalization. Separate scikit-learn RBF SVRs for Valence and Arousal on the raw 1–9 targets, C = 10, ε = 0.2 (the setting of Li & Lin, TCU at ROCLING 2025); outputs clipped to 1–9.

The three teacher models are also members of our submitted system (they are its "encoder ensemble"). The checkpoints are not included here (about 400 MB per encoder).

### 3. Labels and filtering

For each text and each dimension, **label = 0.5 × generation target + 0.5 × mean of the three teachers**, rounded to 3 decimals. Why both: the teachers rank the texts consistently with the targets (Pearson r between target and teacher mean: Valence 0.879, Arousal 0.906), but they compress the Arousal scale (standard deviation 1.13 for the teacher mean vs. 2.03 for the targets), the regression-to-the-mean bias of models trained on out-of-domain data. The blended Arousal label has a standard deviation of 1.54 over all 300 texts (1.50 over the filtered 207).

The **teacher-consistency filter** removes a text when target and teacher mean differ by more than 1.5 on either dimension, keeping 207. The 93 removed texts are concentrated at the Arousal extremes (72 of the 93 have a target Arousal ≤ 3 or > 7, against 100 of the 207 kept), which follows almost by construction from the teachers' compressed scale, so the disagreement need not mean a bad label. Our final system uses all 300.

## How the data was used: the synthetic-data specialist

The "synthetic specialist" in the paper is a RoBERTa regressor trained with exactly the teacher recipe above on the 6,531 original examples **plus** the 300 texts of `synth_labeled_blend_all300.csv` (its 10% held-out split is drawn from the combined pool). It is not trained on synthetic data alone.

Reported results (from the paper):

- ROCLING 2025 test set used as a local proxy (V-MAE / V-PCC / A-MAE / A-PCC, seed 42): no synthetic data 0.500 / 0.795 / 0.771 / 0.629; +207 filtered 0.510 / 0.795 / 0.777 / 0.633; +300 full 0.481 / 0.795 / 0.781 / 0.641.
- Over three seeds (42, 43, 44), proxy A-PCC is 0.623 ± 0.009 without synthetic data, 0.626 ± 0.007 with the filtered 207, and 0.634 ± 0.007 with all 300; the full set is ahead of both in every seed. Valence is unaffected.
- ROCLING 2026 test set (official reading, seed 42): A-PCC 0.3623 vs. 0.3499 for the RoBERTa regressor without synthetic data.

The gain is small (about one seed standard deviation) and improves the ranking of Arousal; it does not reliably widen the Arousal predictions (that widening appears in seed 42 only).

## Reproducibility

| Step | Status |
|---|---|
| Labels from generator targets + teacher predictions | Exact: run `python rebuild_labels.py` (needs pandas) |
| Teacher predictions from the original seed-42 checkpoints | Exact: all six `_teach_*` files were regenerated byte for byte on 5 Oct 2026 |
| Retraining the teachers from scratch | Same data and hyperparameters as above; bit-identical weights are not guaranteed on other GPUs or library versions (ours: torch 2.11.0+cu128, transformers 5.12.0, scikit-learn 1.9.0, RTX 5050) |
| The 300 texts and their targets | Not reproducible: LLM output, original prompt lost; use the files here |

## Caveats

- Being LLM-generated, the texts may carry the generator's own affective stereotypes about new-immigrant experience. We did not audit them for such bias.
- The generation targets are the generator's intended VA, not human annotations; the blended labels are pseudo-labels.

## Other LLM prompts

- **Qwen scorers** (`prompts/qwen_arousal.md`): the exact Traditional Chinese prompts of the two Qwen Arousal vectors in our final submission, copied verbatim from the competition code, with the paper's English translations.
- **Claude scorer**: the prompts of the two Claude scoring passes in the competition were not archived, and no reconstruction has been validated against them. `prompts/claude_replay_rubric.md` is the rubric we rewrote afterwards from the paper's description and ran with Claude Opus 5.5 for the replay on ROCLING 2025 data (paper, Section 5.5). It approximates the original prompts and is not a copy.

## License

The data (`data/`) and documentation are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (`LICENSE`). The code (`rebuild_labels.py`) is licensed under the MIT License (`LICENSE-CODE`).

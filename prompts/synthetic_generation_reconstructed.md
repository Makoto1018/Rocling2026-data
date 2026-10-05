# Reconstructed synthetic-data generation prompt
(Reconstructed on 2026-09-27 from the design record reports/2026-07-13_round3_research.md §2d; the original prompt text was not archived.)

You are generating fictional Traditional Chinese texts for a Valence–Arousal (VA) regression task on new-immigrant narratives (ROCLING 2026 DSA-NIFT).

Style reference: first read `data/raw/rocling2026/DSANIDF_ValidationSet.csv` and imitate the register, length (about 45–85 Chinese characters), and first-person voice of those texts (e.g. diary entries, messages to friends/family/teachers). Do NOT copy or paraphrase any specific validation text.

Content: first-person narratives by new immigrants in Taiwan (e.g. spouses from Vietnam, Indonesia, Thailand, the Philippines, mainland China). Topics: marriage and in-laws, workplace, homesickness, children's education, identity documents / residence permits, language learning, daily life. All people and events must be fictional; no real names or identifiable details. Avoid stereotyping.

Scale: Valence 1 (very negative) – 9 (very positive); Arousal 1 (very calm) – 9 (very excited/agitated); 5 = neutral/medium.

Batch {BATCH}: produce {N} texts, stratified across VA cells:
- Batch A (high arousal, target A ≈ 5.5–8.0): split between high-arousal negative (anger, panic, fear; V ≈ 2–3.5) and high-arousal positive (excitement, joy, pride; V ≈ 7–8.5), plus a few mixed.
- Batch B (low/mid arousal, target A ≈ 2–5.5): split between calm negative (loneliness, resignation; V ≈ 3–4), calm neutral (routine daily life; V ≈ 4.5–5.5) and calm positive (contentment, gratitude; V ≈ 6–7.5).

For each text assign the intended target Valence and Arousal (one decimal) that the text is written to express.

Output: a UTF-8 CSV with header `ID,Text,gen_valence,gen_arousal`, IDs `{PREFIX}0001`…, one text per row, text quoted if it contains commas.

"""Rebuild the pseudo-labels from the generator targets and the three teachers,
and check that they match the shipped files exactly.

    python rebuild_labels.py
"""
from pathlib import Path

import pandas as pd

D = Path(__file__).parent / "data"


def read(name):
    return pd.read_csv(D / name, encoding="utf-8-sig").set_index("ID")


gen = pd.concat([read("gen_a_high_arousal.csv"), read("gen_b_low_arousal.csv")])
teachers = [pd.concat([read(f"_teach_{m}_a.csv"), read(f"_teach_{m}_b.csv")]) for m in ("rb", "mb", "e5")]
t_v = sum(t.valence_rating for t in teachers) / 3
t_a = sum(t.arousal_rating for t in teachers) / 3

# label = 0.5 * generation target + 0.5 * teacher mean, per dimension
blend_v = (0.5 * gen.gen_valence + 0.5 * t_v).round(3)
blend_a = (0.5 * gen.gen_arousal + 0.5 * t_a).round(3)
# filter: drop a text if target and teacher mean differ by more than 1.5 on either dimension
keep = ((gen.gen_valence - t_v).abs() <= 1.5) & ((gen.gen_arousal - t_a).abs() <= 1.5)

all300 = read("synth_labeled_blend_all300.csv")
filt = read("synth_labeled_blend.csv")
teach = read("synth_labeled_teacher.csv")

assert len(gen) == 300 and gen.index.is_unique and gen.Text.is_unique
assert (all300.Text == gen.Text).all()
assert (all300.Valence == blend_v).all() and (all300.Arousal == blend_a).all()
assert list(filt.index) == list(gen.index[keep]) and keep.sum() == 207
assert (filt.Valence == blend_v[keep]).all() and (filt.Arousal == blend_a[keep]).all()
assert list(teach.index) == list(filt.index)
assert (teach.Valence == t_v[keep].round(3)).all() and (teach.Arousal == t_a[keep].round(3)).all()
print("OK: all300, filtered-207 and teacher-only labels match exactly")

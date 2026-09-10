# `grounding_summary` is not comparable across 850a83c

**Any figure computed from `grounding_summary` on a persona written before
commit `850a83c` (2026-09-09) is invalid. Not imprecise — invalid.**

This page exists because the counter has now been fixed, and every
automatically generated report from here on reads from the fixed counter. A
report that compares a period before the fix against a period after it will
manufacture a large, entirely fictional change, and the numbers will look
plausible enough to act on.

## What was wrong

`grounding_summary` was written once, when a persona still carried 1,297
dimensions, and no later step updated it. The pool was trimmed to 48
dimensions; the counter kept reporting the old population.

| | claimed by `grounding_summary` | actually in the files |
|---|---|---|
| dimensions, 42 personas | 54,264 | **2,016** |
| grounding entries | — | **2,048** |
| `generated` | 53,255 | **965** |
| `observed` | 1,009 | 1,009 |

## The two mistakes it produces

**A fixed counter looks exactly like deleted data.** `generated` falling from
53,255 to 965 reads as a large cut. Nothing was cut: 48 dimensions per persona
before, 48 after, no field removed by that commit. The drop is the counter
ceasing to describe a pool that stopped existing weeks earlier.

**A stable numerator over a lying denominator looks like growth.** The measured
share appeared to rise from 1.9% to 51%. `observed` was 1,009 both times. The
real share was always ~50%; only the denominator changed. A ratio that appears
to improve twenty-seven-fold while nothing moves is the more dangerous shape of
the same error, because it flatters rather than alarms.

Both readings were produced in good faith from the file's own self-report. The
lesson is not "read more carefully" — it is that a self-reported count must be
derived from the data on every write, which `recompute_grounding_summary` now
does, and which any script adding or removing a dimension must call.

## Related: `"None"` the answer versus `null` the absence

A sibling error, same family. `"None"` is a legitimate measured answer —
`english_proficiency: None` means a driver who does not speak English,
`veh_assistant_builtin: "None, uses no assistant"` is a real survey option.
`null` means the value is absent. Counting them together turns valid answers
into missing data: the seven personas that moved from `english_proficiency:
Native` to `None` were rule R5 replacing an impossible value with a valid one,
not seven fields being emptied. Across the same commit, string `"None*"` went
83 → 86 and `null` went 0 → 12.

## What to do with pre-fix numbers

Do not repair them; there is nothing to repair, because the underlying files
were always correct. Recompute from the files:

```
uv run python -c "
import yaml, sys
sys.path.insert(0, 'scripts')
from persona_tiers import persona_paths, recompute_grounding_summary
for p in persona_paths(__import__('pathlib').Path('persona/datasets/vn-drivers')):
    d = yaml.safe_load(p.read_text(encoding='utf-8'))
    print(p.name, recompute_grounding_summary(d))
"
```

The dimensions and grounding entries were never wrong. Only the summary was.

---

## The same break, three lines higher: `sources`

`grounding_summary` was fixed in `850a83c`. `sources` sits directly above it in
every persona file, counts the same thing from the same data, and was missed.

Until the commit that added this section, `vn-drv-001` declared:

```yaml
sources:
  full_dag:              {values: 1266}
  vn_driver_survey_2026: {values: 8}
```

while its `grounding` held **seven** values from `full_dag` and **twenty-two**
from the survey. The block was written before the trim step cut a persona from
1,306 dimensions to 48, and nothing recomputed it — so the header described a
persona twenty-seven times larger than the file underneath it, and understated
the survey's contribution by a factor of three.

**The same warning applies.** A `sources` figure quoted from a persona written
before this fix is invalid, and a comparison spanning the fix invents a change:
`full_dag` reads 1266 → 7 as though a thousand fields were deleted, when the
count was the only thing that moved. The survey moves 8 → 22 in the flattering
direction, which is worse, because nobody audits a number that improves.

`matraix.persona_sources.recompute_sources` computes the block from the
persona's own grounding; `sources_disagree` is asserted over both committed
pools in `tests/unit/matraix/test_sources_block_matches_grounding.py`, so this
cannot silently rot again.

## And a derived field nobody evaluated

Not a counter, but found in the same sweep and with the same shape — a value
that claimed something the file did not support.

`att_voice_assistant` is a **function** of `vn_assistant_task_scope`: a driver
who delegates nothing is Opposed, one who delegates everything is Enthusiast.
It therefore has exactly one correct value and nothing to disagree about. Two
code paths computed it anyway, from two different parents: the crosswalk used
the task scope, while the shipped pool recorded
`derived_from:att_self_driving_cars`. **29 of 42 personas held a value the map
does not produce** — `vn-drv-001` delegates navigation and media, which is
Neutral, and was written Opposed.

Any analysis that read `att_voice_assistant` on the 42-persona pool before this
fix read a field that was, in 69% of cases, not derived from anything.
`matraix.persona_derivations` evaluates it and records `corrected_from`.

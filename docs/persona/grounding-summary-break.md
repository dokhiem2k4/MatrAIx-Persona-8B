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

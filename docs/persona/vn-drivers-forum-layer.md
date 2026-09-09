# VN-Drives forum layer: before and after

Date: 2026-09-05
Source: otofun.net.vn
Pool: `persona/datasets/vn-drivers`. The layer once wrote a separate
`vn-drivers-forum`; the two were consolidated, so it now reads and writes the
same pool. The pre-layer base is in git at `b2ce5d8`.

## What was collected

| | |
| --- | --- |
| Subforums | VinFast, Ô tô điện, Sửa chữa, Hỏi đáp đường sá |
| Threads | 73 |
| Unique posts | 1,403 |
| Distinct members | 541 |
| Members with enough writing to measure | 84 (≥3 posts, ≥400 characters) |
| Posts behind the measurements | 754 |

Collected with `scripts/crawl_otofun_posts.py`: one request every 2 seconds,
single connection, a User-Agent naming the project and a contact address, and
the paths under `robots.txt` `Disallow` left alone. Quoted passages,
signatures and reaction bars are stripped before anything is measured, so a
reading reflects what the member wrote in that post and nothing else.

The raw posts are **not** in this repository. They are the members' own
writing; only the aggregate measurements below were kept, in
`persona/datasets/vn-drivers/forum_measurements.json`.

## What was measured

Both readings are counted deterministically by
`scripts/measure_forum_language.py` — no model judges anything, so every value
traces back to the strings that produced it.

**Self-positioning.** Vietnamese uses one word for "I" and for "you"; which it
is comes from the relation, not the token. On this board the convention is
settled: members address each other as *cụ/bác/mợ* and name themselves as
*em/cháu/mình/tôi*. A pronoun is therefore counted as first person only where
the grammar forces it — immediately before a verb it governs (`em thấy`), or
after a noun it possesses (`xe em`).

| | n | share |
| --- | ---: | ---: |
| Deferential (*em*, *cháu*) | 64 | 92.8% |
| Neutral (*mình*, *tôi*) | 5 | 7.2% |

A first attempt counted every occurrence of *cụ* and *bác* as self-reference
and returned 0% neutral. That is what a broken measure looks like, not a
finding; the result above comes from the corrected pass.

**Verbosity.** Median words per post, per member:

```
min 8 · p20 22 · p40 27.5 · p60 33 · p80 46 · max 138
```

## What changed in the 42 personas

Only two dimensions. Verified mechanically: 0 dimensions lost, no observed
grounding altered, no other value touched.

### `vn_address_register`

The dimension was **absent from all 42 persona files**. The schema defines it
as the pronoun pair the persona uses when speaking to an in-car assistant, and
it decides how every simulated user opens their turn.

| | before | after |
| --- | --- | --- |
| chi/em | — | 19 |
| anh/em | — | 13 |
| co-chu/con | — | 5 |
| minh/ban | — | 3 |
| bac/chau | — | 2 |
| *(absent)* | 42 | 0 |

### `cog_verbosity`

Previously drawn from the synthesis graph. Now allocated so the pool matches
the measured distribution, by largest remainder rather than sampling, so the
match is exact and the run repeats identically.

| band | before | after | measured on OTOFUN |
| --- | ---: | ---: | ---: |
| Terse | 9 | 9 | 23% |
| Concise | 8 | 8 | 18% |
| Balanced | 13 | 9 | 20% |
| Wordy | **4** | 8 | 20% |
| Rambling | 8 | 8 | 19% |

Distance to the measured distribution (total variation, 0 = exact):

```
before 0.119   →   after 0.024
```

The old pool under-represented wordy drivers by half.

## What did not change, and why

**Pool redundancy is untouched.**

```
                    before                              after
pairwise overlap    all 37.0% observed 49.5%            all 37.0% observed 49.5%
constant dimensions 9                                   9
```

Two of 1,291 dimensions moved, and no new people were added, so the pool is
exactly as repetitive as it was. Two personas still agree on half of everything
that was actually measured about them. Fixing that needs more respondents, not
more attributes on the same 42.

**Nothing here is `forum_measured`.** That assignment type means "measured from
the person's own writing", and the 42 personas are survey respondents, not the
84 forum members. Both dimensions keep `assignment_type: generated` with
`source_ref: otofun_2026`; what the forum supplies is the prior behind the
value, not the value itself. The set of dimensions that may be used to score a
run is unchanged.

Within that limit the individual values are not arbitrary: a persona that gets
a kinship register gets the pair implied by its **own measured** age and
gender, and only the kinship-versus-neutral split comes from the forum.

**The behavioural comparison was not run.** The structural numbers above say
the personas are better specified; they do not prove the simulated users behave
better. The test that would — replay the same stimuli against both pools and
check whether each persona now holds one register instead of drifting — needs
OpenRouter credit, and the account is at -$0.09. It is the first thing to run
once credit is restored.

That drift is measured and real. Across his 26 conversations in
`data/vita-drive-agent-results-3p9i.jsonl`, the single persona Lê Văn Long
opened with *tôi* (12), *mình* (5), *anh/chị* (5) and *tao/mày* (3) — not a
varied person but an unconstrained model, because the dimension that governs it
was missing from his file.

## Reproducing

```
uv run python scripts/crawl_otofun_posts.py --out <scratch>/otofun_posts.jsonl
uv run python scripts/measure_forum_language.py <scratch>/otofun_posts.jsonl \
    -o persona/datasets/vn-drivers/forum_measurements.json
uv run python scripts/apply_forum_persona_layer.py \
    --measurements persona/datasets/vn-drivers/forum_measurements.json \
    --pool <base pool> --out persona/datasets/vn-drivers
```

The last two steps are deterministic. The crawl is not: the board moves, so a
later run measures a later population.

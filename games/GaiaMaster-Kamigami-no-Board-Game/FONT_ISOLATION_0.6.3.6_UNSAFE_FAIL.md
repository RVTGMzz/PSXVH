# Gaia Master — Font Isolation 0.6.3.6 EARLY-FLAG POST-COPY SENTINEL — UNSAFE FAIL

Runtime test date: **2026-09-12**

## Purpose

0.6.3.5 attempted a post-copy RAM sentinel but checked `s0 == 0x889F` too late in the pipeline. The sentinel was not visible, so target identity at that late hook was considered unreliable.

0.6.3.6 attempted to solve only target identity:

```text
metadata stage: target 0x889F -> FLAG = 1
other glyphs -> FLAG = 0
late post-copy hook reads FLAG only
```

The intended sentinel remained:

```text
rows 10..11 = dark/gray full band
rows 12..15 = bright white full band
```

## Runtime result

**UNSAFE FAIL.**

Observed twice:

```text
Sony logo appears
-> game freezes immediately afterward
-> Character Select is never reached
```

Therefore:

- no sentinel result exists;
- no inference about converted rows 12..15 is valid from this build;
- do not retest 0.6.3.6.

## What changed from stable 0.6.3.5

0.6.3.6 introduced persistent mutable target state in the executable cave and enlarged the early metadata hook so it set/cleared that state for every glyph.

The stable 12x16 source/copy/sprite architecture itself was not the new idea under test.

## Strongest lesson

A region that is zero-filled in the executable file is not automatically safe as long-lived mutable runtime state.

Do not use another persistent global/cave FLAG to carry target identity across the font pipeline.

## Next direction

Return to the stable 0.6.3.5 / 0.6.3.3 path and reverse exact arguments/registers around `0x8003C67C`.

Preferred target identity:

1. unique extended source glyph pointer;
2. metadata source pointer already present in the current call;
3. target-specific height/source combination;
4. a local register/stack argument inside the copy routine.

Next diagnostic must be local to the copy call and must not:

- trust late `s0`;
- create persistent/global target state;
- mutate shared cache allocator/cursor state.

The unresolved question remains:

> Do converted rows 12..15 exist after the 16-row copy routine?

# Gaia Master — Font Isolation 0.6.3.12 CONTROLLED RAM TAIL MIRROR — DIAGNOSTIC FAIL

Runtime date: 2026-09-12.

## Intended diagnostic

At post-copy hook `0x8003CC4C`, target was selected using:

```text
lhu 18(sp) == 15
```

Then probe assumed:

```text
dest = *(s1+100)
```

and wrote:

```text
rows6..7   = dark control
rows12..15 -> rows8..11 mirror
```

## Runtime result

- `TEST` becomes vertical;
- target becomes block/texture garbage;
- the intended control/mirror pattern cannot be read reliably;
- no valid conclusion about rows12..15 can be made.

## Conclusion

0.6.3.12 is a **diagnostic failure**, not proof that tail rows exist or do not exist.

Strongest implication:

- writing through `*(s1+100)` at `0x8003CC4C` perturbs data/state that affects glyph layout;
- therefore the model "state+100 is safely writable current converted destination after the call" is not trusted;
- alternatively the hook clobbers registers/state that remain live after `0x8003CC4C`.

Do not retest 0.6.3.12.
Do not make another post-copy write to `state+100` until raw caller/callee dataflow is reverse-proven.

## Next action

Use read-only executable dump/disassembly before any next runtime patch:

```text
GaiaMaster_063_REVERSE_DUMP_0.1.zip
```

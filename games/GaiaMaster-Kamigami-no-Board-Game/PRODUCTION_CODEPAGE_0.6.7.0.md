# Gaia Master 0.6.7.0 Production Codepage 60

Current `vi_full` inventory requires 60 custom Vietnamese glyphs. The verified conservative zero-hit atlas capacity is 64 slots, so the current corpus fits with 4 reserve slots.

Architecture remains locked to native 12x12 / 72-byte / 4bpp and static mapping-only routing. 0.6.6.1 remains the last-good runtime baseline for glyph composition and vertical alignment. Wide horizontal spacing is accepted as visual polish for this phase.

Frozen production atlas slots use 34 completely unmapped zero-hit slots plus 26 mapped-but-static-unused zero-hit slots. Reserve zero-hit slots: 794, 807, 821, 824.

The 0.6.7.0 multi-UI proof installs all 60 current `vi_full` custom glyphs, then tests three nearby setup strings: `Đã ổn?`, `Chọn tướng`, and `Nhấn O`.

Do not revive the 6x12 narrow path, 12x16, composite overlay, pointer redirect, or spacing-driven renderer changes.

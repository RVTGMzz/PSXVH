# ASCII Capacity Test 0.2.2 — Result

## Runtime result

User confirmed the ASCII 1-byte test does **not** render readable Latin text. Instead, the game shows garbled symbols / incorrect glyphs.

Test strings included:

- `XAC NHAN CAI DAT?`
- `CHON NHAN VAT`
- `NHAN NUT O`

The builder itself succeeded after the Windows JSON encoding fix, so this result is a renderer/encoding behavior result, not a build failure.

## Conclusion

- Plain ASCII 1-byte is **not suitable** for the current text renderer path.
- The game appears to expect Shift-JIS / 2-byte glyph codes on this path.
- Keep the working full-width Latin Shift-JIS strategy for the playable translation build.
- Do not retry ASCII as the main localization encoding unless the renderer is hooked/replaced.

## Next direction

1. Continue large-batch translation using full-width Latin as the working fallback.
2. Keep a separate natural Vietnamese source column with full diacritics.
3. Reverse the font/glyph rendering path and test custom glyphs for Vietnamese diacritics.
4. If a custom glyph table or renderer hook succeeds, re-encode the master translation without retranslating the text.

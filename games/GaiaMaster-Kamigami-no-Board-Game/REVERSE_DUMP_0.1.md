# Gaia Master — 0.6.3 Reverse Dump 0.1

Purpose: replace another speculative runtime probe with a read-only executable dump.

Tool:

```text
GaiaMaster_063_REVERSE_DUMP_0.1.zip
```

Launcher:

```text
00_RUN_REVERSE_DUMP.cmd
```

Input:
- CLEAN Gaia Master BIN, or
- Alpha 0.6.1 FRONT BIN.

Output:

```text
GaiaMaster_063_REVERSE_DUMP.txt
```

The tool does not modify the ROM and does not require emulator boot.

Dump ranges:

```text
0x8003C180..0x8003C780  renderer metadata + copy routine
0x8003C880..0x8003CE80  caller/cache/record path
0x8003D380..0x8003D540  cache page init
0x8003D980..0x8003DAA0  final primitive consumer
0x8003DB40..0x8003DC40  page flush/upload
```

Primary questions:
1. destination register lifetime inside `0x8003C67C`;
2. meaning/lifetime of `s1+100` before and after the copy call;
3. exact cache Y assignment and texture-V construction;
4. whether converted rows12..15 are contiguous or rebased;
5. live-register requirements around `0x8003CC4C`.

No next runtime build should be made until this report is analyzed.

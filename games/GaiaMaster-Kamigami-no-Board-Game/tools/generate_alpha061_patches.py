#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import csv, json, re

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / 'translation'

MASTER_PARTS = [TRANS / f'TRANSLATION_MASTER_0.6_part{i:02d}.csv' for i in range(1, 7)]
FRONT = TRANS / 'FRONT_DEMO_ADDED_061.csv'
OUT = Path(__file__).resolve().parent / 'patches_alpha061.json'

EXTENTS = {'SLPS_020.75': 24, 'PRGPACK.BDP': 2679}


def fullwidth_runtime(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s[i] == '%':
            m = re.match(r'%[+\-0-9.]*[sdifuxX]', s[i:])
            if m:
                out.append(m.group(0))
                i += len(m.group(0))
                continue
        if s.startswith('/V', i) or s.startswith('/v', i):
            out.append(s[i:i+2])
            i += 2
            continue
        c = s[i]
        if c == ' ':
            out.append('　')
        elif '!' <= c <= '~':
            out.append(chr(ord(c) + 0xFEE0))
        else:
            out.append(c)
        i += 1
    return ''.join(out)


def make_patch(file_name, off, jp, vi):
    orig = jp.encode('cp932')
    enc = fullwidth_runtime(vi).encode('cp932')
    if len(enc) > len(orig):
        return None
    new = enc + b'\x00' * (len(orig) - len(enc))
    return {
        'file': file_name,
        'extent': EXTENTS[file_name],
        'file_offset': off,
        'orig_hex': orig.hex(),
        'new_hex': new.hex(),
        'jp': jp,
        'vi': vi,
    }


def main():
    patches = []
    seen = set()

    for path in MASTER_PARTS:
        with path.open(encoding='utf-8-sig', newline='') as f:
            for r in csv.DictReader(f):
                file_name = r['file']
                off = int(r['offset_hex'], 16)
                vi = r['vi_game_current']
                if not vi or (file_name, off) in seen:
                    continue
                p = make_patch(file_name, off, r['japanese'], vi)
                if p is not None:
                    patches.append(p)
                    seen.add((file_name, off))

    with FRONT.open(encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            file_name = 'PRGPACK.BDP'
            off = int(r['offset_hex'], 16)
            if (file_name, off) in seen:
                continue
            p = make_patch(file_name, off, r['japanese'], r['vi_no_accents'])
            if p is None:
                raise RuntimeError('Front patch too long at 0x%X' % off)
            patches.append(p)
            seen.add((file_name, off))

    patches.sort(key=lambda x: (x['file'], x['file_offset']))
    OUT.write_text(json.dumps(patches, ensure_ascii=True, indent=2), encoding='ascii')
    print('Generated patches:', len(patches))
    print('Output:', OUT)
    if len(patches) != 397:
        raise SystemExit('Expected 397 patches, got %d' % len(patches))


if __name__ == '__main__':
    main()

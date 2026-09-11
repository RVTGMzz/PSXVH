#!/usr/bin/env python
# -*- coding: ascii -*-
from __future__ import print_function
import os, sys, hashlib, shutil, struct, binascii

EXPECTED_SHA1 = 'f4d5298583c90d89c4b7e51d2dde160ee07f2aec'
PRG_EXTENT = 2679

PATCHSETS = {
    'first_string_s3122': [
        (PRG_EXTENT, 0xDDAB4, '82a0', '82a2'),
    ],
    'slot_s3123': [
        (PRG_EXTENT, 0xDE110,
         '8272826b826e827382f082a682e782f182c582cb',
         '8272826b826e827382f082a682e782f182c582e6'),
    ],
    'control_other_pack': [
        (PRG_EXTENT, 0x510, '82e282e982cb', '82e282e982e6'),
    ],
    'balanced_swap': [
        (PRG_EXTENT, 0xDDD68,
         '8351815b838082f082cd82b682df82e982e6',
         '8351815b838082f082cd82b682df82e982cb'),
        (PRG_EXTENT, 0xDE110,
         '8272826b826e827382f082a682e782f182c582cb',
         '8272826b826e827382f082a682e782f182c582e6'),
    ],
}

LABELS = {
    'first_string_s3122': 'FIRST_STRING_S3122',
    'slot_s3123': 'SLOT_S3123',
    'control_other_pack': 'CONTROL_OTHER_PACK',
    'balanced_swap': 'BALANCED_SWAP',
}

PY2 = sys.version_info[0] == 2

def barray_to_bytes(x):
    if PY2:
        return ''.join(chr(v) for v in x)
    return bytes(x)

def sha1_file(path):
    h = hashlib.sha1()
    f = open(path, 'rb')
    try:
        while True:
            c = f.read(8 * 1024 * 1024)
            if not c:
                break
            h.update(c)
    finally:
        f.close()
    return h.hexdigest()

ECC_F = [0] * 256
ECC_B = [0] * 256
EDC_LUT = [0] * 256

for i in range(256):
    j = ((i << 1) ^ (0x11D if (i & 0x80) else 0)) & 0xFF
    ECC_F[i] = j
    ECC_B[(i ^ j) & 0xFF] = i
    x = i
    for _ in range(8):
        x = (x >> 1) ^ (0xD8018001 if (x & 1) else 0)
    EDC_LUT[i] = x & 0xFFFFFFFF

def edc_compute(src):
    edc = 0
    for v in src:
        if not isinstance(v, int):
            v = ord(v)
        edc = (edc >> 8) ^ EDC_LUT[(edc ^ v) & 0xFF]
    return edc & 0xFFFFFFFF

def ecc_compute(src, major_count, minor_count, major_mult, minor_inc):
    size = major_count * minor_count
    dest = bytearray(major_count * 2)
    for major in range(major_count):
        index = (major >> 1) * major_mult + (major & 1)
        a = 0
        b = 0
        for _ in range(minor_count):
            t = src[index]
            if not isinstance(t, int):
                t = ord(t)
            index += minor_inc
            if index >= size:
                index -= size
            a ^= t
            b ^= t
            a = ECC_F[a]
        a = ECC_B[ECC_F[a] ^ b]
        dest[major] = a
        dest[major + major_count] = a ^ b
    return dest

def regen_sector(sec):
    s = bytearray(sec)
    s[2072:2076] = struct.pack('<I', edc_compute(s[16:2072]))
    hdr = s[12:16]
    s[12:16] = bytearray([0, 0, 0, 0])
    s[2076:2248] = ecc_compute(s[12:2076], 86, 24, 2, 86)
    s[2248:2352] = ecc_compute(s[12:2248], 52, 43, 86, 88)
    s[12:16] = hdr
    return s

def build(src, mode):
    if mode not in PATCHSETS:
        print('ERROR: Unknown mode:', mode)
        return 2
    got = sha1_file(src).lower()
    print('Input SHA1:', got)
    if got != EXPECTED_SHA1:
        print('ERROR: Wrong BIN or already patched BIN.')
        print('Expected:', EXPECTED_SHA1)
        return 3
    label = LABELS[mode]
    root, ext = os.path.splitext(src)
    out_bin = root + ' [DIAG ' + label + '].bin'
    out_cue = root + ' [DIAG ' + label + '].cue'
    shutil.copyfile(src, out_bin)
    changed = set()
    f = open(out_bin, 'r+b')
    try:
        for extent, file_offset, orig_hex, new_hex in PATCHSETS[mode]:
            srcb = binascii.unhexlify(orig_hex)
            dstb = binascii.unhexlify(new_hex)
            if len(srcb) != len(dstb):
                raise RuntimeError('Patch length mismatch')
            left = 0
            while left < len(srcb):
                logical = file_offset + left
                sec = extent + (logical // 2048)
                within = logical % 2048
                n = min(len(srcb) - left, 2048 - within)
                raw = sec * 2352 + 24 + within
                f.seek(raw)
                cur = f.read(n)
                exp = srcb[left:left+n]
                if cur != exp:
                    raise RuntimeError('Data mismatch sector %d offset %d' % (sec, within))
                f.seek(raw)
                f.write(dstb[left:left+n])
                changed.add(sec)
                left += n
        for sec in sorted(changed):
            f.seek(sec * 2352)
            raw = f.read(2352)
            if len(raw) != 2352:
                raise RuntimeError('Cannot read full sector %d' % sec)
            f.seek(sec * 2352)
            f.write(barray_to_bytes(regen_sector(raw)))
    finally:
        f.close()
    f = open(out_cue, 'w')
    try:
        f.write('FILE "' + os.path.basename(out_bin) + '" BINARY\n')
        f.write('  TRACK 01 MODE2/2352\n')
        f.write('    INDEX 01 00:00:00\n')
    finally:
        f.close()
    print('OK: BUILD SUCCESS')
    print('Changed sectors:', len(changed), sorted(changed))
    print('Output SHA1:', sha1_file(out_bin))
    return 0

def main():
    if len(sys.argv) < 3:
        print('Usage: diagnostic_0.1.8.py <mode> <original BIN>')
        return 1
    mode = sys.argv[1].lower()
    src = os.path.abspath(sys.argv[2])
    if not os.path.isfile(src):
        print('ERROR: Input not found:', src)
        return 2
    try:
        return build(src, mode)
    except Exception as e:
        print('ERROR:', repr(e))
        return 9

if __name__ == '__main__':
    sys.exit(main())

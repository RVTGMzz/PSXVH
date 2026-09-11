#!/usr/bin/env python3
# -*- coding: ascii -*-
from __future__ import print_function
import os, sys, json, hashlib, shutil, struct

EXPECTED_BIN_SHA1 = "f4d5298583c90d89c4b7e51d2dde160ee07f2aec"

FILES = {
    "SLPS_020.75": {
        "extent": 24,
        "size": 487424,
        "sha1": "1dfeb6b7cfda59c108dde2dc0b8abda9a40e6ae5",
    },
    "PRGPACK.BDP": {
        "extent": 2679,
        "size": 1534236,
        "sha1": "a9b195b8ae5d8cad7f4f755daa08337d4671632c",
    },
}

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
    if len(sec) != 2352:
        raise RuntimeError("Bad raw sector length")
    s = bytearray(sec)
    if s[15] != 2:
        raise RuntimeError("Expected MODE2 sector")
    if s[18] & 0x20:
        raise RuntimeError("Unexpected Mode2/Form2 sector; refusing to patch")
    if s[16:20] != s[20:24]:
        raise RuntimeError("Mode2 subheader copies do not match")
    s[2072:2076] = struct.pack("<I", edc_compute(s[16:2072]))
    hdr = bytes(s[12:16])
    s[12:16] = b"\x00\x00\x00\x00"
    s[2076:2248] = ecc_compute(s[12:2076], 86, 24, 2, 86)
    s[2248:2352] = ecc_compute(s[12:2248], 52, 43, 86, 88)
    s[12:16] = hdr
    return bytes(s)

def sha1_bytes(data):
    h = hashlib.sha1(); h.update(data); return h.hexdigest()

def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            c = f.read(8 * 1024 * 1024)
            if not c: break
            h.update(c)
    return h.hexdigest()

def read_iso_file(rawf, extent, size):
    out = bytearray(); remaining = size; sector = extent
    while remaining:
        n = min(2048, remaining)
        rawf.seek(sector * 2352 + 24)
        chunk = rawf.read(n)
        if len(chunk) != n: raise RuntimeError("Short read at raw sector %d" % sector)
        out.extend(chunk); remaining -= n; sector += 1
    return out

def write_changed_iso_file(rawf, extent, original, modified, changed_sectors):
    if len(original) != len(modified): raise RuntimeError("File size changed unexpectedly")
    total = len(original); sectors = (total + 2047) // 2048
    for i in range(sectors):
        a = i * 2048; b = min(a + 2048, total)
        if original[a:b] == modified[a:b]: continue
        sec = extent + i
        rawf.seek(sec * 2352)
        raw = bytearray(rawf.read(2352))
        if len(raw) != 2352: raise RuntimeError("Short raw sector read %d" % sec)
        if raw[15] != 2 or (raw[18] & 0x20): raise RuntimeError("Sector %d is not MODE2/Form1" % sec)
        raw[24:24 + (b-a)] = modified[a:b]
        rawf.seek(sec * 2352); rawf.write(bytes(raw)); changed_sectors.add(sec)

def bdp_checksum(block):
    s = (sum(block[:4]) + sum(block[8:])) & 0xFFFF
    return (((~s) & 0xFFFF) << 16) | s

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    patches_path = os.path.join(here, "patches_alpha061.json")
    with open(patches_path, "r", encoding="utf-8") as f:
        patches = json.load(f)
    if len(sys.argv) >= 2:
        src = os.path.abspath(sys.argv[1])
    else:
        src = os.path.join(here, "GaiaMaster - Kamigami no Board Game (Japan).bin")
    if not os.path.isfile(src):
        print("[ERROR] Original BIN not found:"); print(src); return 2
    got = sha1_file(src).lower(); print("Input SHA1:", got)
    if got != EXPECTED_BIN_SHA1:
        print("[ERROR] Wrong game image or already patched image."); print("Expected:", EXPECTED_BIN_SHA1); return 3
    with open(src, "rb") as rf:
        originals = {}
        for name, meta in FILES.items():
            data = read_iso_file(rf, meta["extent"], meta["size"])
            got_file = sha1_bytes(data); print("%s SHA1: %s" % (name, got_file))
            if got_file != meta["sha1"]:
                print("[ERROR] Embedded file mismatch:", name); return 4
            originals[name] = data
    work = {k: bytearray(v) for k,v in originals.items()}
    prg_orig = originals["PRGPACK.BDP"]
    magic, top_stored, toc_size, count = struct.unpack_from("<IIII", prg_orig, 0)
    if magic != 0x10F0 or bdp_checksum(prg_orig) != top_stored:
        raise RuntimeError("PRGPACK top-level checksum verification failed")
    payload_base = 8 + toc_size
    entries = []
    for i in range(count):
        rel, size = struct.unpack_from("<II", prg_orig, 16 + i*8)
        start = payload_base + rel; end = start + size; block = prg_orig[start:end]
        if len(block) != size or struct.unpack_from("<I", block, 0)[0] != 0x10F0:
            raise RuntimeError("Bad nested BDP entry %d" % i)
        stored = struct.unpack_from("<I", block, 4)[0]
        if bdp_checksum(block) != stored:
            raise RuntimeError("Nested BDP checksum verification failed at entry %d" % i)
        entries.append((i,start,end))
    touched_entries = set(); applied = 0
    for p in patches:
        name = p["file"]; off = int(p["file_offset"])
        orig = bytes.fromhex(p["orig_hex"]); new = bytes.fromhex(p["new_hex"])
        if len(orig) != len(new): raise RuntimeError("Patch length mismatch at %s 0x%X" % (name, off))
        buf = work[name]; cur = bytes(buf[off:off+len(orig)])
        if cur != orig: raise RuntimeError("Original bytes mismatch at %s 0x%X" % (name, off))
        buf[off:off+len(new)] = new; applied += 1
        if name == "PRGPACK.BDP":
            hit = [(i,a,b) for (i,a,b) in entries if a <= off and off+len(orig) <= b]
            if len(hit) != 1: raise RuntimeError("PRGPACK patch 0x%X crosses/escapes nested entry" % off)
            touched_entries.add(hit[0][0])
    prg = work["PRGPACK.BDP"]
    for i,start,end in entries:
        if i not in touched_entries: continue
        block = bytearray(prg[start:end]); new_chk = bdp_checksum(block)
        struct.pack_into("<I", prg, start + 4, new_chk)
        block2 = bytes(prg[start:end])
        if struct.unpack_from("<I", block2, 4)[0] != bdp_checksum(block2):
            raise RuntimeError("Nested checksum write failed at entry %d" % i)
    top_chk = bdp_checksum(prg); struct.pack_into("<I", prg, 4, top_chk)
    if struct.unpack_from("<I", prg, 4)[0] != bdp_checksum(prg):
        raise RuntimeError("Top-level PRGPACK checksum write failed")
    stem, ext = os.path.splitext(src)
    out_bin = stem + " [VI Alpha 0.6.1 FRONT].bin"
    out_cue = stem + " [VI Alpha 0.6.1 FRONT].cue"
    shutil.copyfile(src, out_bin)
    changed_sectors = set()
    with open(out_bin, "r+b") as wf:
        for name, meta in FILES.items():
            write_changed_iso_file(wf, meta["extent"], originals[name], bytes(work[name]), changed_sectors)
        for sec in sorted(changed_sectors):
            wf.seek(sec * 2352); raw = wf.read(2352); wf.seek(sec * 2352); wf.write(regen_sector(raw))
    with open(out_cue, "w") as cf:
        cf.write('FILE "' + os.path.basename(out_bin) + '" BINARY\n')
        cf.write('  TRACK 01 MODE2/2352\n')
        cf.write('    INDEX 01 00:00:00\n')
    print(""); print("============================================")
    print("[OK] GAIA MASTER VI ALPHA 0.6.1 FRONT BUILD SUCCESS")
    print("============================================")
    print("Patched text locations:", applied)
    print("Touched nested BDP entries:", len(touched_entries), sorted(touched_entries))
    print("Changed raw sectors:", len(changed_sectors))
    print("Output SHA1:", sha1_file(out_bin)); print("Output CUE:", out_cue)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[ERROR]", repr(e)); sys.exit(9)

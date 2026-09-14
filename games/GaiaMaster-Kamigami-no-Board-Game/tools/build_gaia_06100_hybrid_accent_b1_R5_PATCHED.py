#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runtime-safe patched view of the historical 0.6.10 readable builder.

This keeps the large historical readable source stable in Git while applying the
production fixes proven by R5 plus the 0.6.55 runtime polish deterministically.
"""
from pathlib import Path

BASE = Path(__file__).with_name("build_gaia_06100_hybrid_accent_b1_LEGACY.py")
src = BASE.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global src
    if new in src:
        return
    if old not in src:
        raise RuntimeError(f"R5 patch anchor missing: {label}")
    src = src.replace(old, new, 1)


# Proof wording aligned with the final exact contract.
replace_once(
    '(0xBFBEC, "この設定でいいかしら？", "Đã ổn?"),',
    '(0xBFBEC, "この設定でいいかしら？", "Xác nhận?"),',
    "proof Xac nhan",
)
replace_once(
    '(0xBFE4C, "○ボタンをおしてね！", "Nhấn O"),',
    '(0xBFE4C, "○ボタンをおしてね！", "Nhấn O!"),',
    "proof Nhan O",
)

# Runtime-driven intro rewrite. All replacements keep the original fixed fields.
INTRO_REPLACEMENTS = {
    '0xC00B4: "Thần chiến",': '0xC00B4: "Thần chiến!",',
    '0xC00D0: "Người=cờ",': '0xC00D0: "Người: cờ",',
    '0xC00E4: "Thếgiới=bàncờ",': '0xC00E4: "Đời là bàn cờ",',
    '0xC0100: "Ko chống",': '0xC0100: "Khuất phục",',
    '0xC0118: "Lực thần",': '0xC0118: "Trước thần",',
    '0xC0130: "Đất ảo",': '0xC0130: "Miền ảo",',
    '0xC0144: "Vua tu sĩ",': '0xC0144: "Vua,tu sĩ",',
    '0xC0158: "Luật Gaia",': '0xC0158: "Theo luật Gaia",',
    '0xC0194: "Tan nát hết",': '0xC0194: "Tan biến hết",',
    '0xC01DC: "Đến lúc!",': '0xC01DC: "Bắt đầu!",',
    '0xC01F0: "Thời Gaia Master",': '0xC01F0: "Trò Gaia Master",',
    '0xC0218: "Lực địa loạn",': '0xC0218: "Đại lục loạn",',
    '0xC0234: "100 năm mệnh",': '0xC0234: "100 năm một lần",',
    '0xC0258: "Đất ảo trời",': '0xC0258: "Miền đất ảo",',
    '0xC0274: "Che cả trời",': '0xC0274: "Trời u tối",',
    '0xC028C: "Thế giới mất chủ",': '0xC028C: "Thế giới đổi chủ",',
}
for old, new in INTRO_REPLACEMENTS.items():
    replace_once(old, new, old.split(":", 1)[0])

# R5 production staging: consume Core/translation first, never silently bypass it.
OLD_FETCH = '''def fetch_csv(here, name):
    local = os.path.join(here, name)
    if os.path.isfile(local):
        with open(local, "rb") as f:
            data = f.read()
        return data.decode("utf-8-sig"), "local"

    url = TRANSLATION_BASE + name
'''
NEW_FETCH = '''def fetch_csv(here, name):
    # Production staging lives in Core/translation. Always prefer that tree.
    # Older builders used `here` (= Core/tools), which silently bypassed staged
    # Translation Master files and could fall back to GitHub/cache instead.
    translation_dir = os.path.normpath(os.path.join(here, "..", "translation"))
    staged = os.path.join(translation_dir, name)
    if os.path.isfile(staged):
        with open(staged, "rb") as f:
            data = f.read()
        return data.decode("utf-8-sig"), "local-translation"

    # Legacy tools-local cache remains a secondary fallback only.
    local = os.path.join(here, name)
    if os.path.isfile(local):
        with open(local, "rb") as f:
            data = f.read()
        return data.decode("utf-8-sig"), "local-tools-cache"

    url = TRANSLATION_BASE + name
'''
replace_once(OLD_FETCH, NEW_FETCH, "fetch_csv staged translation")

# Structural exact-patch overlap gate.
SORT_ANCHOR = '    patches.sort(key=lambda x: (x["file"], x["offset"]))\n\n'
OVERLAP_BLOCK = '''    patches.sort(key=lambda x: (x["file"], x["offset"]))

    # Structural safety: exact patches must never overlap byte ranges.
    _last = {}
    for _p in patches:
        _name = _p["file"]
        _a = _p["offset"]
        _b = _a + len(_p["orig"])
        if _name in _last:
            _pa, _pb, _prev = _last[_name]
            if _a < _pb:
                raise RuntimeError(
                    "Overlapping exact patches: %s+0x%X..0x%X %r overlaps "
                    "%s+0x%X..0x%X %r"
                    % (_name, _pa, _pb, _prev["jp"],
                       _name, _a, _b, _p["jp"])
                )
        _last[_name] = (_a, _b, _p)

'''
if "Structural safety: exact patches must never overlap byte ranges." not in src:
    if SORT_ANCHOR not in src:
        raise RuntimeError("R5 patch anchor missing: patch sort")
    src = src.replace(SORT_ANCHOR, OVERLAP_BLOCK, 1)

# Runtime-evidenced font polish: raise Đ/đ crossbar by one pixel.
replace_once(
    '        yy = max(y0, min(y1, (y0 + y1) // 2))',
    '        yy = max(y0, min(y1, (y0 + y1) // 2 - 1))',
    "D crossbar",
)

# Keep human-readable report strings aligned where they exist.
src = src.replace("  Đã ổn?", "  Xác nhận?")
src = src.replace("  Nhấn O\n", "  Nhấn O!\n")

exec(compile(src, str(BASE) + "<R5_PATCHED>", "exec"), globals(), globals())

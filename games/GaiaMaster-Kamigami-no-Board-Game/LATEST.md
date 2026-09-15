# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-16**

## CURRENT — B51R1 GUARDED EXACT-OFFSET / FROZEN-60 TEXT LAYER

Trọng tâm hiện tại: đưa toàn bộ B50 exact-offset source layer vào production một cách có guard, **không đụng font**.

Trạng thái hiện tại:

- B50 exact-offset static byte-fit: **PASS**
- B51R1 static CI: **PASS**
- B51R1 real CLEAN guarded dry-run: **chưa chạy trong môi trường hiện tại**
- B51R1 real build/static-byte verification: **chưa chạy trong môi trường hiện tại**
- Runtime PASS: **NO**

## CLEAN contract

Exact Japan CLEAN BIN SHA1:

`f4d5298583c90d89c4b7e51d2dde160ee07f2aec`

Không patch từ BIN lạ hoặc BIN đã mod khi dùng làm CLEAN source oracle.

## B50 canonical checkpoint

Canonical B50 overlay:

`translation/source_layer/checkpoint_B50/GaiaMaster_RUNTIME_CANDIDATE_EXACT_OVERLAY_B50.csv`

Raw SHA256:

`448bc34afa675299b0de20c54d804d5765e7f9954f67c39058884b318de504b7`

Raw size:

`162851`

B50:

- exact candidates: `1229/1229`
- direct `vi_full`: `41`
- compact candidates: `1188`
- duplicate keys: `0`
- overlapping spans: `0`
- byte-fit violations: `0`
- ROM/font/pointer modified: NO

B50 vẫn là canonical validated binary/source checkpoint vì chưa có BIN thật trong connected runtime để chạy B51R1 binary pass.

## B51 production discovery

B51 production encoder audit phát hiện B50 có một lớp nợ mà static byte-fit chưa bắt được:

- `19` ký tự tiếng Việt nằm ngoài frozen 60-glyph codepage
- ảnh hưởng `64` exact runtime rows

Unsupported raw-B50 character set:

`À Á Â É è õ ý Ă Ư ẳ ẵ ẹ Ế ễ Ồ Ở ỡ Ừ ỳ`

Không mở rộng font để xử lý lỗi này.

## B51R1 text-only correction layer

Correction manifest:

`translation/source_layer/B51_RUNTIME_CHARSET_CORRECTIONS.csv`

Production wrapper:

`tools/build_gaia_b51r1_guarded_exact_overlay.py`

Quy tắc:

- B50 gốc không bị sửa
- exact-key correction `64/64`
- mỗi correction phải match đúng old candidate
- không đổi token/control order
- không được dài hơn field
- không được vượt byte budget B50 đã duyệt
- thêm glyph mới: `0`
- font/mapping mutation: NO

## B51R1 STATIC CI PASS

Static validator:

`tools/validate_gaia_b51_static.py`

Workflow:

`.github/workflows/gaia-b51-static-validation.yml`

Validated commit:

`33a5049bf6dc932a95892eeb1dbb99033c8d074b`

GitHub Actions run:

`35005218964`

CI result:

```text
B51/B51R1 import + syntax           = PASS
B50 restored SHA256                = PASS
B50 restored size                  = 162851/162851
B50 exact candidates               = 1229/1229
Raw B50 unsupported chars          = 19/19 known debt
Raw B50 bad rows                   = 64/64 known debt
B51R1 corrections                  = 64/64
Corrected frozen-60 charset        = PASS, 0 unsupported rows
B50 canonical mutated              = NO
New font glyphs                    = 0
B40 / Batch42 protected            = 560/560
B43 protected                      = 102/102
Combined historical               = 662/662
Intro protected                    = 19/19
Legacy Alpha                       = 397/397
Translation Master                = 596/596
Duplicate/overlap/byte/token       = PASS
ROM/font/pointer modified          = NO
Runtime PASS                       = NO
```

Proof:

`translation/source_layer/checkpoint_B51/B51R1_STATIC_CI_PROOF.txt`

## Historical B43 padded fields

B51 CI cũng bắt được một giả định validator sai ở `PRGPACK.BDP+0xDE0A0`.

B43 proven builder cho phép `field_bytes` lớn hơn literal Japanese CP932 bytes vì một số field có padding. B51R1 hiện dùng đúng historical contract:

`field_bytes >= literal Japanese bytes`

Rule này chỉ dùng khi reconstruct historical B40/B43 manifests. B50 exact source identity vẫn giữ strict.

## Hard historical contracts

```text
Batch42/B40 exact = 560/560
Batch43 exact     = 102/102
Combined          = 662/662
Legacy Alpha      = 397/397
TranslationMaster = 596/596
Intro exact       = 19/19
```

B51R1 hiện có `0` overlap với B40, B43 và intro19.

## Architecture lock

```text
native 12x12 / 72-byte / 4bpp / LOW nibble first
static mapping-only
frozen 60-glyph Vietnamese codepage
no renderer hook
no pointer redirect
no 12x16
no 6x12
no composite overlay
```

Font work parked. Không tự quay lại Batch45R2/font-first.

## Tools chạy tiếp

Dry-run Python:

```text
python tools/build_gaia_b51r1_guarded_exact_overlay.py "GaiaMaster - Kamigami no Board Game (Japan).bin"
```

Dry-run Windows:

`tools/00_RUN_B51R1_GUARDED_DRYRUN.cmd`

Sau khi dry-run thật PASS mới build:

```text
python tools/build_gaia_b51r1_guarded_exact_overlay.py "GaiaMaster - Kamigami no Board Game (Japan).bin" --build-from "KNOWN_GOOD_RUNTIME_BASE.bin"
```

Build Windows:

`tools/00_BUILD_B51R1_GUARDED_EXACT_OVERLAY.cmd`

Không dùng CLEAN BIN làm `--build-from` vì B51R1 là text-only, không cài font.

## Claim policy

Hiện được phép gọi:

- `B50 static byte-fit PASS`
- `B51R1 STATIC CI PASS`

Chưa được gọi:

- `B51R1 guarded CLEAN dry-run PASS`
- `B51R1 build PASS`
- `Runtime PASS`

Gameplay screenshots vẫn là điều kiện bắt buộc trước Runtime PASS.

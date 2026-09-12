# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime 0.6.3.11 RAM TAIL MIRROR**.

## Chốt hiện tại

- Custom Vietnamese atlas path đã PASS từ 0.6.2.13.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics.
- Extended-height 12x16 vẫn là hướng production.
- 0.6.3.7 SOURCE ROW SENTINEL: rows10..11 hiện, rows12..15 không hiện đủ.
- 0.6.3.10 dùng per-glyph height thật tại `sp+18`; runtime ổn nhưng target y hệt 0.6.3.7, nên final primitive height không còn là blocker chính.
- 0.6.3.11 RAM TAIL MIRROR: **runtime không xuất hiện bright 4-row mirror block**; target gần như y hệt 0.6.3.7/0.6.3.10.

## Vì sao 0.6.3.11 vẫn chưa kết luận tail bị mất

0.6.3.11 mirror:

```text
converted rows12..15: dest+96..127
-> rows8..11:         dest+64..95
```

Nhưng probe này không có visual control độc lập để chứng minh cả hai việc:

1. post-copy hook đã chạy đúng target;
2. `*(s1+100)` tại hook thật sự là current converted destination.

Vì vậy `no mirror` còn mơ hồ giữa:

- lower converted rows thật sự không chứa expected bright tail;
- hoặc hook/destination assumption chưa đúng.

## CURRENT — 0.6.3.12 CONTROLLED RAM TAIL MIRROR

Start từ 0.6.3.11 nhưng target identity đổi sang field đã dataflow-proven:

```text
lhu 18(sp) == 15
```

Tại `0x8003CC4C`, trước allocator advance:

```text
dest = *(s1+100)
```

Probe tạo hai tín hiệu trong cùng target:

### CONTROL

```text
converted rows6..7 = full 0x77 dark/gray band
```

Rows6..7 nằm chắc trong vùng đang nhìn thấy.

### MIRROR

```text
converted rows12..15 -> rows8..11
```

Source rows12..15 vẫn là full `0x11` bright white.

### Interpretation

- **dark control + bright 4-row mirror** => hook/dest đúng và tail tồn tại sau conversion; blocker nằm downstream cache/VRAM placement.
- **dark control nhưng không bright mirror** => hook/dest đúng, nhưng rows12..15 không có expected content ngay sau copy; reverse tiếp `0x8003C67C` / loop state / destination writes.
- **không dark control** => hook/destination model vẫn sai; chưa được kết luận tail loss.

Package:

```text
GaiaMaster_FontIsolation_0.6.3.12_CONTROLLED_RAM_TAIL_MIRROR.zip
```

Launcher:

```text
00_RUN_PROBE_06312.cmd
```

## Do not repeat

- Không quay lại Krom.
- Không polish production stacked accents trong 12x12.
- Không retest 0.6.2.18.
- Không retest 0.6.3.0..0.6.3.11.
- Không patch shared `0x8003CD94..0x8003CDB4` kiểu 0.6.3.1.
- Không persistent/global flag kiểu 0.6.3.6.
- Không force height16 global kiểu 0.6.3.8.
- Không dùng `s3+2` như glyph metadata.

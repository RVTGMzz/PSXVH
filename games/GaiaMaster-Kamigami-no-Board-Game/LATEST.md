# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-12 sau runtime 0.6.3.12 CONTROLLED RAM TAIL MIRROR**.

## Chốt hiện tại

- Custom Vietnamese atlas path đã PASS từ 0.6.2.13.
- Native 12x12 bị loại cho production stacked Vietnamese diacritics.
- Extended-height 12x16 vẫn là hướng production.
- 0.6.3.7 SOURCE ROW SENTINEL là runtime sạch nhất: rows10..11 hiện, rows12..15 không hiện đủ.
- 0.6.3.10 chứng minh final primitive visible-height không phải blocker chính.
- 0.6.3.11 RAM TAIL MIRROR không có mirror nhưng thiếu control nên inconclusive.
- 0.6.3.12 CONTROLLED RAM TAIL MIRROR = **DIAGNOSTIC FAIL / LAYOUT CORRUPTION**.

## Runtime 0.6.3.12

Ảnh runtime:

- `TEST` bị dựng dọc;
- target thành block/texture nhiễu;
- không thể đọc control/mirror theo thiết kế;
- vì chính post-copy RAM hook làm hỏng layout, kết quả không được dùng để kết luận về rows12..15.

=> assumption `*(s1+100)` có thể chưa phải current converted destination ở thời điểm hook, hoặc post-copy hook clobber/register/state đang còn live.
=> **không build tiếp runtime probe bằng cách ghi vào state+100** cho tới khi raw caller/copy dataflow được reverse lại từ executable thật.

## CURRENT — REVERSE ONLY / NO USER RUNTIME PROBE

Bước tiếp theo không boot game.

Tool read-only:

```text
GaiaMaster_063_REVERSE_DUMP_0.1.zip
```

Launcher:

```text
00_RUN_REVERSE_DUMP.cmd
```

Tool chỉ đọc CLEAN BIN hoặc Alpha 0.6.1 FRONT BIN và xuất:

```text
GaiaMaster_063_REVERSE_DUMP.txt
```

Các vùng được dump/disassemble:

```text
0x8003C180..0x8003C780  renderer metadata + copy routine
0x8003C880..0x8003CE80  caller/cache/record path
0x8003D380..0x8003D540  cache page init
0x8003D980..0x8003DAA0  final primitive consumer
0x8003DB40..0x8003DC40  page flush/upload
```

Mục tiêu reverse tiếp:

1. xác định register giữ destination pointer thật bên trong `0x8003C67C`;
2. xác định `state+100` trước/sau `jal` có còn là current dest hay không;
3. xác định nơi 16-row converted data được đặt trong cache page;
4. xác định record U/V/H lấy cache Y nào;
5. chỉ sau đó mới build runtime probe mới.

## Do not repeat

- không quay lại Krom;
- không polish production stacked accents trong 12x12;
- không retest 0.6.2.18;
- không retest 0.6.3.0..0.6.3.12;
- không patch shared `0x8003CD94..0x8003CDB4` kiểu 0.6.3.1;
- không persistent/global flag kiểu 0.6.3.6;
- không global force-height16 kiểu 0.6.3.8;
- không dùng `s3+2` như glyph metadata;
- không tiếp tục post-copy write vào `state+100` cho tới khi raw dataflow xác nhận lại.

# Gaia Master — trạng thái mới nhất

Cập nhật: **2026-09-13 sau nghiên cứu repo Việt hóa PS1 Yu-Gi-Oh! MCBB và reverse dump 0.1**.

## Chốt hiện tại

- Custom Vietnamese atlas path PASS từ 0.6.2.13.
- Native 12x12 không đủ nếu cố nhét toàn bộ `Ế/Ể/Ẳ/...` vào một glyph duy nhất mà vẫn giữ thân chữ full-size.
- Nhánh 0.6.3.x cố mở cell 12x12 -> 12x16 đã chạm quá nhiều state chung: converted cache, Y cursor, VRAM placement, primitive geometry và allocator.
- 0.6.3.12 làm layout `TEST` dựng dọc nên post-copy write probe bị loại.
- Reverse dump 0.1 xác nhận `state+100` vẫn là current converted destination ngay sau `jal 0x8003C67C`; nó chỉ được advance tại `0x8003CD94`.
- Tuy nhiên public repo `2ez4gcx/yugioh-mcbb-vi-patch` cho một bài học chiến lược: một bản Việt hóa PS1 hoàn thiện có thể đi theo hướng **font vẽ lại + một ít code adjustment**, không nhất thiết phải redesign renderer lớn.

## PIVOT — COMPOSITE ACCENT

Thay vì làm một glyph `Ế` cao 16px, giữ nguyên base letter native 12x12 và vẽ dấu bằng một glyph overlay thứ hai.

Proof concept 0.6.4.0:

```text
internal: ＴＥＳＴＥ亜
visual:   ＴＥＳＴẾ
```

- `Ｅ` = native full-size, shading nguyên bản;
- glyph `亜` = transparent accent-only `mũ + sắc`;
- riêng overlay được dịch `X -= 12`, `Y -= 4` để chồng lên E;
- toàn bộ atlas/cache/VRAM vẫn native 12x12 / 72-byte.

Không dùng:
- 12x16 source;
- 96-byte glyph;
- cache stride rewrite;
- CD94 allocator rewrite;
- sprite-height rewrite;
- persistent/global flag.

Package current:

```text
GaiaMaster_FontIsolation_0.6.4.0_COMPOSITE_ACCENT_OVERLAY.zip
```

Launcher:

```text
00_RUN_PROBE_0640.cmd
```

Runtime question duy nhất:

> Mũ + sắc có chồng sạch lên full-size native E để đọc thành `Ế` hay không?

Nếu PASS, 0.6.3.x extended-height trở thành research phụ, không còn là production blocker.

## Reverse dump 0.2

`GaiaMaster_063_REVERSE_DUMP_0.2.zip` vẫn có giá trị để hoàn tất reverse 0.6.3.x, nhưng **không còn chặn thử nghiệm composite 0.6.4.0**.

## Do not repeat

- không quay lại Krom;
- không polish một-glyph stacked accents trong 12x12;
- không retest 0.6.2.18;
- không retest 0.6.3.0..0.6.3.12;
- không patch shared `0x8003CD94..0x8003CDB4` kiểu 0.6.3.1;
- không persistent/global flag kiểu 0.6.3.6;
- không global force-height16 kiểu 0.6.3.8;
- không dùng `s3+2` như glyph metadata;
- không post-copy RAM write probe kiểu 0.6.3.12.

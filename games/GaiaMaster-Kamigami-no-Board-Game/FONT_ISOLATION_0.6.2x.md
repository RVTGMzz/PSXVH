# Gaia Master — Font Isolation 0.6.2.x

Checkpoint chi tiết cho chuỗi thử nghiệm tiếng Việt có dấu.

## Nền build

Tất cả test quan trọng sau giai đoạn đầu đều kế thừa:

- `Alpha 0.6.1 FRONT`
- 397 patch text
- output SHA1 runtime baseline: `54d2fb026bc3b71c79861e723caffb4114caa34c`

Visible probe ổn định:

```text
PRGPACK.BDP 0xBFD2C
キャラクターをえらんでね
```

Text-only replacement đã được nhìn thấy ở Character Select.

## Mục tiêu font

Mục tiêu cuối cùng là giữ `vi_full` có dấu và đưa các glyph tiếng Việt như:

```text
Ă Â Ê Ô Ơ Ư Đ
Á À Ả Ã Ạ
Ắ Ằ Ẳ Ẵ Ặ
Ế Ề Ể Ễ Ệ
Ớ Ờ Ở Ỡ Ợ
Ứ Ừ Ử Ữ Ự
```

vào renderer mà không phá text Nhật chưa dịch.

---

## Font Test 0.3

Diagnostic dựng từ ROM gốc, không kế thừa 397 patch.

Kết quả không dùng để đánh giá tiến độ translation vì sau intro game trông như ROM gốc. Không coi đây là PASS/FAIL chính thức của glyph injection.

---

## Alpha 0.6.2 HYBRID FONT

Ý tưởng:

- hook global `Krom2RawAdd` wrapper tại VA `0x80068208` / file `0x58A08`;
- custom codes `0x85xx` -> injected 16x15 Vietnamese atlas;
- normal Japanese -> BIOS font path gốc.

Runtime:

```text
TREO ngay sau logo PlayStation
```

Không thấy intro.

---

## Alpha 0.6.2.1 HYBRID HOTFIX

Thay vì hook global wrapper:

- hook renderer call-site `0x26CF4`;
- normal Japanese tail-jump về wrapper gốc;
- custom `0x85xx` -> atlas Việt.

Runtime:

```text
TREO sau logo PlayStation
```

=> vẫn chưa đủ dữ liệu để kết luận custom glyph sai.

---

## Font Isolation 0.6.2.2

Tách pass-through khỏi glyph injection.

### A

```text
renderer -> stub 8 byte -> wrapper gốc
```

Không custom code, không atlas.

Runtime:

```text
A = TREO
```

=> ngay pass-through cũng treo. Nghi code cave/runtime overwrite.

Code cave cũ:

```text
SLPS file offset 0x6FE10
```

---

## Font Isolation 0.6.2.3 SAFE CAVE

Chuyển stub sang vùng zero-padding tĩnh khác:

```text
SLPS file offset 0x5C0E0 .. 0x5C2B8
VA start 0x8006B8E0
length 472 bytes
```

### A2

Pass-through only.

Runtime:

```text
A2 = BOOT
```

### B2

- dùng mã Shift-JIS hợp lệ `0x889F` = `亜`;
- thử intercept thành custom glyph `Ế`;
- test đặt ở intro.

Runtime:

```text
B2 = BOOT
```

Nhưng user không thấy `Ế`, vì probe intro không đi qua đường render đang hook hoặc không phải vị trí quan sát phù hợp.

Kết luận quan trọng:

> Safe cave mới được runtime xác nhận an toàn.

---

## Font Isolation 0.6.2.4 VISIBLE MENU

Đưa probe sang Character Select đã xác nhận visible.

### C1 — text only

Payload:

```text
TEST亜
```

Runtime:

```text
C1 = HIEN TEST亜
```

=> offset text đúng, `0x889F` render bình thường.

### C2 — hook direct caller #1

Call-site:

```text
SLPS file offset 0x26CF4
```

Intercept `0x889F` -> glyph `Ế`.

Runtime:

```text
C2 = HIEN TEST亜
```

=> direct call-site #1 không phải đường glyph của Character Select probe.

---

## Font Isolation 0.6.2.5 SECOND RENDER PATH

Direct caller thứ hai tới wrapper:

```text
SLPS file offset 0x2CCA0
VA 0x8003C4A0
```

### D1

Pass-through.

Runtime:

```text
D1 = HIEN TEST亜
```

### D2

Intercept `0x889F` -> glyph `Ế`.

Runtime:

```text
D2 = HIEN TEST亜
```

=> direct caller #2 cũng không phải đường glyph của Character Select.

---

## Font Isolation 0.6.2.6 GLOBAL SAFE WRAPPER

Do cả hai direct caller đều không bắt probe, thử global wrapper lại nhưng lần này:

- dùng safe cave đã BOOT;
- không dùng invalid/custom `0x85xx`;
- chỉ intercept mã Shift-JIS hợp lệ `0x889F`;
- pass-through mô phỏng wrapper gốc.

### E1

Global pass-through.

Runtime:

```text
E1 = BOOT + TEST亜
```

### E2

Global wrapper intercept `0x889F` -> custom glyph `Ế`.

Runtime:

```text
E2 = HIEN TEST亜
```

---

## Kết luận hiện tại

Kết quả C2 + D2 + E2 loại khá mạnh giả thuyết rằng Character Select lấy glyph qua `Krom2RawAdd` path đã hook.

Đã xác nhận:

- text code `0x889F` vẫn render thành `亜`;
- cả hai direct caller và global wrapper hook đều không thay glyph này;
- safe cave mới hoạt động runtime;
- vấn đề không còn nằm ở chỗ code cave.

Vì vậy:

> **Dừng test thêm các biến thể Krom2RawAdd direct/global hook cho Character Select.**

## Giả thuyết mạnh tiếp theo

1. Character Select dùng custom glyph cache/font atlas riêng.
2. Glyph Nhật đã được preload/copy vào RAM/VRAM trước khi vẽ.
3. Renderer UI nhận Shift-JIS code nhưng lookup glyph qua table/cache khác.
4. Có font asset nén/custom format chưa được nhận diện như TIM chuẩn.

## NEXT TASK

Không build thêm Krom diagnostic.

Thay vào đó:

1. tìm bitmap/glyph `亜` trong RAM/VRAM/asset;
2. xác định kích thước + packing của glyph set;
3. truy code/index table dùng ở Character Select;
4. tạo **một probe duy nhất**:

```text
text vẫn = TEST亜
bitmap glyph 亜 -> bitmap Ế
```

Expected:

```text
TESTẾ
```

Nếu pass, mới mở rộng thành custom Vietnamese atlas/codepage.

## Quy tắc test tối ưu thời gian

- chạy test chính trước;
- control test chỉ chạy nếu test chính treo hoặc kết quả mơ hồ;
- ưu tiên Character Select vì đây là probe visible đã xác nhận;
- không bắt user đi sâu gameplay;
- không lặp lại nhánh kỹ thuật đã bị loại.

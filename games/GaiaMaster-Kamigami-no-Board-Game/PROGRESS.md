# Gaia Master: Kamigami no Board Game (Japan) — Tiến độ Việt hóa

Cập nhật: **2026-09-11, sau runtime test Alpha 0.6.1 FRONT**.

## Bản game mục tiêu

- Platform: PlayStation 1
- Region: Japan
- Serial: `SLPS-02075`
- Disc format: MODE2/2352 BIN/CUE
- SHA1 BIN gốc: `f4d5298583c90d89c4b7e51d2dde160ee07f2aec`
- Emulator test: DuckStation

## Những gì đã xác định chắc chắn

- `SLPS_020.75` chứa nhiều text gameplay/card/menu dạng Shift-JIS.
- `PRGPACK.BDP` là BDP archive chứa **60 nested BDP**.
- Nested BDP và top-level BDP dùng checksum additive 32-bit.
- Full-width Latin Shift-JIS đã được xác nhận hiển thị đúng trong game.
- ASCII 1-byte đã test sau khi checksum được sửa đúng và **hiển thị ký hiệu sai**, vì vậy đã loại.
- Patcher raw MODE2/Form1 + EDC/ECC đang hoạt động đúng.
- Một số menu/title lớn không xuất hiện như chuỗi Shift-JIS trong các vùng text đã scan, nên có khả năng là **graphic/texture** và phải patch ảnh riêng.

## Cấu trúc BDP đã reverse

Header quan sát được:

- `+0x00`: magic `0x000010F0`
- `+0x04`: checksum 32-bit
- `+0x08`: TOC size
- `+0x0C`: entry count
- sau đó là descriptor `(offset, size)` 8 byte/entry

Checksum:

```text
sum16 = sum(all bytes except checksum field +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Công thức đã verify trên **60/60 nested BDP** và top-level `PRGPACK.BDP`.

## Diagnostic đã chốt

### 0.1.9 checksum fix

- A `FIX_A_CHECKSUM`: **OK**
- B `FIX_SLOT_CHECKSUM`: **OK**
- C `FIX_FIRST_CHECKSUM`: **OK**
- D `FULLWIDTH_BATDAU_CHECKSUM`: **OK**

Kết luận: nguyên nhân treo của các patch trước là checksum nested BDP chưa được cập nhật.

### Visible Menu 0.2.1

Người dùng nhìn thấy trực tiếp:

```text
ＶＩＥＴＨＯＡＴＥＳＴ！
```

=> text patch thật sự được game đọc và full-width Latin render đúng.

### ASCII Capacity Test 0.2.2 / 0.2.2.1

- 0.2.2 ban đầu lỗi `UnicodeDecodeError('charmap', ...)` do Windows mở JSON bằng codepage mặc định.
- 0.2.2.1 sửa bằng JSON ASCII-safe + explicit UTF-8 reader; builder chạy thành công.
- Runtime: **ASCII 1-byte hiện ký hiệu lung tung**, không phải Latin bình thường.

=> **Loại ASCII 1-byte.** Runtime hiện dùng full-width Latin Shift-JIS.

## Lỗi launcher Windows đã gặp

Alpha 0.5 BAT từng báo:

```text
.bin was unexpected at this time.
```

Nguyên nhân: tên file có `(Japan).bin` nằm trong parenthesized `IF (...)` block của CMD. Dấu `)` trong tên file phá parser của batch.

Quy tắc từ đây:

- launcher BAT tránh parenthesized blocks khi biến có thể chứa dấu ngoặc;
- ưu tiên label + `goto`;
- cửa sổ build giữ mở và luôn ghi `build_log.txt`.

## Alpha 0.5 / 0.5.1 — runtime đã xác nhận

- 203 vị trí text.
- `SLPS_020.75`: 73 vị trí.
- `PRGPACK.BDP`: 130 vị trí.
- 9 nested BDP bị tác động: `0, 3, 4, 5, 6, 7, 8, 29, 30`.
- Alpha 0.5.1 sửa launcher BAT.
- Người dùng xác nhận **bản dịch hiển thị và game chạy**.

## Translation master 0.6

Master hiện có **596 vị trí** trong workflow.

Mỗi dòng giữ song song:

1. tiếng Nhật gốc;
2. `vi_full`: tiếng Việt chuẩn có dấu làm source-of-truth;
3. `vi_game_current`: fallback không dấu cho runtime full-width hiện tại.

Mục tiêu: khi custom font/glyph hoàn thành chỉ đổi encoding, **không dịch lại từ đầu**.

## Alpha 0.6 — LARGE BATCH

- **366 vị trí** patch an toàn với giới hạn slot hiện tại.
- Alpha 0.5: 203 vị trí.
- Thêm mới ở 0.6: **163 vị trí**.
- `SLPS_020.75`: 158 vị trí.
- `PRGPACK.BDP`: 208 vị trí.
- 9 nested BDP bị sửa: `0, 3, 4, 5, 6, 7, 8, 29, 30`.
- **230 vị trí** đã dịch nhưng chưa fit slot full-width, được đưa vào `PENDING_LONG_OR_REPACK_06.csv`.

Local verify:

```text
Patched text locations: 366
Touched nested BDP entries: 9 [0, 3, 4, 5, 6, 7, 8, 29, 30]
Changed raw sectors: 25
Output SHA1: 5a12d3209deee065c129945e169e632f4cec9a8e
```

## Alpha 0.6.1 FRONT DEMO — runtime đã test

Mục tiêu: **không bắt tester phải vào sâu gameplay mới thấy tiếng Việt**.

Đã thêm **31 patch front-loaded** trên nền Alpha 0.6, nâng tổng thành:

```text
Patched text locations: 397
Touched nested BDP entries: 9 [0, 3, 4, 5, 6, 7, 8, 29, 30]
Changed raw sectors: 26
Output SHA1: 54d2fb026bc3b71c79861e723caffb4114caa34c
```

Các vùng bổ sung:

- intro / lời dẫn đầu game;
- câu hỏi load Weapon Skill data;
- setup trước Character Select;
- xác nhận nhân vật / cài đặt;
- một số lựa chọn `CÓ / KHÔNG` fallback không dấu.

### Kết quả runtime 0.6.1

Người dùng xác nhận:

- **nhiều chỗ đầu game đã hiện Việt hóa**;
- vẫn còn **đa số text tiếng Nhật**;
- có màn intro bị **Nhật + Việt lẫn nhau** trong cùng màn.

Ví dụ screenshot có các fragment Việt kiểu:

```text
THEGIOI=BANCO
NGUOI=CO
```

nhưng vẫn có fragment Nhật chưa patch.

Đây không được xem là lỗi encoding. Intro được ghép từ nhiều text fragment và 0.6.1 mới thay một phần. Cần patch đủ toàn bộ fragment của từng màn để tránh UI nửa Nhật nửa Việt.

## Những text đầu game đã xác định là text thật

Các chuỗi sau có trong `PRGPACK.BDP` và patch bằng pipeline text hiện tại được:

```text
0xC0274  月も太陽もおおいかくす
0xC028C  世界はもはや人のものではなくなった
0xBFC20  武器スキルのデータをロードする？
```

0.6.1 đã bổ sung nhiều fragment intro/setup quanh các vùng này.

## Những thành phần có khả năng là graphic/texture

Các label lớn sau **không tìm thấy như chuỗi Shift-JIS bình thường** trong vùng text đã scan và cần theo nhánh graphic patch:

- `ストーリーモード` — Story Mode
- `対戦モード` — Versus Mode
- `武器スキルリスト` — Weapon Skill List
- `オプション` — Option
- `キャラクターセレクト` — Character Select title

Không được tuyên bố 100% là texture cho tới khi asset được xác định, nhưng hiện đây là giả thuyết mạnh nhất.

## Hai bài toán kỹ thuật còn lại

### 1. Repack / string table

Full-width Latin dùng 2 byte/ký tự, nên nhiều câu Việt không fit slot Nhật gốc. Hiện có **230 dòng pending** ở master 0.6.

Cần reverse/repack string table hoặc pointer table để:

- tăng không gian câu;
- tránh rút gọn quá mức;
- dùng câu Việt tự nhiên hơn.

### 2. Font tiếng Việt có dấu — ưu tiên tiếp theo

Người dùng đã đồng ý **test dấu ngay bước tiếp theo**, trước khi đổ thêm quá nhiều text không dấu.

Không nhét UTF-8 trực tiếp.

Hướng nghiên cứu:

- xác định renderer/glyph path;
- executable có wrapper/trampoline liên quan BIOS `B(51h) Krom2RawAdd`, là đầu mối cần trace;
- kiểm tra font atlas / custom glyph table nếu có;
- nếu renderer dùng BIOS Shift-JIS, nghiên cứu remap/inject glyph 2-byte cho tiếng Việt.

Visible font test mục tiêu phải nằm **ngay đầu game/menu**, ví dụ:

```text
TIẾNG VIỆT
Ă Â Ê Ô Ơ Ư Đ
Á À Ả Ã Ạ
Ắ Ằ Ẳ Ẵ Ặ
Ế Ề Ể Ễ Ệ
Ớ Ờ Ở Ỡ Ợ
Ứ Ừ Ử Ữ Ự
```

Nếu pass, chuyển pipeline từ fallback không dấu sang `vi_full` có dấu.

## Ưu tiên công việc kể từ đây

1. **Font/glyph tiếng Việt có dấu**, test visible ngay đầu game.
2. Dọn intro để không còn màn Nhật + Việt lẫn nhau.
3. Xác định và patch graphic/texture main menu + Character Select title.
4. Tiếp tục mở rộng full translation từ master.
5. Reverse/repack string table để đưa 230 dòng pending vào game.
6. Dump/phân loại tiếp `EVCARD.BDP`, `DUELDATA.BDP`, `PC_DATA.BDP`, `SCR_DATA.BDP`.
7. Cuối cùng phát hành patch, không phân phối BIN game.

## Quy tắc test

- Cold boot mỗi image.
- Không load save state từ image khác.
- Builder phải verify BIN SHA1 chuẩn.
- Mở đúng `.cue` mới sinh.
- Demo/test mới phải ưu tiên **text visible ngay đầu game**, không bắt tester vào sâu gameplay.

## Trạng thái handoff hiện tại

- Original: **OK**
- COPY_ONLY: **OK**
- BDP structure/checksum: **đã reverse và verify**
- Raw MODE2/Form1 + EDC/ECC: **OK**
- Full-width Latin Shift-JIS: **OK**
- ASCII 1-byte: **FAIL runtime / loại**
- Alpha 0.5.1: **runtime OK**
- Translation master: **596 vị trí**
- Alpha 0.6: **366 patch, local verify OK**
- Alpha 0.6.1 FRONT: **397 patch, runtime có Việt hóa nhưng còn nhiều Nhật + mixed fragments**
- Next milestone: **Vietnamese diacritics / custom glyph visible test**

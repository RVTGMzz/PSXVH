# Gaia Master — checksum BDP & visible menu test

## Kết quả xác nhận checksum

Diagnostic 0.1.9:

- A `FIX_A_CHECKSUM`: OK
- B `FIX_SLOT_CHECKSUM`: OK
- C `FIX_FIRST_CHECKSUM`: OK
- D `FULLWIDTH_BATDAU`: OK
- Không quan sát được chữ `BATDAU!!!` vì câu gốc không xuất hiện rõ trong flow test thực tế.

## Checksum nested BDP

Nested BDP có checksum 32-bit tại offset `+0x04`.

Công thức đã khớp chính xác với dữ liệu gốc:

```text
sum16 = sum(all bytes except checksum field +0x04..+0x07) & 0xFFFF
checksum = ((~sum16 & 0xFFFF) << 16) | sum16
```

Việc `BALANCED_SWAP` ở 0.1.8 chạy được cũng được giải thích bởi tổng byte không đổi nên checksum cũ vẫn hợp lệ.

Sau khi sửa text trong nested BDP, pipeline an toàn hiện tại là:

1. patch text;
2. tính lại checksum nested BDP;
3. ghi checksum mới;
4. regenerate PS1 MODE2/Form1 EDC/ECC cho các raw sector bị thay đổi;
5. xuất BIN/CUE mới;
6. cold boot DuckStation, không dùng save state cũ.

## Visible Menu Test 0.2.0

Để không phải săn câu text xuất hiện chớp nhoáng, test kế tiếp chuyển sang pre-game UI / character select trong top-level PRGPACK entry 29, nested BDP bắt đầu tại `0xBF7AC`, length `123628` bytes.

Ba chuỗi được patch bằng Latin full-width cùng độ dài byte:

- `この設定でいいかしら？` -> `ＴＥＳＴ　ＶＩＥＴ！！`
- `キャラクターをえらんでね` -> `ＶＩＥＴＨＯＡＴＥＳＴ！`
- `○ボタンをおしてね！` -> `ＶＩＥＴＴＥＳＴ！！`

Các chuỗi này nằm ở màn setup / chọn nhân vật trước gameplay nên dễ quan sát hơn nhiều.

Nếu nhìn thấy các dòng Latin full-width này trong game, có thể kết luận renderer của vùng UI này hỗ trợ glyph Latin full-width và bắt đầu prototype Việt hóa menu/UI không dấu trước khi cấy font tiếng Việt có dấu.

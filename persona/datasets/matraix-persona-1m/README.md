# matraix-persona-1m — tải xong, chưa đọc được bằng code trong nhánh này

`release/` chứa bản phát hành công khai đã tải đầy đủ (6,4 GB, 999.847 persona).
Dữ liệu **không hỏng**. Playground đếm được `1,000,000` vì nó chỉ đọc
`manifest.json`, nhưng khi giải mã persona thật thì báo:

```
Expected 1292 columns, found 1290
```

Thông báo đó gây hiểu nhầm: nó nghe như lệch 2 chiều, trong khi thực tế **bố cục
nhị phân cũng đã khác**.

## Hai định dạng lệch nhau ở đâu

|                  | Bản phát hành công khai | Nhánh này |
|------------------|------------------------:|----------:|
| Số chiều         | 1290 | 1292 |
| Đóng gói         | 2 mã 4-bit mỗi byte | 1 byte mỗi thuộc tính |
| `attributes`     | `fixed_size_binary[645]` | 1292 byte |
| `format_version` | 1 | 1 |

Đọc dữ liệu 645 byte bằng bố cục 1292 byte thì lệch toàn bộ, không phải chỉ mất
hai chiều cuối.

## Vì sao lệch

Ở commit gốc `955149e`, repo khớp hoàn toàn bản phát hành
(`ATTRIBUTE_COUNT = 1290`, `ATTRIBUTE_BYTES = (COUNT + 1) // 2 = 645`).

Nhánh `dokhiem2k4/vita-multiturn-pipeline` mang theo hai commit đổi định dạng:

- `6bb171a` — thêm chiều tiếng Việt và sổ địa chỉ VN (1290 → 1291)
- `0c3e657` — đổi sang một byte mỗi thuộc tính thay vì hai mã 4-bit

Cả hai **không nâng `format_version`**, nên không có gì cảnh báo khi đọc dữ liệu
cũ. Đây cũng là gốc của hai test hỏng sẵn kể từ lúc merge:

- `tests/unit/playground_core/test_persona_generator.py::test_checked_in_sample_manifest_is_consistent`
- `tests/unit/matraix/test_dimension_label_packs.py::test_committed_packs_are_valid_and_fresh`

## Muốn dùng bộ này thì làm gì

Ba đường, chưa đường nào được làm:

1. **Cho bộ đọc lấy số chiều và bề rộng byte từ chính bộ dữ liệu**
   (`release/persona_codes.schema.json` + kiểu parquet) thay vì hằng số toàn cục
   trong `persona/post_process/unified_dataset/schema.py`. Sửa đúng gốc; đụng cả
   `application/playground/backend/service/persona_1m_index.py`.
2. Xin bản phát hành mới mã hoá theo 1292 chiều / 1 byte.
3. Dùng pool khác. `vn-drivers-forum` (42 tài xế Việt) hợp hơn cho các task Vita
   hiện tại, vốn chỉ chạy 1–3 persona mỗi lượt.

Dù chọn đường nào, nên **nâng `format_version`** khi bố cục nhị phân đổi. Nếu
`0c3e657` đã làm vậy thì lỗi này sẽ hiện ra thành "phiên bản không tương thích"
ngay từ đầu, thay vì một thông báo lệch số cột dễ hiểu sai.

`release/` bị `.gitignore` chặn (dòng 271). File README này thì không, để ghi chú
còn lại kể cả khi ai đó xoá phần dữ liệu.

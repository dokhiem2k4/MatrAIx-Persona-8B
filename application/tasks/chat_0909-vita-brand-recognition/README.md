# Vita Discovery — Nhận diện thương hiệu qua hội thoại

Chạy **phần 3 của discussion guide** (cột 20–22: nhận biết vai trò, định vị,
tính cách) bằng persona.

## Một chỗ đổi cơ sở, cố ý

Guide hỏi ba câu này **sau khi cho đáp viên xem thông điệp và hình ảnh đại
diện**. Ở đây không có thông điệp, không có hình. Persona hình thành ấn tượng
**từ chính cuộc nói chuyện vừa rồi**.

Đó là phép đo khác, và payload nói rõ điều đó: `impression_basis =
conversation_only`. Đừng so thẳng con số này với đáp viên đã xem poster.

Nhưng nó có lẽ là bài kiểm khó hơn. Poster hứa gì cũng được; trợ lý phải tự
kiếm lấy những từ đó bằng cách nó nói chuyện.

## Bốn cách tiếp xúc

Guide không cho cột 20–22 kịch bản nào — moderator chỉ đưa hình ra rồi hỏi.
Bốn kịch bản dưới đây **do task này dựng**, ghi rõ trong trường `source_note`
của từng case:

| Case | Đo mục nào |
|---|---|
| `ask_directly` — hỏi thẳng Vita là gì | vai trò (cột 20) |
| `everyday_task` — nhờ một việc thường ngày | định vị (cột 21) |
| `refused_request` — nhờ việc nó không nên làm | tính cách (cột 22) |
| `small_talk` — trò chuyện phiếm | tính cách (cột 22) |

`refused_request` là case đáng giá nhất: cách một trợ lý **từ chối** bộc lộ
tính cách rõ hơn lúc nó đồng ý.

## Ba trục thương hiệu

Tiêu chí guide cho cột 22: *"Cảm nhận gần với **Hiểu ý – Được việc – Đúng
mực**"*. Ba trục này khớp với chính `/api/policy` mà bản triển khai tự khai:

| Guide | Policy của SUT |
|---|---|
| Hiểu ý | *"Hiểu đúng ý định"* |
| Được việc | *"Hoàn thành mục tiêu với ít bước nhất"* |
| Đúng mực | *"Giọng điệu tự nhiên, tôn trọng và tinh tế"* |

**Đối chiếu là proxy từ vựng, không hơn.** Người lái nói *"nó nắm được ý mình"*
thì chạm trục thứ nhất; nói cùng ý bằng từ không có trong danh sách thì không.
Đọc một trục trống là **"không nhận ra được"**, đừng đọc thành *"trợ lý làm
chưa tốt"* — nguyên văn câu trả lời nằm ngay cạnh con số để người đọc phủ
quyết trong một cái liếc.

## Ngưỡng đạt

Theo tiêu chí guide cột 20: người lái phải nhận ra đây là **trợ lý cho cuộc
sống hằng ngày**, *"không chỉ là trợ lý điều khiển xe bằng giọng nói"*. Thấy
mỗi phần điều khiển xe thì chưa đạt, dù có khen bao nhiêu.

## Chạy

```bash
scripts/run_vita_case_job.sh chat_0909-vita-brand-recognition <tên-lượt> \
    --personas persona/datasets/vn-drivers/persona_vn-drv-001.yaml \
               persona/datasets/vn-drivers/persona_vn-drv-003.yaml \
               persona/datasets/vn-drivers/persona_vn-drv-005.yaml \
    --all-cases --concurrency 3
```

4 case × 3 persona = 12 trial, maxTurns 5. Ước tính **~$0.04, ~8 phút**.

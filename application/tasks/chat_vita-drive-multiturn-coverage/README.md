# chat_vita-drive-multiturn-coverage

Đảm bảo **phủ đủ 46 sub_intent** trong hội thoại nhiều lượt, thay vì phó mặc
persona tự nghĩ chủ đề như `chat_vita-drive-assistant` đang làm.

**Trial = 1 persona × 1 conversation seed.** 46 seed. `maxTurns: 6`.

## Chỉ lấy lượt user đầu tiên

`input/cases.jsonl` **cố ý không chứa lượt assistant nào** của dataset gốc. Nếu
persona đọc được câu trả lời mẫu, nó sẽ lái hội thoại theo đúng transcript và
phép đo mất hết ý nghĩa. `reference_turn_count` chỉ là mốc tham chiếu, không
phải chuẩn đúng/sai.

## Chất lượng dữ liệu — đọc trước khi tin số liệu

Bộ này **nhiễu**. Nhiều seed là mảnh vụn nhận dạng giọng nói, hoặc nằm dưới một
`sub_intent` mà nội dung không khớp. Vài ví dụ có thật:

| sub_intent | seed |
|---|---|
| `calendar_query` | `gì` |
| `source_queue` | `usb` |
| `calling` | `đây là dấu hiệu của của bệnh gì` |
| `parking_arrival` | `bạn đã đến nơi` (thông báo dẫn đường, không phải lời người lái) |

Luật chỉ bắt được `seed_quality = too_short` (6/46). **Gán sai nhãn thì luật
không bắt được** — phải người đọc. `seed_review.md` liệt kê đủ 46 seed kèm cột
Duyệt để review tay.

Facet `seed_quality` đi vào báo cáo để tách nhiễu đầu vào khỏi lỗi của mô hình.

## `lexical_topic_overlap` là proxy, không phải điểm

Nó chỉ hỏi một lượt trả lời sau có dùng lại từ nội dung persona nêu ở câu mở đầu
không. Mô hình có thể giữ ngữ cảnh hoàn hảo mà diễn đạt lại toàn bộ, hoặc lặp từ
mà mất mạch. Đọc như tín hiệu khói rẻ tiền, đừng đọc như điểm số.

Nguồn dataset nằm ngoài repo và không được commit.

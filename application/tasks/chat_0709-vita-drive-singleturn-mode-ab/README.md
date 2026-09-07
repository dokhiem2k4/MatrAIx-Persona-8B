# chat_0709-vita-drive-singleturn-mode-ab

Đo ảnh hưởng của **chế độ trợ lý × trạng thái xe** lên trải nghiệm người dùng,
trên bộ Vita Demo 276 case.

Lưới giai thừa **cân bằng tuyệt đối**: 46 subintent × `vehicle_state`
(driving/parking) × `ASSISTANT_MODE` (quiet/balance/proactive) = 276, mỗi ô
đúng 46 case. So sánh giữa các ô hợp lệ mà không cần cân lại trọng số.

**Trial = 1 persona × 1 case.** Hai yếu tố thí nghiệm bơm vào request qua
`sessionBody`.

## Không có ground truth

Bộ này **không có cột expected nào**. Verifier ở đây không chấm đúng/sai — nó
ghi lại hai yếu tố thí nghiệm, vài phép đo tất định trên phản hồi, và đánh giá
của chính persona.

Phép đo tất định đáng giá nhất là `reply_char_count`: câu hỏi "chế độ proactive
có làm phiền người đang lái không" trả lời được một phần bằng việc trợ lý nói
bao nhiêu khi `vehicle_state = driving`.

## Giới hạn phải ghi vào báo cáo

Toàn bộ 276 prompt có `source = generated` và `note` rỗng — **máy sinh, chưa qua
review người**. Facet `prompt_source` mang thông tin này để báo cáo nói được rõ.
Kết luận rút ra chỉ nói về hành vi của Vita trước prompt sinh máy, không đại diện
cho người dùng thật.

Nguồn dataset nằm ngoài repo và không được commit.

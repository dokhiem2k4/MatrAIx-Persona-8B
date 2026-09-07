# chat_0709-vita-drive-singleturn-mode-ab

Đo ảnh hưởng của **chế độ trợ lý × trạng thái xe** lên trải nghiệm người dùng,
trên bộ Vita Demo 276 case.

Lưới giai thừa **cân bằng tuyệt đối**: 92 tổ hợp (46 subintent × `vehicle_state`
driving/parking) × **7 profile thật của trợ lý** = 644, mỗi ô đúng 46 case.
So sánh giữa các ô hợp lệ mà không cần cân lại trọng số.

## Vì sao không dùng ASSISTANT_MODE của workbook

Workbook có cột `ASSISTANT_MODE` với ba giá trị `quiet` / `balance` / `proactive`.
**Bản triển khai không có ba chế độ đó.** `GET /api/assistant/profiles` cho thấy
trục tính cách thật là `assistantProfileId` với bảy giá trị: `normal` (mặc định),
`sweet`, `chao`, `cheeky`, `bright`, `rustic`, `calm`.

Giữ nguyên cột cũ thì cả ba ô sẽ cho kết quả giống hệt nhau — đo một yếu tố hệ
thống không có. Nên lưới được dựng lại: prompt của workbook là **kích thích**,
profile là **yếu tố cần đo**. Chỉ số prompt được xoay theo chỉ số tổ hợp để một
profile không luôn đi kèm cùng một câu chữ, tránh nhập nhằng giữa cách diễn đạt
và tính cách.

## Chưa kiểm chứng: profile có được áp dụng không

`POST /api/chat` nhận `{message, drivingContext, intent}`. Nhưng trong bundle
của web, profile được đặt qua **một lời gọi riêng**:
`POST /api/persona/session {sessionId, assistantProfileId}`.

Task gửi `assistantProfileId` kèm mỗi tin nhắn qua `sessionBody`. **Chưa xác
minh được máy chủ có đọc nó ở đó không.** Nếu không, mọi ô lưới sẽ giống nhau
đúng như vấn đề mà thay đổi này định sửa. Xác minh cần đúng một lời gọi thật
`/api/chat` — chưa làm.

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

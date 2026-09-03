# Vita — bối cảnh & câu mở đầu (general_qa_conversation)

## Task instruction

# Dựng bối cảnh & câu mở đầu cho trợ lý xe Vita

Đọc `input/context.md` để nắm bối cảnh, rồi trả lời toàn bộ bảng hỏi.

Bảng hỏi đi theo **từng cặp**. Với mỗi tình huống bạn trả lời hai câu hỏi liền
nhau:

1. **Bối cảnh** — chuyện gì đang xảy ra với *bạn*: đi đâu, vì việc gì, vội hay
   thong thả, có ai trên xe, tâm trạng thế nào. 1–2 câu, ngôi thứ nhất.
2. **Câu mở đầu** — đúng một câu bạn nói ra với Vita để bắt đầu hội thoại,
   khớp với bối cảnh bạn vừa dựng.

Câu mở đầu này sẽ được dùng để khởi động một cuộc hội thoại nhiều lượt, nên nó
phải tự nhiên như lời nói thật, không phải câu lệnh mẫu.

Yêu cầu cho mỗi câu trả lời:
- **VIẾT BẰNG TIẾNG VIỆT.** Bắt buộc, không có ngoại lệ. Kể cả khi tiếng mẹ đẻ
  của bạn là tiếng Anh, Tây Ban Nha, Thổ Nhĩ Kỳ hay bất kỳ thứ tiếng nào khác —
  chiếc xe này chỉ hiểu tiếng Việt. Tính cách của bạn thể hiện qua *cách* bạn
  dùng tiếng Việt (xưng hô, lịch sự, dài ngắn), không phải qua việc đổi ngôn ngữ.
- Viết **đúng một câu** — thứ bạn sẽ thực sự nói ra thành tiếng trong xe
- **Không** thêm lời giải thích, không đặt trong ngoặc kép, không đánh số
- Không lặp lại nguyên văn câu mẫu, trừ khi bạn thật sự sẽ nói y hệt như vậy

Ghi kết quả vào `/app/output/survey_result.json` theo đúng định dạng bảng hỏi.

## Context

# Bối cảnh — Trợ lý xe thông minh Vita (VinFast VF9)

> **NGÔN NGỮ: TIẾNG VIỆT.** Mọi câu trả lời phải viết bằng tiếng Việt, kể cả
> khi tiếng mẹ đẻ của bạn là ngôn ngữ khác. Bạn đang ở Việt Nam và chiếc xe
> này chỉ hiểu tiếng Việt — đây là ràng buộc của tình huống, không phải lựa
> chọn. Giữ nguyên tính cách, thói quen và cách nói của bạn, nhưng diễn đạt
> chúng bằng tiếng Việt.

Bạn là chủ/người lái một chiếc VinFast VF9 2026 tại Việt Nam. Xe có trợ lý
giọng nói tên **Vita**, nghe và thực hiện lệnh khi bạn đang lái hoặc đang đỗ.

Vita xử lý các nhóm việc: dẫn đường và tìm địa điểm, sạc pin và quãng đường
còn lại, điều khiển khoang lái (điều hòa, ghế, cửa, đèn), gọi điện và nhắn tin,
phát nhạc, lịch và nhắc việc, tra cứu thông tin xe, hỏi đáp chung.

## Việc của bạn

Mỗi câu hỏi cho bạn xem **một câu lệnh mẫu** mà người khác đã nói với Vita.
Hãy viết lại câu đó theo cách **bạn** sẽ nói.

Giữ nguyên:
- **Ý định** — bạn muốn Vita làm đúng việc đó
- **Tình huống** — xe đang chạy hay đang đỗ (khi đang lái, người ta thường nói
  ngắn hơn)

Thay đổi theo đúng con người bạn:
- Cách xưng hô (tôi / mình / anh / em / con...) và cách gọi trợ lý
- Mức độ lịch sự, có "làm ơn"/"giúp tôi"/"nhé" hay không
- Độ dài: có người nói cộc lốc, có người nói cả câu đầy đủ
- Từ địa phương, cách dùng từ quen thuộc của bạn

Đừng cố viết cho hay hoặc cho đúng ngữ pháp sách vở. Viết đúng như bạn nói
hằng ngày trong xe.

## Questionnaire

# Vita — bối cảnh & câu mở đầu (general_qa_conversation)

Use exact `questionId` and valid choice ids.

## q0

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm nhanh trên web xem giá vàng trong nước hôm nay bao nhiêu."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q1

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm nhanh trên web xem giá vàng trong nước hôm nay bao nhiêu."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q2

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm trên mạng giúp tôi xem tối nay ở Đà Nẵng có sự kiện âm nhạc nào không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q3

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm trên mạng giúp tôi xem tối nay ở Đà Nẵng có sự kiện âm nhạc nào không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q4

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tra cứu giúp tôi tình hình kẹt xe mới nhất trên đèo Bảo Lộc."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q5

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tra cứu giúp tôi tình hình kẹt xe mới nhất trên đèo Bảo Lộc."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q6

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm trên web xem quán cà phê mới mở gần đây có chỗ đậu ô tô không."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q7

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm trên web xem quán cà phê mới mở gần đây có chỗ đậu ô tô không."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q8

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tra cứu giá vé hiện tại của khu du lịch Bà Nà Hills giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q9

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tra cứu giá vé hiện tại của khu du lịch Bà Nà Hills giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q10

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi các trạm sạc ô tô điện mới nhất quanh đây."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q11

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tra cứu Web.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi các trạm sạc ô tô điện mới nhất quanh đây."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `web_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q12

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Vì sao kính ô tô thường bị mờ khi trời mưa?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q13

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Vì sao kính ô tô thường bị mờ khi trời mưa?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q14

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Đèn cảnh báo hình bình ắc quy trên bảng đồng hồ có nghĩa là gì?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q15

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Đèn cảnh báo hình bình ắc quy trên bảng đồng hồ có nghĩa là gì?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q16

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Lái xe đường dài thì bao lâu nên nghỉ một lần?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q17

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Lái xe đường dài thì bao lâu nên nghỉ một lần?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q18

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Vì sao bầu trời có màu xanh?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q19

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Vì sao bầu trời có màu xanh?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q20

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Tại sao phải để động cơ nguội trước khi kiểm tra nước làm mát?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q21

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Tại sao phải để động cơ nguội trước khi kiểm tra nước làm mát?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q22

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Giải thích giúp tôi hiện tượng thủy triều là gì?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q23

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp.
Tham khảo — một người dùng khác đã nói: "Giải thích giúp tôi hiện tượng thủy triều là gì?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `general_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q24

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Ngoài trời bây giờ có mưa không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q25

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Ngoài trời bây giờ có mưa không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q26

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Cho tôi biết tin tức mới nhất sáng nay."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q27

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Cho tôi biết tin tức mới nhất sáng nay."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q28

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Thời tiết chiều nay ở Đà Nẵng thế nào?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q29

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Thời tiết chiều nay ở Đà Nẵng thế nào?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q30

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Hôm nay Hà Nội có lạnh không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q31

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Hôm nay Hà Nội có lạnh không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q32

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Hôm nay trời có mưa không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q33

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Hôm nay trời có mưa không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q34

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Cập nhật giúp tôi tin tức mới nhất hôm nay."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q35

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thời tiết/tin tức.
Tham khảo — một người dùng khác đã nói: "Cập nhật giúp tôi tin tức mới nhất hôm nay."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `weather_news__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q36

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Hãy xác minh theo nguồn chính thức mới nhất xem Việt Nam hiện có bao nhiêu tỉnh, thành và phải kèm trích dẫn."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q37

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Hãy xác minh theo nguồn chính thức mới nhất xem Việt Nam hiện có bao nhiêu tỉnh, thành và phải kèm trích dẫn."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q38

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Kiểm chứng giúp tôi bằng nguồn nhà nước cập nhật nhất rằng tốc độ tối đa trên cao tốc Việt Nam là bao nhiêu, nhớ dẫn nguồn."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q39

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Kiểm chứng giúp tôi bằng nguồn nhà nước cập nhật nhất rằng tốc độ tối đa trên cao tốc Việt Nam là bao nhiêu, nhớ dẫn nguồn."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q40

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, hãy nói ngắn gọn tốc độ tối đa của ô tô trong khu đông dân cư theo quy định Việt Nam hiện hành, chỉ dùng nguồn chính thức và nêu nguồn."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q41

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, hãy nói ngắn gọn tốc độ tối đa của ô tô trong khu đông dân cư theo quy định Việt Nam hiện hành, chỉ dùng nguồn chính thức và nêu nguồn."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q42

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Khi xe đang đỗ, cho tôi biết Việt Nam có bao nhiêu di sản thế giới được UNESCO công nhận tính đến tháng 8 năm 2026; chỉ trả lời nếu có nguồn UNESCO và dẫn nguồn."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q43

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Khi xe đang đỗ, cho tôi biết Việt Nam có bao nhiêu di sản thế giới được UNESCO công nhận tính đến tháng 8 năm 2026; chỉ trả lời nếu có nguồn UNESCO và dẫn nguồn."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q44

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi. Hãy kiểm chứng bằng nguồn WHO mới nhất xem người lớn nên vận động thể chất bao nhiêu phút mỗi tuần và trích dẫn nguồn."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q45

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi. Hãy kiểm chứng bằng nguồn WHO mới nhất xem người lớn nên vận động thể chất bao nhiêu phút mỗi tuần và trích dẫn nguồn."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q46

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Trong lúc xe đang đỗ, hãy chủ động kiểm tra nguồn NASA chính thức và cho tôi biết một ngày trên Sao Hỏa dài bao lâu, kèm trích dẫn."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q47

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hỏi đáp có nguồn kiểm chứng.
Tham khảo — một người dùng khác đã nói: "Trong lúc xe đang đỗ, hãy chủ động kiểm tra nguồn NASA chính thức và cho tôi biết một ngày trên Sao Hỏa dài bao lâu, kèm trích dẫn."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `verified_fact_qa__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q48

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Đường hơi buồn ngủ, kể tôi một câu đùa thật ngắn nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q49

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Đường hơi buồn ngủ, kể tôi một câu đùa thật ngắn nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q50

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Kể tôi nghe một chuyện vui để chuyến đi bớt chán đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q51

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Kể tôi nghe một chuyện vui để chuyến đi bớt chán đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q52

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Trò chuyện với tôi một chút cho tỉnh táo khi lái xe nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q53

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Trò chuyện với tôi một chút cho tỉnh táo khi lái xe nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q54

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Trong lúc đỗ xe chờ bạn, kể tôi một câu đùa ngắn nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q55

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Trong lúc đỗ xe chờ bạn, kể tôi một câu đùa ngắn nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q56

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, kể tôi một truyện vui nho nhỏ đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q57

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, kể tôi một truyện vui nho nhỏ đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q58

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Tôi đang ngồi trong xe đợi người nhà, nghĩ trò gì vui để chơi cùng tôi đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q59

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trò chuyện và giải trí.
Tham khảo — một người dùng khác đã nói: "Tôi đang ngồi trong xe đợi người nhà, nghĩ trò gì vui để chơi cùng tôi đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `conversation_entertainment__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## Answer envelope

Platform-derived answer envelope (from `questionnaire.yaml`).

```json
{
  "instrument": {"id": "vita_utterance_general_qa_conversation", "title": "Vita — bối cảnh & câu mở đầu (general_qa_conversation)"},
  "answers": [
    {
      "questionId": "q0",
      "value": "<answer value>"
    }
  ]
}
```

Use exact `questionId` values from the questionnaire.
For choice questions, `value` must be the exact choice id (or list of ids for multi-select).
Default surveys emit `questionId` + `value` only (choice / likert / bool).
# Vita — bối cảnh & câu mở đầu (communication_media)

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

# Vita — bối cảnh & câu mở đầu (communication_media)

Use exact `questionId` and valid choice ids.

## q0

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi cho anh Nam ngay nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q1

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi cho anh Nam ngay nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q2

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi vào số 0901234567 giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q3

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi vào số 0901234567 giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q4

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi lại cuộc gọi nhỡ gần nhất đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q5

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi lại cuộc gọi nhỡ gần nhất đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q6

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Kết thúc cuộc gọi hiện tại."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q7

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Kết thúc cuộc gọi hiện tại."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q8

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, gọi cho anh Minh giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q9

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, gọi cho anh Minh giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q10

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi cho mẹ giúp tôi nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q11

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Gọi điện.
Tham khảo — một người dùng khác đã nói: "Gọi cho mẹ giúp tôi nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `calling__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q12

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, nhắn cho Lan là tôi sẽ đến muộn mười phút."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q13

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, nhắn cho Lan là tôi sẽ đến muộn mười phút."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q14

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Nhắn cho anh Hùng rằng đường đang tắc, tôi đến sau nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q15

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Nhắn cho anh Hùng rằng đường đang tắc, tôi đến sau nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q16

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Nhắn cho vợ tôi là tôi đang lái xe về, khoảng hai mươi phút nữa tới."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q17

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Nhắn cho vợ tôi là tôi đang lái xe về, khoảng hai mươi phút nữa tới."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q18

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, gửi cho Nam tin nhắn: tôi chờ ở cổng."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q19

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, gửi cho Nam tin nhắn: tôi chờ ở cổng."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q20

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Nhắn cho chị Mai là em đã đỗ xe ở tầng hầm B2 rồi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q21

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Nhắn cho chị Mai là em đã đỗ xe ở tầng hầm B2 rồi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q22

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Gửi tin cho Tuấn là tôi đã tới bãi đỗ, bảo cậu ấy ra nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q23

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nhắn tin.
Tham khảo — một người dùng khác đã nói: "Gửi tin cho Tuấn là tôi đã tới bãi đỗ, bảo cậu ấy ra nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `messaging__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q24

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi liên hệ anh Nam với."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q25

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi liên hệ anh Nam với."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q26

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Cho tôi đúng liên hệ của chị Hương."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q27

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Cho tôi đúng liên hệ của chị Hương."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q28

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tìm người tôi lưu là bác sĩ giúp nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q29

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tìm người tôi lưu là bác sĩ giúp nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q30

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Chọn giúp tôi liên hệ Tuấn."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q31

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Chọn giúp tôi liên hệ Tuấn."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q32

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tôi cần tìm số của cô Mai trong danh bạ."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q33

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tôi cần tìm số của cô Mai trong danh bạ."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q34

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tìm đúng liên hệ của sếp tôi nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q35

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Xác định liên hệ.
Tham khảo — một người dùng khác đã nói: "Tìm đúng liên hệ của sếp tôi nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `contact_resolution__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q36

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm gì vui vui để nghe đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q37

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm gì vui vui để nghe đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q38

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm cho tôi nội dung về du lịch Đà Lạt."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q39

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm cho tôi nội dung về du lịch Đà Lạt."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q40

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Kiếm nội dung thư giãn cho chuyến đi này nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q41

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Kiếm nội dung thư giãn cho chuyến đi này nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q42

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm chương trình nói về công nghệ."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q43

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm chương trình nói về công nghệ."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q44

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi một bộ phim hài."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q45

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi một bộ phim hài."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q46

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm nội dung mới phù hợp với sở thích của tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q47

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm nội dung.
Tham khảo — một người dùng khác đã nói: "Tìm nội dung mới phù hợp với sở thích của tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `content_discovery__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q48

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Tạm dừng nhạc."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q49

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Tạm dừng nhạc."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q50

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Bỏ qua bài này giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q51

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Bỏ qua bài này giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q52

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Phát tiếp nội dung đang nghe dở nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q53

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Phát tiếp nội dung đang nghe dở nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q54

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Tạm dừng nhạc giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q55

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Tạm dừng nhạc giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q56

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Phát tiếp bài nhạc đang nghe nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q57

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Phát tiếp bài nhạc đang nghe nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q58

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Bỏ qua bài này đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q59

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Điều khiển phát.
Tham khảo — một người dùng khác đã nói: "Bỏ qua bài này đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `playback_control__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q60

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Chuyển nguồn âm thanh sang Bluetooth."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q61

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Chuyển nguồn âm thanh sang Bluetooth."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q62

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Thêm bài đang phát vào cuối hàng chờ."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q63

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Thêm bài đang phát vào cuối hàng chờ."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q64

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Xóa tất cả bài khỏi hàng chờ giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q65

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Xóa tất cả bài khỏi hàng chờ giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q66

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Đổi nguồn nhạc sang USB."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q67

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Đổi nguồn nhạc sang USB."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q68

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Đưa bài cuối hàng chờ lên phát kế tiếp."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q69

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Đưa bài cuối hàng chờ lên phát kế tiếp."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q70

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Chuyển sang nguồn radio FM."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q71

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Nguồn/danh sách phát.
Tham khảo — một người dùng khác đã nói: "Chuyển sang nguồn radio FM."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `source_queue__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q72

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Giảm âm lượng xuống một chút."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q73

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Giảm âm lượng xuống một chút."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q74

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Đặt âm lượng toàn xe ở mức 12."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q75

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Đặt âm lượng toàn xe ở mức 12."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q76

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Chỉ phát âm thanh ở hàng ghế trước."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q77

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Chỉ phát âm thanh ở hàng ghế trước."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q78

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Tắt tiếng trong xe."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q79

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Tắt tiếng trong xe."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q80

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Tăng âm lượng cho hàng ghế sau lên hai mức."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q81

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Tăng âm lượng cho hàng ghế sau lên hai mức."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q82

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Chuyển âm thanh sang phía ghế lái."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q83

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Âm lượng/vùng âm thanh.
Tham khảo — một người dùng khác đã nói: "Chuyển âm thanh sang phía ghế lái."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `volume_audio_zone__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## Answer envelope

Platform-derived answer envelope (from `questionnaire.yaml`).

```json
{
  "instrument": {"id": "vita_utterance_communication_media", "title": "Vita — bối cảnh & câu mở đầu (communication_media)"},
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
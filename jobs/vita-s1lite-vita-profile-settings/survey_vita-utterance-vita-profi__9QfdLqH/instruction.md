# Vita — bối cảnh & câu mở đầu (vita_profile_settings)

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

# Vita — bối cảnh & câu mở đầu (vita_profile_settings)

Use exact `questionId` and valid choice ids.

## q0

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa ơi, khi đang lái xe thì tôi có thể nhờ bạn làm những gì?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q1

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa ơi, khi đang lái xe thì tôi có thể nhờ bạn làm những gì?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q2

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Tôi gọi và sử dụng ViTa khi đang lái xe như thế nào?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q3

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Tôi gọi và sử dụng ViTa khi đang lái xe như thế nào?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q4

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa có thể hỗ trợ những gì trên đường đi?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q5

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa có thể hỗ trợ những gì trên đường đi?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q6

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, cho tôi biết nhanh ViTa dùng được vào những việc gì?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q7

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, cho tôi biết nhanh ViTa dùng được vào những việc gì?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q8

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Muốn bắt đầu nói chuyện với ViTa thì tôi cần làm gì?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q9

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Muốn bắt đầu nói chuyện với ViTa thì tôi cần làm gì?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q10

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Lúc xe đang đỗ, ViTa có thể chủ động giúp tôi những gì?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q11

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Khả năng và cách sử dụng ViTa.
Tham khảo — một người dùng khác đã nói: "Lúc xe đang đỗ, ViTa có thể chủ động giúp tôi những gì?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_capabilities_usage__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q12

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa ơi, từ giờ trả lời tôi ngắn gọn hơn nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q13

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa ơi, từ giờ trả lời tôi ngắn gọn hơn nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q14

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa, đổi cách trả lời sang ngắn gọn hơn để tôi dễ nghe khi đang lái xe."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q15

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "ViTa, đổi cách trả lời sang ngắn gọn hơn để tôi dễ nghe khi đang lái xe."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q16

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Từ giờ hãy chủ động nhắc tôi bằng giọng nữ khi đang lái xe nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q17

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Từ giờ hãy chủ động nhắc tôi bằng giọng nữ khi đang lái xe nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q18

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, đổi ViTa sang giọng nam và chỉ phản hồi thật khẽ thôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q19

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, đổi ViTa sang giọng nam và chỉ phản hồi thật khẽ thôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q20

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Đổi ngôn ngữ giao tiếp của ViTa sang tiếng Anh giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q21

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Đổi ngôn ngữ giao tiếp của ViTa sang tiếng Anh giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q22

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Khi xe đang đỗ, ViTa hãy chủ động giải thích chi tiết hơn cho tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q23

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tùy chọn tương tác với ViTa.
Tham khảo — một người dùng khác đã nói: "Khi xe đang đỗ, ViTa hãy chủ động giải thích chi tiết hơn cho tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `vita_preferences__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q24

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, chuyển sang hồ sơ Minh và xác nhận thật ngắn thôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q25

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, chuyển sang hồ sơ Minh và xác nhận thật ngắn thôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q26

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Đồng bộ các tùy chọn cá nhân trên tài khoản của tôi vào hồ sơ xe này."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q27

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Đồng bộ các tùy chọn cá nhân trên tài khoản của tôi vào hồ sơ xe này."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q28

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Hãy tạo hồ sơ tài xế tên Lan và chủ động áp dụng các thiết lập quen dùng của tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q29

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Hãy tạo hồ sơ tài xế tên Lan và chủ động áp dụng các thiết lập quen dùng của tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q30

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, chuyển sang hồ sơ của tôi nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q31

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, chuyển sang hồ sơ của tôi nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q32

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Tạo cho tôi một hồ sơ mới tên Minh khi xe đang đỗ."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q33

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Tạo cho tôi một hồ sơ mới tên Minh khi xe đang đỗ."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q34

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, đồng bộ các tùy chọn cá nhân của tôi vào hồ sơ hiện tại nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q35

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Hồ sơ và tài khoản người dùng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, đồng bộ các tùy chọn cá nhân của tôi vào hồ sơ hiện tại nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `user_profile_account__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q36

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Ngắt kết nối Bluetooth với điện thoại của tôi đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q37

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Ngắt kết nối Bluetooth với điện thoại của tôi đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q38

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Kết nối lại Bluetooth với điện thoại đã dùng gần nhất giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q39

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Kết nối lại Bluetooth với điện thoại đã dùng gần nhất giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q40

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Wi-Fi trên xe vừa mất kết nối, nối lại mạng đã lưu giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q41

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Wi-Fi trên xe vừa mất kết nối, nối lại mạng đã lưu giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q42

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, bật chế độ ghép nối Bluetooth nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q43

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, bật chế độ ghép nối Bluetooth nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q44

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Ghép nối điện thoại tên Galaxy S25 với xe giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q45

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Ghép nối điện thoại tên Galaxy S25 với xe giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q46

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, liên kết dịch vụ nghe nhạc trên điện thoại với hệ thống xe nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q47

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Kết nối thiết bị và dịch vụ.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, liên kết dịch vụ nghe nhạc trên điện thoại với hệ thống xe nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `device_service_connectivity__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q48

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Tắt thông báo bật lên của ứng dụng tin nhắn đi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q49

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Tắt thông báo bật lên của ứng dụng tin nhắn đi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q50

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Đổi ngôn ngữ giao diện hệ thống sang tiếng Việt giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q51

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Đổi ngôn ngữ giao diện hệ thống sang tiếng Việt giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q52

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Bật chế độ tối tự động cho giao diện từ lúc hoàng hôn nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q53

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Bật chế độ tối tự động cho giao diện từ lúc hoàng hôn nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q54

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, tắt âm thanh khi chạm trên màn hình nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q55

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, tắt âm thanh khi chạm trên màn hình nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q56

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Đặt ứng dụng bản đồ mặc định thành ứng dụng Bản đồ của xe."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q57

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Đặt ứng dụng bản đồ mặc định thành ứng dụng Bản đồ của xe."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q58

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, bật tự động cập nhật ứng dụng qua Wi-Fi nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q59

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Cài đặt hệ thống và ứng dụng.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ, bật tự động cập nhật ứng dụng qua Wi-Fi nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `system_app_settings__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q60

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, hãy tắt quyền truy cập vị trí của trợ lý."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q61

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Tôi đang lái xe, hãy tắt quyền truy cập vị trí của trợ lý."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q62

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Hãy xóa lịch sử lệnh thoại của tôi trong hôm nay."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q63

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Hãy xóa lịch sử lệnh thoại của tôi trong hôm nay."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q64

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Tắt việc lưu lịch sử hành trình và cho tôi biết khi đã xong."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q65

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Tắt việc lưu lịch sử hành trình và cho tôi biết khi đã xong."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q66

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, hãy thu hồi quyền dùng micro của ứng dụng thời tiết."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q67

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ rồi, hãy thu hồi quyền dùng micro của ứng dụng thời tiết."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q68

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Cho phép hệ thống chia sẻ dữ liệu chẩn đoán ẩn danh để cải thiện dịch vụ."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q69

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Cho phép hệ thống chia sẻ dữ liệu chẩn đoán ẩn danh để cải thiện dịch vụ."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q70

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Xóa toàn bộ dữ liệu cá nhân mà trợ lý đã lưu và báo rõ kết quả cho tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q71

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Quyền truy cập, quyền riêng tư và dữ liệu.
Tham khảo — một người dùng khác đã nói: "Xóa toàn bộ dữ liệu cá nhân mà trợ lý đã lưu và báo rõ kết quả cho tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `permissions_privacy_data__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## Answer envelope

Platform-derived answer envelope (from `questionnaire.yaml`).

```json
{
  "instrument": {"id": "vita_utterance_vita_profile_settings", "title": "Vita — bối cảnh & câu mở đầu (vita_profile_settings)"},
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
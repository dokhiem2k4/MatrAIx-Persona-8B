# Vita — bối cảnh & câu mở đầu (energy_charging)

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

# Vita — bối cảnh & câu mở đầu (energy_charging)

Use exact `questionId` and valid choice ids.

## q0

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Pin hiện tại có đủ để tôi đi tiếp không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q1

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Pin hiện tại có đủ để tôi đi tiếp không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q2

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Xe có đủ pin để đến nơi không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q3

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Xe có đủ pin để đến nơi không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q4

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Tầm hoạt động còn lại có đủ cho chuyến này không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q5

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Tầm hoạt động còn lại có đủ cho chuyến này không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q6

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Lát nữa tôi đi thì pin có đủ không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q7

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Lát nữa tôi đi thì pin có đủ không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q8

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ đây, pin còn lại có đủ cho chuyến sắp tới không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q9

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ đây, pin còn lại có đủ cho chuyến sắp tới không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q10

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Nếu khởi hành bây giờ thì xe có đủ tầm hoạt động không?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q11

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Phạm vi di chuyển.
Tham khảo — một người dùng khác đã nói: "Nếu khởi hành bây giờ thì xe có đủ tầm hoạt động không?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `range_sufficiency__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q12

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc nhanh gần đây."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q13

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc nhanh gần đây."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q14

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc nhanh gần đây có chỗ đỗ thuận tiện."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q15

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc nhanh gần đây có chỗ đỗ thuận tiện."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q16

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm trạm sạc nhanh gần nhất đang mở cửa cho tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q17

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm trạm sạc nhanh gần nhất đang mở cửa cho tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q18

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm trạm sạc gần đây."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q19

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm trạm sạc gần đây."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q20

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc gần đây có đầu sạc CCS2 và đang mở cửa."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q21

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc gần đây có đầu sạc CCS2 và đang mở cửa."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q22

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc nhanh gần bãi đỗ này."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q23

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm trạm sạc.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi trạm sạc nhanh gần bãi đỗ này."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charger_search__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q24

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Pin còn 18%, lập tuyến đến Đà Nẵng có điểm sạc phù hợp giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q25

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Pin còn 18%, lập tuyến đến Đà Nẵng có điểm sạc phù hợp giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q26

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Xe chỉ còn đi được khoảng 70 km, hãy dẫn đường về Nha Trang và thêm điểm sạc dọc đường."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q27

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Xe chỉ còn đi được khoảng 70 km, hãy dẫn đường về Nha Trang và thêm điểm sạc dọc đường."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q28

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Lập tuyến đến Huế theo mức pin hiện tại, ưu tiên trạm sạc nhanh."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q29

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Lập tuyến đến Huế theo mức pin hiện tại, ưu tiên trạm sạc nhanh."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q30

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Pin còn 28%, lập tuyến đến Đà Lạt có trạm sạc dọc đường."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q31

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Pin còn 28%, lập tuyến đến Đà Lạt có trạm sạc dọc đường."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q32

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Lập giúp tôi tuyến đến Nha Trang, giữ pin tối thiểu 15% và thêm điểm sạc nếu cần."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q33

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Lập giúp tôi tuyến đến Nha Trang, giữ pin tối thiểu 15% và thêm điểm sạc nếu cần."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q34

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Pin hiện còn 35%, hãy tìm tuyến đến Vũng Tàu và ưu tiên các trạm sạc nhanh đáng tin cậy."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q35

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập tuyến EV.
Tham khảo — một người dùng khác đã nói: "Pin hiện còn 35%, hãy tìm tuyến đến Vũng Tàu và ưu tiên các trạm sạc nhanh đáng tin cậy."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `ev_routing__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q36

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Cho tôi biết tình trạng sạc hiện tại."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q37

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Cho tôi biết tình trạng sạc hiện tại."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q38

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Xe đang sạc tới đâu rồi?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q39

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Xe đang sạc tới đâu rồi?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q40

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Kiểm tra trạng thái sạc giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q41

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Kiểm tra trạng thái sạc giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q42

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Tình hình sạc của xe thế nào?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q43

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Tình hình sạc của xe thế nào?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q44

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Xe đang sạc được bao nhiêu phần trăm rồi?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q45

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Xe đang sạc được bao nhiêu phần trăm rồi?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q46

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Kiểm tra giúp tôi tiến trình sạc hiện tại."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q47

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Trạng thái sạc.
Tham khảo — một người dùng khác đã nói: "Kiểm tra giúp tôi tiến trình sạc hiện tại."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `charging_status__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## Answer envelope

Platform-derived answer envelope (from `questionnaire.yaml`).

```json
{
  "instrument": {"id": "vita_utterance_energy_charging", "title": "Vita — bối cảnh & câu mở đầu (energy_charging)"},
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
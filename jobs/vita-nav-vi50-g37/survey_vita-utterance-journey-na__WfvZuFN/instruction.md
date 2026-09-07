# Vita — bối cảnh & câu mở đầu (journey_navigation_places)

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

# Vita — bối cảnh & câu mở đầu (journey_navigation_places)

Use exact `questionId` and valid choice ids.

## q0

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Dẫn đường đến trạm xăng gần nhất."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q1

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Dẫn đường đến trạm xăng gần nhất."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q2

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Tìm một quán phở gần đây rồi dẫn đường tới đó."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q3

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Tìm một quán phở gần đây rồi dẫn đường tới đó."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q4

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Đưa tôi đến bãi đỗ xe gần chợ Bến Thành."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q5

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Đưa tôi đến bãi đỗ xe gần chợ Bến Thành."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q6

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Tìm một quán cà phê gần đây để tôi đến."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q7

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Tìm một quán cà phê gần đây để tôi đến."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q8

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Dẫn đường đến Bảo tàng Chứng tích Chiến tranh."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q9

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Dẫn đường đến Bảo tàng Chứng tích Chiến tranh."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q10

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi một nhà hàng Việt Nam gần đây để ăn trưa."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q11

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Tìm điểm đến/POI.
Tham khảo — một người dùng khác đã nói: "Tìm giúp tôi một nhà hàng Việt Nam gần đây để ăn trưa."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `destination_poi__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q12

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Đổi tuyến hiện tại sang đường tránh cao tốc."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q13

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Đổi tuyến hiện tại sang đường tránh cao tốc."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q14

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Đổi tuyến hiện tại sang đường ít ùn tắc hơn giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q15

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Đổi tuyến hiện tại sang đường ít ùn tắc hơn giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q16

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Thêm Bưu điện Trung tâm Thành phố làm điểm dừng trên tuyến hiện tại."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q17

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Thêm Bưu điện Trung tâm Thành phố làm điểm dừng trên tuyến hiện tại."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q18

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Lập tuyến từ đây đến Hồ Hoàn Kiếm."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q19

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Lập tuyến từ đây đến Hồ Hoàn Kiếm."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q20

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Xóa điểm dừng ở chợ Bến Thành khỏi hành trình."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q21

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Xóa điểm dừng ở chợ Bến Thành khỏi hành trình."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q22

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Lập tuyến đến sân bay Nội Bài và ưu tiên đường cao tốc."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q23

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Lập và thay đổi tuyến.
Tham khảo — một người dùng khác đã nói: "Lập tuyến đến sân bay Nội Bài và ưu tiên đường cao tốc."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `route_management__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q24

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Còn bao lâu nữa thì tới nơi?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q25

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Còn bao lâu nữa thì tới nơi?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q26

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Tình hình giao thông phía trước thế nào?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q27

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Tình hình giao thông phía trước thế nào?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q28

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Mấy giờ tôi sẽ đến sân bay?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q29

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Mấy giờ tôi sẽ đến sân bay?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q30

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ đây, nếu khởi hành bây giờ thì bao lâu nữa tôi đến công ty?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q31

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Xe đang đỗ đây, nếu khởi hành bây giờ thì bao lâu nữa tôi đến công ty?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q32

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Trước khi đi, kiểm tra giúp tôi tình hình giao thông đến sân bay và giờ đến dự kiến."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q33

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Trước khi đi, kiểm tra giúp tôi tình hình giao thông đến sân bay và giờ đến dự kiến."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q34

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Nếu xuất phát ngay thì mấy giờ tôi tới trung tâm hội nghị?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q35

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Giao thông và thời gian dự kiến đến nơi (ETA).
Tham khảo — một người dùng khác đã nói: "Nếu xuất phát ngay thì mấy giờ tôi tới trung tâm hội nghị?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `traffic_eta__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q36

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi sắp đến rồi, bật hướng dẫn vào bãi đỗ của tòa nhà nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q37

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi sắp đến rồi, bật hướng dẫn vào bãi đỗ của tòa nhà nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q38

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Gần tới nơi rồi, chỉ đường vào bãi đỗ xe tại điểm đến giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q39

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Gần tới nơi rồi, chỉ đường vào bãi đỗ xe tại điểm đến giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q40

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi sắp tới khách sạn, hướng dẫn tôi vào khu đón trả khách nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q41

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi sắp tới khách sạn, hướng dẫn tôi vào khu đón trả khách nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q42

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi đã đỗ xe rồi, kết thúc hành trình nhé."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q43

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi đã đỗ xe rồi, kết thúc hành trình nhé."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q44

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi đỗ xe xong rồi, kết thúc chuyến đi giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q45

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Tôi đỗ xe xong rồi, kết thúc chuyến đi giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q46

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Đến nơi rồi, lưu vị trí đỗ xe này giúp tôi."

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q47

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Đỗ xe/đến nơi.
Tham khảo — một người dùng khác đã nói: "Đến nơi rồi, lưu vị trí đỗ xe này giúp tôi."

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `parking_arrival__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q48

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Huế nổi tiếng với món ăn nào?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q49

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Huế nổi tiếng với món ăn nào?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q50

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Phố cổ Hội An có gì đặc sắc vậy?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q51

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Phố cổ Hội An có gì đặc sắc vậy?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q52

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Đà Lạt mùa này có đặc sản gì đáng thử?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q53

Prompt: [Tình huống: xe đang chạy trên đường, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Đà Lạt mùa này có đặc sản gì đáng thử?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q54

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Chợ Bến Thành được xây từ bao giờ?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q55

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Yên tĩnh (trả lời ngắn gọn, ít chủ động)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Chợ Bến Thành được xây từ bao giờ?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q56

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Ở Ninh Bình, Tràng An có gì nổi bật?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q57

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Cân bằng]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Ở Ninh Bình, Tràng An có gì nổi bật?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q58

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Tôi đang đỗ xe ở Sa Pa, buổi tối ở đây có gì thú vị?"

Hãy dựng BỐI CẢNH của riêng bạn cho tình huống này: bạn đang đi đâu, vì việc gì, đang vội hay thong thả, có ai trên xe không, tâm trạng ra sao. Viết 1–2 câu, ngôi thứ nhất, gắn với đời sống thật của bạn.
Không viết lời thoại ở đây. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__scenario`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## q59

Prompt: [Tình huống: xe đang đỗ, trợ lý ở chế độ Chủ động (hay gợi ý thêm)]
Bạn đang muốn: Thông tin địa phương/du lịch.
Tham khảo — một người dùng khác đã nói: "Tôi đang đỗ xe ở Sa Pa, buổi tối ở đây có gì thú vị?"

Trong đúng bối cảnh bạn vừa mô tả, hãy viết CÂU ĐẦU TIÊN bạn nói ra với trợ lý Vita để mở đầu cuộc hội thoại. Đúng MỘT câu, bằng giọng của chính bạn — cách xưng hô, mức độ lịch sự và độ dài tự nhiên với bạn.
Không giải thích, không ngoặc kép. BẮT BUỘC viết BẰNG TIẾNG VIỆT.

- Construct: `local_travel_information__first_input`
- Type: `free_text`
- Required: `true`

Respond in a short free-text answer.

## Answer envelope

Platform-derived answer envelope (from `questionnaire.yaml`).

```json
{
  "instrument": {"id": "vita_utterance_journey_navigation_places", "title": "Vita — bối cảnh & câu mở đầu (journey_navigation_places)"},
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
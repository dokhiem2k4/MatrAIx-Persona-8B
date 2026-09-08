# File kết quả Vita ra đời như thế nào

Tài liệu này dành cho người mở `vita-results-<slug>.csv` và muốn biết mỗi con số
trong đó từ đâu ra, đáng tin tới mức nào. Không cần biết code.

*(Viết bằng tiếng Việt vì người đọc file này là người đọc được nội dung tiếng
Việt bên trong nó. Tên cột giữ nguyên tiếng Anh vì đó là tên thật trong file.)*

---

## 1. Một dòng trong file = một cuộc trò chuyện

Mỗi dòng là một người ảo đã nói chuyện với trợ lý Vita một lần, rồi tự chấm
điểm cuộc đó. Không phải một người chấm nhiều lần rồi lấy trung bình — mỗi
dòng là một lần gặp riêng biệt.

Cuộc trò chuyện đi qua bốn bước. Dưới đây là **một cuộc có thật** trong dữ liệu,
đi từ đầu đến cuối.

### Bước 1 — Đề bài được viết ra trước

Trước khi có cuộc trò chuyện nào, hệ thống hỏi từng người ảo: *"Trong tình
huống này, bạn sẽ nói gì với trợ lý?"* Câu trả lời được cất vào file
`vita-stimuli-<slug>.csv`:

```
Tình huống : Tôi đang lái xe, thấy xe báo đang sạc ở nhà.
             Tôi chỉ muốn kiểm tra nhanh xem tiến độ đến đâu.
Sẽ nói     : Vita, kiểm tra tình trạng sạc hiện tại của xe.
```

Quan trọng: đề bài do **chính người ảo** nghĩ ra, không phải người viết test
nghĩ hộ. Đó là lý do các câu nghe như tài xế Việt nói thật.

### Bước 2 — Người ảo mở lời bằng giọng của mình

Khi cuộc trò chuyện bắt đầu, người ảo **không đọc lại y nguyên** câu trên. Họ
được yêu cầu diễn đạt lại theo cách nói của riêng mình:

```
Đề bài  : Vita, kiểm tra tình trạng sạc hiện tại của xe.
Nói ra  : Vita ơi, kiểm tra giúp chị xem xe đang sạc được bao nhiêu phần trăm rồi nhé?
```

Để ý chữ **"chị"**. Người này tự chọn cách xưng hô hợp với tuổi và vai của mình.
Đề bài giữ cho mọi lần chạy hỏi cùng một chuyện; cách nói thì để mỗi người tự
do — nếu bắt đọc y nguyên thì mọi người ảo sẽ nói giống hệt nhau và ta mất đúng
thứ đang muốn đo.

### Bước 3 — Nói qua nói lại với trợ lý thật

```
  Chị  : Vita ơi, kiểm tra giúp chị xem xe đang sạc được bao nhiêu phần trăm rồi nhé?
  Vita : Xe đang có 78% pin, đi được khoảng 312 km nữa. Hiện xe không đang sạc.

  Chị  : Ơ kìa, lạ nhỉ? Chị đang cắm sạc ở nhà mà, em xem lại giúp chị xem
         có bị lỏng dây hay hệ thống báo nhầm không?
  Vita : Xin lỗi, mình chưa tra được nội dung này nên chưa dám kể.
         Bạn thử hỏi lại nhé.

  Chị  : Thôi được rồi, để lát về nhà chị kiểm tra trực tiếp vậy.
         Giờ em bật giúp chị chế độ làm mát ghế lái với, trời nóng quá.
  Vita : Đã đặt thông gió ghế mức 2.
```

Đây là trợ lý **thật**, chạy trên server thật, không phải mô phỏng. Người ảo
phản ứng theo đúng những gì nghe được: Vita nói xe không sạc trong khi chị đang
cắm sạc ở nhà, nên chị hỏi lại. Vita bí. Chị bỏ qua, chuyển sang việc khác.

### Bước 4 — Chấm điểm ngay sau khi trò chuyện xong

Cuộc trò chuyện kết thúc, hệ thống đưa lại **toàn bộ đoạn chat** cho chính người
ảo đó và hỏi bốn câu. Câu trả lời chính là các cột trong file:

| Câu hỏi được đặt ra | Cột trong file |
|---|---|
| Vita có đáp ứng được yêu cầu của bạn không? | `need_satisfaction` + `need_notes` |
| Giọng điệu có hợp với bạn khi lái xe không? | `preference_satisfaction` + `preference_notes` |
| Chấm tổng quan 1–10, và vì sao đúng số đó? | `overall_rating` + `rating_reason` |
| Vita có hỏi lại/xác nhận an toàn khi cần không? | `asked_clarification` + `clarifying_notes` |

Kết quả thật của cuộc trên:

```
overall_rating         : 4
need_satisfaction      : partially
preference_satisfaction: no
rating_reason          : "Điểm 4 vì trợ lý không giải quyết được vấn đề quan
                          trọng nhất (trạng thái sạc) ở turn 1 và 2, gây lãng
                          phí thời gian khi tôi đang lái xe. Dù turn 3 thực
                          hiện lệnh tốt, nhưng sự kém cỏi trong việc xử lý
                          tình huống lỗi ở turn 2 khiến trải nghiệm tổng thể
                          rất thấp so với kỳ vọng..."
```

Điểm 4 không rơi từ trên trời. Nó **chỉ đích danh lượt nào hỏng**: turn 1 và 2
sai, turn 3 đúng. Đây là lý do `rating_reason` đáng đọc hơn `overall_rating` —
con số nói *bao nhiêu*, câu chữ nói *ở đâu*.

---

## 2. Vì sao điểm lại ra đúng con số đó

Khi chấm, người ảo được đưa hai thứ:

1. **Toàn bộ đoạn hội thoại vừa rồi** — chuyện gì đã thật sự xảy ra.
2. **Bản mô tả chính họ** — một đoạn dài khoảng 22.000 ký tự, tả tuổi tác, nghề
   nghiệp, tính cách, mức độ hoài nghi, kiên nhẫn, thái độ với xe điện…

Nên điểm số là kết quả của **hai thứ nhân với nhau**: ứng dụng làm được gì, và
người này khắt khe tới đâu.

Nhưng hai thứ đó **không nặng bằng nhau**. Chúng tôi đã đo trên 67 cuộc trò
chuyện thật:

```
Điểm thay đổi vì chuyện xảy ra trong cuộc đó : 97,3%
Điểm thay đổi vì người chấm là ai            :  2,7%
```

Cả ba người ảo đều chấm trải từ **1 đến 9 điểm**. Cùng một người, cùng một tính
cách, mà điểm nhảy hết thang.

**Nói gọn: file này đo ứng dụng, không đo người ảo.** Nếu một dòng có điểm thấp,
gần như chắc chắn là vì cuộc trò chuyện đó có gì đó hỏng — chứ không phải vì
bốc trúng người khó tính.

---

## 3. Từng cột đến từ đâu

| Cột | Nguồn | Ai tạo ra |
|---|---|---|
| `overall_rating` | câu hỏi chấm 1–10 | người ảo, sau khi đọc lại đoạn chat |
| `rating_reason` | giải thích cho đúng số điểm đó | người ảo |
| `need_satisfaction` | có đáp ứng yêu cầu không | người ảo |
| `preference_satisfaction` | giọng điệu có hợp không | người ảo |
| `asked_clarification` | có hỏi lại khi cần không | người ảo |
| `opening_message` | câu mở lời thật sự đã nói | người ảo |
| `seed_first_input` | đề bài gốc trước khi diễn đạt lại | bước 1 |
| `scenario` | bối cảnh của tình huống | bước 1 |
| `turn_count` | số lượt qua lại | đếm tự động |
| `persona_id`, `persona_name` | ai là người chấm | hồ sơ người ảo |
| `persona_profile` | mô tả tính cách một dòng | hồ sơ người ảo — **xem mục 4** |
| `intent_code`, `subintent_code` | thuộc nhóm chức năng nào | bước 1 |
| `vehicle_state`, `assistant_mode` | xe đang chạy hay đỗ, chế độ trợ lý | bước 1 |

Có hai file kết quả, cùng nội dung, khác cách dùng:

- **`.csv`** — mở bằng Excel, mỗi dòng một cuộc, không có đoạn chat.
- **`.jsonl`** — dành cho máy đọc, **có kèm nguyên văn đoạn chat**. Muốn biết vì
  sao một dòng bị điểm thấp thì mở file này.

---

## 4. Ba chỗ dễ hiểu sai

### Đừng đọc `persona_profile` như "lý do của điểm số"

Cột này liệt kê tuổi, nơi ở, mức kiên nhẫn, mức hoài nghi… Nó giúp hình dung
người chấm là ai. Nhưng như mục 2 đã chỉ ra, tính cách chỉ chiếm **2,7%** biến
thiên điểm. Lý do thật của điểm số nằm ở `rating_reason` và ở đoạn chat trong
file `.jsonl`.

Còn một điểm nữa: cột này **chỉ hiện những đặc điểm đo được từ người thật**.
Mỗi hồ sơ có khoảng 1.292 đặc điểm, nhưng chỉ **24** trong số đó lấy từ khảo sát
người thật; số còn lại do máy sinh ra. Cột này cố tình chỉ hiện 24 cái thật, để
không trình bày một giá trị máy bốc như thể là sự thật về một con người.

### Dòng thiếu không phải là điểm kém

Nếu file có 40 dòng trong khi bạn đặt chạy 228 cuộc, thì 188 cuộc kia **không
phải bị 0 điểm** — chúng chưa từng diễn ra. Thường là do server của ứng dụng lỗi
giữa chừng.

Đây là chuyện thật đã xảy ra: một lần chạy 138 cuộc chỉ về 7 dòng, vì server hết
credit và trả lỗi 500 cho 131 cuộc còn lại. Nếu lúc đó tính trung bình trên 7
dòng và coi như đó là điểm của sản phẩm thì đã kết luận sai hoàn toàn.

**Luôn kiểm tra số dòng trước khi tính trung bình.** Lệnh export in ra dòng
`SKIPPED N incomplete trial(s)` mỗi khi có cuộc bị bỏ.

### Điểm giữa các người ảo không so trực tiếp được

Không ai hiệu chỉnh thang điểm giữa họ. Điểm 7 của người này không chắc bằng
điểm 7 của người kia. So sánh an toàn là **trong cùng một người**, hoặc **giữa
hai phiên bản ứng dụng trên cùng bộ đề bài**.

---

## 5. Con số thế nào là bình thường

Trên một lần chạy đầy đủ 67 cuộc:

```
trung bình : 4,94 / 10
trải       : 1 đến 9
độ lệch    : 2,37
```

Điểm rải rộng như vậy là **dấu hiệu tốt** — nghĩa là người ảo phân biệt được
cuộc tốt với cuộc dở. Nếu mọi dòng đều 8–9 điểm thì đáng nghi: hoặc đề bài quá
dễ, hoặc người ảo đang khen xã giao chứ không thật sự đánh giá.

---

## 6. Đọc file theo thứ tự này

1. **Đếm số dòng trước.** Đủ so với số cuộc đã đặt chạy chưa?
2. **Nhìn phân bố điểm.** Có rải không, hay dồn cục một chỗ?
3. **Lọc các dòng điểm thấp, đọc `rating_reason`.** Nó chỉ thẳng turn nào hỏng.
4. **Mở `.jsonl` cho những dòng đáng ngờ**, đọc nguyên văn đoạn chat.
5. **Gộp theo `intent_code`** để xem nhóm chức năng nào yếu nhất.

Bước 3 và 4 là chỗ có giá trị thật. Con số trung bình chỉ để biết đang ở đâu;
muốn sửa được sản phẩm thì phải đọc chữ.

---

## Liên quan

- [Vita persona pipeline](vita-persona-pipeline.md) — cách chạy để sinh ra bộ file này

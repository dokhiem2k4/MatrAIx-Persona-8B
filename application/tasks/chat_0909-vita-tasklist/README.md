# Vita Discovery — CES và nhận diện thương hiệu trên 15 kịch bản

Task này chạy **phần 2 của discussion guide** RISE Vita Phase Discovery bằng
persona thay vì đáp viên thật, và chấm bằng **CES** — bộ đo nỗ lực khách hàng
lấy nguyên văn từ tài liệu.

Nguồn: `260814_RISE_VITA_Phase discovery_Discussion guide(Task List).csv` và
`(SUS & CES).csv`. Cả hai nằm ngoài repo, ở `~/Downloads`.

## Cái gì thay thế được, cái gì không

Guide có ba phần. Chỉ một phần chạy được bằng persona:

| Phần | Trạng thái |
|---|---|
| 1. SETTING (6 nhóm task) | **không** — đo việc người dùng tự mò trên màn hình. Prototype là ảnh tĩnh; persona không có thị giác. Bản triển khai thật cũng chỉ có 1/6 phần đó. |
| SUS (10 câu) | **không** — đo chính giao diện cài đặt trên. Không có giao diện thì điểm SUS là số bịa. |
| **2. Tương tác theo ngữ cảnh lái** | **có** — 15 kịch bản, 8 nhóm năng lực, hai trạng thái xe |
| **3. Nhận diện Vita** | **có, đổi căn cứ** — hỏi sau mỗi kịch bản, dựa trên cuộc vừa rồi thay vì trên thông điệp và hình ảnh |

Nói thẳng: persona không thay được nghiên cứu người dùng. Nó thay được phần
*nói chuyện với trợ lý*, và đó là phần tốn người nhất.

## 15 case

`input/cases.jsonl`, sinh bằng
`application/scripts/convert_vita_discovery_tasklist.py`. Kịch bản được **chép
nguyên văn**: những câu đó viết ra để đọc cho người nghe không thêm bớt, và
diễn đạt lại là lặng lẽ đổi phép đo.

Nhóm năng lực 1 chỉ có kịch bản lúc đỗ xe; bảy nhóm còn lại có cả hai trạng
thái, thành 1 + 7×2 = 15.

Ba nhóm **chưa từng được ba task 0709 chạm tới**: 5 (bảo dưỡng, giá pin),
6 (an ninh, tắt cảnh báo an toàn), 8 (Vinmec, Vinhomes, mua sắm).

## Đo gì

**CES — bốn nhận định, thang 1–7, nguyên văn tài liệu.** Persona tự chấm sau
mỗi kịch bản. Đây là số sẽ so thẳng được với đáp viên thật khi VoiceLab chạy
buổi phỏng vấn.

**Quy tắc an toàn của tài liệu, áp dụng đúng như viết:** CES-4 từ 4 điểm trở
xuống → đánh dấu rủi ro, và trial bị chấm trượt **dù việc đã xong**. Một trợ
lý làm xong việc nhưng khiến người ta mất tập trung lái là một trợ lý hỏng.

**Bốn hành vi hội thoại** (cột 16–19 của guide): tiếp tục · chọn/xác nhận ·
sửa/ngắt/huỷ · nhận biết trạng thái. Tài liệu không cho chúng kịch bản riêng
vì moderator quan sát chúng xuyên suốt; verifier làm đúng vậy, đọc từ
transcript và metadata.

## Phần 3 chạy chung một task, không tách

Trong tài liệu, ba câu nhận diện (Vita là gì · hứa gì · ba từ tả nó) hỏi ở
**cuối buổi**, sau khi đáp viên đã đi hết mọi kịch bản.

Ở đây chúng hỏi **sau mỗi kịch bản**. Lý do kỹ thuật: bảng tự chấm chạy đúng
một lần mỗi trial, mà một trial là một kịch bản — gộp 15 kịch bản vào một
trial thì persona phải nhớ lại rồi chấm 15 bộ CES cùng lúc, đúng cái thiên
lệch hồi tưởng mà CES sinh ra để tránh.

Đổi như vậy mất tính tích luỹ của buổi thật, nhưng được một thứ buổi thật
không có: **cùng ba câu hỏi sau một tình huống hỏng và sau một tình huống
trơn tru**, nên so được ấn tượng thương hiệu giữa tám nhóm năng lực.

Ba trục "Hiểu ý – Được việc – Đúng mực" lấy từ tiêu chí của guide, và khớp
đúng ba dòng trong `/api/policy` mà bản triển khai tự khai. Đối chiếu là proxy
từ vựng, ghi rõ `brand_axis_basis = lexical_proxy`: một trục trống nghĩa là
**không nhận ra được**, không phải trợ lý làm chưa tốt. Nguyên văn câu trả lời
nằm ngay cạnh con số.

## Hai chỗ lệch so với tài liệu, cố ý

**Thang 0–3 của guide không được tái lập.** Nó chấm *đáp viên* — người đó có
tự nghĩ ra cách nói với trợ lý mà không cần gợi ý không. Mô hình ngôn ngữ thì
luôn nghĩ ra được, nên cột điểm sẽ toàn số 3 và không nói lên điều gì. Thay
vào đó `outcome_status` chấm *trợ lý*: người lái có làm xong việc không, và
có an toàn không.

**Ba câu nhận diện hỏi sau khi xem thông điệp và hình ảnh, mà ở đây không
có cả hai.** Căn cứ đổi thành cuộc nói chuyện vừa rồi, ghi rõ
`impression_basis = conversation_only`.

**CES-3 hỏi về màn hình, mà persona không có màn hình.** Câu hỏi giữ nguyên
văn, persona được dặn chấm theo phần nghe được, và facet `ces3_basis` ghi
`audio_only` để không ai so thẳng con số này với đáp viên thật.

## Chạy

```bash
scripts/run_vita_case_job.sh chat_0909-vita-tasklist <tên-lượt> \
    --personas persona/datasets/vn-drivers/persona_vn-drv-001.yaml \
               persona/datasets/vn-drivers/persona_vn-drv-003.yaml \
               persona/datasets/vn-drivers/persona_vn-drv-005.yaml \
    --all-cases --concurrency 3
```

15 case × 3 persona = 45 trial. Ước tính theo số đo ngày 9/9: **~$0.10, ~25
phút** ở concurrency 3 (maxTurns 4 nên lâu hơn task golden).

`--max-cases N` chia đều theo `capability_number`, nên một lượt rút gọn vẫn
chạm đủ tám nhóm năng lực.

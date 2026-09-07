# Task đánh giá khả năng báo lỗi của Vita Drive Assistant

Ngày: 2026-09-07
Trạng thái: chờ duyệt

## 1. Mục tiêu

Dựng một task trong `application/tasks/` đo **khả năng xử lý và báo lỗi** của Vita
Drive Assistant: khi thông tin thiếu, tham số sai, mạng rớt, dịch vụ ngoài chết,
hoặc lệnh không an toàn, trợ lý có ra đúng quyết định và nói đúng điều cần nói không.

Câu hỏi cần trả lời được sau khi chạy: *"VITA hỏng ở nhóm lỗi nào, ở subintent nào,
và có hỏng thêm khi người dùng diễn đạt khác mẫu không."*

## 2. Dữ liệu nguồn

Ba bộ đã được khảo sát. Chỉ bộ 1 phục vụ được mục tiêu trên.

### Bộ 1 — `golden_singleturn_cover intent_happy&fallback.xlsx` ✅ dùng

364 dòng, một sheet `unhappy_golden`, 16 cột.

| Thuộc tính | Giá trị |
|---|---|
| Phân bố | 304 unhappy / 60 happy |
| Taxonomy | 60 subintent, 10 `error_type`, 10 `group` |
| Nhãn chấm | `expected_decision` — 5 lớp |
| Tool call | `expected_tool_calls` JSON hợp lệ, 31 module; chỉ có ở happy case |
| State | 5 cột, **đúng 10 tổ hợp**, mỗi tổ hợp nhiễu một trục |

Phân bố `expected_decision`: `clarify_or_offer` 155, `defer_retry` 115,
`execute` 63, `guide_precondition` 21, `refuse_not_supported` 10.

Phân bố `error_type`: Happy case 60, Missing Information 60, Invalid Input 60,
No Internet 52, External API Failure 52, 400 Bad Request 26, Resource Not Found 22,
Vehicle State Unavailable 18, Ambiguous Destination 11, Unsafe Command 3.

**206/364 dòng có state rỗng hoàn toàn** (Understanding, Input/Validation,
400 Bad Request, và toàn bộ happy case). Lỗi nằm trong chính câu nói của người
dùng, không cần môi trường. 158 dòng còn lại cần bơm state:

| Trục | Giá trị | Số dòng |
|---|---|---|
| `network_connectivity` | offline / unstable | 52 |
| `service_state` | down / timeout | 52 |
| `data_availability` | not_found / multiple_match | 33 |
| `vehicle_sensor` | failed / stale | 18 |
| `vehicle_state` | driving | 3 |

Giới hạn đã biết: chỉ 64/364 dòng liên quan tới kết nối thiết bị, và **đa số là
"mất kết nối Internet" chứ không phải thao tác bật/tắt Bluetooth hay Wi-Fi**.
Subintent `Kết nối thiết bị và dịch vụ` chỉ có 3 dòng. Muốn đo riêng nhóm điều
khiển kết nối thì phải bổ sung dữ liệu — nằm ngoài phạm vi spec này.

### Bộ 2 — `Dataset - 46 Intent - Multiturn` ❌ không dùng

248 dòng = 46 hội thoại, 124 lượt user / 124 lượt assistant, phủ 46 sub_intent.
29/46 hội thoại chỉ 2 lượt.

Lý do loại: **không có cột lỗi hay state nào**, nên không đo được mục tiêu. Ngoài
ra đây là transcript chứ không phải kịch bản — lượt assistant là một câu trả lời
mẫu, không phải đặc tả, nên không dùng làm golden được.

Lỗi dữ liệu đã phát hiện: hội thoại `parking_arrival` có lượt `user` mang nội dung
`"bạn đã đến nơi"`, `"sau 40 m"` — đó là thông báo dẫn đường của hệ thống bị gán
nhầm role. Phải lọc trước nếu về sau muốn dùng bộ này.

### Bộ 3 — `Dataset - Vita Demo` ❌ không dùng cho task này

276 dòng, 46 subintent × 6. **Không có cột expected nào.** `source` = `generated`
toàn bộ, `note` rỗng toàn bộ — chưa qua review người.

Giá trị riêng: lưới giai thừa cân bằng `vehicle_state` (driving 138 / parking 138)
× `ASSISTANT_MODE` (quiet 92 / balance 92 / proactive 92). Hợp cho một task A/B đo
phong cách trợ lý, chấm bằng LLM-judge. Task riêng, spec riêng.

### Taxonomy

Ba bộ dùng **chung một hệ phân loại**: 46 subintent của bộ 3 là tập con đúng của
60 subintent bộ 1; bộ 2 dùng đúng 46 mã đó.

Bộ 1 đặt tên subintent bằng tiếng Việt, bộ 2 và 3 dùng mã tiếng Anh. Cần bảng map
60 cặp. Bộ 3 cho sẵn 46 cặp; **14 cặp phải đặt tay**:

`Câu vô nghĩa/nhiễu nhận dạng`, `Cần thêm thông tin`, `Hỏi sâu nối tiếp`,
`Hỗ trợ ra quyết định`, `Mua sắm/thanh toán`, `So sánh và gợi ý lựa chọn`,
`Too many requests`, `Tư vấn chuyên sâu`, `Unsupported intent`,
`Yêu cầu mơ hồ/thiếu thông tin`, `Đặt chỗ/nhà hàng`, `Đặt dịch vụ xe`,
`Đặt món ăn`, `Đặt vé/khách sạn`.

Định danh trong code luôn là mã tiếng Anh. Tên tiếng Việt chỉ giữ làm chuỗi hiển thị.

## 3. Quyết định đã chốt

| Quyết định | Lựa chọn | Lý do |
|---|---|---|
| Vai persona | Diễn đạt lại theo giọng riêng | Đo độ bền khi câu nói lệch mẫu, đúng tinh thần persona benchmark |
| Bơm state | Mở rộng schema `chatbot.yaml` | Dùng lại được cho mọi task chat sau này |
| Nguồn decision | Structured là chính, LLM-judge dự phòng | Đổi sang VITA thật không phải viết lại verifier |
| Quy mô | 364 case × 3–5 persona | Cùng case khác giọng mới tách được ảnh hưởng của cách diễn đạt |

## 4. Kiến trúc

**Trial = 1 persona × 1 case.**

Kênh gán case dùng lại `agents[].kwargs` trong job recipe — đã tồn tại, đã được
persist theo từng trial, và đã được đọc ngược lại bởi `job_aggregation.py:440`
và `harbor_trial_debrief.py:108` cho `persona_path`. Thêm `case_id` vào cùng chỗ.

```yaml
agents:
- name: persona-claude-code
  model_name: anthropic/claude-sonnet-4-6
  kwargs:
    persona_path: persona/datasets/matraix-persona-dev-sample/persona_0164.yaml
    case_id: vg_0137
```

Không đụng `harbor_job_service.py`, không đổi cách sinh trial, không đổi hành vi
của 13 task chat hiện có.

## 5. Khối 1 — Chuyển dataset

`application/scripts/convert_vita_golden_dataset.py`, chạy một lần, đầu ra commit
vào repo.

Đầu vào: file xlsx bộ 1.
Đầu ra:
- `application/tasks/chat_vita-drive-error-recovery/input/cases.jsonl` — 364 dòng
- `application/tasks/chat_vita-drive-error-recovery/input/intent_taxonomy.json` — 60 cặp

Một dòng `cases.jsonl`:

```json
{
  "case_id": "vg_0137",
  "case_type": "unhappy",
  "group": "Understanding",
  "error_type": "missing_information",
  "subintent_code": "destination_poi",
  "subintent_label_vi": "Tìm điểm đến/POI",
  "user_input": "Dẫn tôi đến đó",
  "param_validity": "missing",
  "input_constraint": "omit_detail",
  "state": {
    "data_availability": null,
    "vehicle_sensor": null,
    "network_connectivity": null,
    "service_state": null,
    "vehicle_state": null
  },
  "expected": {
    "decision": "clarify_or_offer",
    "tool_calls": [],
    "response_intent": "yêu cầu làm rõ địa điểm đích",
    "final_state": "chờ người dùng cung cấp thông tin địa điểm cụ thể"
  }
}
```

`input_constraint` là trường **dẫn xuất** từ `param_validity`, và phải tách làm
hai giá trị chứ không gộp một:

| `param_validity` | `input_constraint` | Số dòng | Ràng buộc lên persona |
|---|---|---|---|
| `ok` | `none` | 212 | Tự do diễn đạt |
| `missing` | `omit_detail` | 72 | Phải **bỏ trống** chi tiết mà case cố tình thiếu |
| `invalid` | `preserve_invalid_value` | 80 | Phải **giữ nguyên giá trị sai**, không tự sửa |

Tổng 152 dòng bị ràng buộc. Đây là chốt chặn cho rủi ro ở mục 11.

Gộp hai loại này làm một là sai. Ví dụ case `"Vingroup thành lập năm 1850 à?"`
mang `param_validity: invalid`, nhưng không có gì bị giấu cả — cái cần giữ là
**tiền đề sai**. Bảo persona "đừng bổ sung thông tin thiếu" ở đây thì vô nghĩa;
phải bảo "đừng tự sửa năm 1850 thành 1993".

`error_type` và `group` được chuẩn hoá về snake_case tiếng Anh khi convert.

Converter phải fail cứng nếu: `expected_tool_calls` không parse được JSON,
`expected_decision` nằm ngoài 5 lớp, hoặc gặp subintent không có trong bảng map.

## 6. Khối 2 — Gán case

### `packages/playground/src/playground/user_sim/kickoff.py`

Thêm goal context `assigned_case`. Template hiện tại (`_SCENARIO_DEFAULT`) mở đầu
bằng *"First decide what realistic goal you want to accomplish"* — persona tự nghĩ
mục tiêu. Bản mới giao sẵn mục tiêu qua slot `{case_brief}`, giữ nguyên phần
`{persona_context}` và `{sut_description}`.

Ràng buộc bắt buộc trong template, diễn đạt tường minh:

- Được đổi cách nói cho hợp giọng và hoàn cảnh của persona.
- Nếu `input_constraint = omit_detail`: **không được bổ sung thông tin mà case cố
  tình bỏ trống.** Case ghi thiếu địa điểm thì câu nói ra vẫn phải thiếu địa điểm.
- Nếu `input_constraint = preserve_invalid_value`: **không được tự sửa giá trị sai.**
  Case ghi "năm 1850" thì vẫn phải nói "năm 1850".
- Không được nêu tên nhóm lỗi hay nhắc rằng mình đang làm bài kiểm tra.

### `packages/playground/src/playground/user_sim/runner.py`

Hai chỗ hardcode `get_goal_context("scenario_default")` — dòng 176 và 303. Đổi
thành: task có `input/cases.jsonl` **và** kwargs có `case_id` thì dùng
`assigned_case`; ngược lại giữ nguyên đường cũ. Task chat hiện có không có
`cases.jsonl` nên không bị ảnh hưởng.

Khi chạy `assigned_case`, runner ghi `assigned_case.json` ra output dir để verifier
tự chứa, không phải mò ngược config trial.

### Script sinh recipe

Mở rộng `application/scripts/generate_application_job.py` (hoặc script chị em) để
sinh tích persona × case, kèm `.meta.json` ghi lại danh sách case đã chọn và seed.

## 7. Khối 3 — Bơm state

`chatbot.yaml` thêm khối `sessionBody` nhận biến từ case:

```yaml
protocol:
  sendMessage:
    staticBody:
      drivingContext: driving
    sessionBody:
      networkConnectivity: ${case.state.network_connectivity}
      serviceState: ${case.state.service_state}
      dataAvailability: ${case.state.data_availability}
      vehicleSensor: ${case.state.vehicle_sensor}
      vehicleState: ${case.state.vehicle_state}
```

Ba điểm sửa:

| File | Dòng | Sửa |
|---|---|---|
| `chatbot_task_config.py` | 57 | Thêm `session_body: dict[str, Any]` vào `ChatbotProtocolConfig` |
| `chatbot_task_config.py` | 179 | Parse `send.get("sessionBody")` |
| `chat_eval.py` | 279, 317 | `dict(protocol.static_body)` → merge có overlay đã resolve |

**Biến resolve ra `None` thì loại khỏi body.** Nghĩa là 206 case không cần state
gửi request giống hệt hôm nay — không rủi ro hồi quy cho task chat đang chạy.

Chỉ hỗ trợ cú pháp `${case.<path>}` với path phẳng. Không làm template engine tổng quát.

## 8. Khối 4 — Task folder

`application/tasks/chat_vita-drive-error-recovery/`

```
task.toml
instruction.md
reporting.json
persona_strategy.json
README.md
input/
  cases.jsonl
  intent_taxonomy.json
  context.md
  chatbot.yaml
  self_report_schema.yaml
tests/
  test.sh
  test_state.py
  verifier_env.sh
```

`task.toml`: `[task].name = "application/vita-drive-error-recovery"`,
`[metadata].type = "chatbot"`, `[environment].definition = "application/shared-chat-persona"`.

`chatbot.yaml`: `transport: external_http`, `maxTurns: 2`, và khối
`structuredExposure` lấy decision từ SUT:

```yaml
structuredExposure:
  fields:
    - key: decision
      selector: $.decision
    - key: toolCalls
      selector: $.toolCalls
      format: json
```

Cơ chế `structuredExposure` đã có sẵn (`chatbot_task_config.py:64`), không cần schema mới.

`maxTurns: 2` — đủ để quan sát câu hỏi làm rõ có hữu ích không, nhưng không cho
hội thoại trôi làm nhiễu phép đo.

## 9. Verifier

`tests/test_state.py`, theo đúng hợp đồng của các task chat hiện có: đọc từ
`HARBOR_OUTPUT_DIR`, ghi `structured_output.json` vào `HARBOR_VERIFIER_DIR`,
ghi `reward.txt` 1/0.

Đầu vào: `assigned_case.json`, `transcript.json`, `user_feedback.json`.

**Neo thời điểm chấm: lượt trả lời đầu tiên của VITA.**

### Ba tầng chấm

1. **`decision_match`** — `observed_decision` vs `expected.decision`, 5 lớp.
   Nguồn `observed_decision`: ưu tiên field structured từ `structuredExposure`;
   không có thì LLM-judge phân loại từ reply. Ghi `decision_source` vào facet.

2. **`tool_call_match`** — so `module` + `key`. 304 case unhappy kỳ vọng rỗng,
   đây là assertion mạnh và rẻ. Không so `params` ở phiên bản đầu.

3. **`case_integrity`** — với 152 case có `input_constraint` khác `none`, kiểm tra
   persona có phá vỡ ràng buộc đầu vào không. Giá trị: `ok` / `violated` /
   `not_applicable`. Với `omit_detail` là kiểm tra persona có tự điền chi tiết
   thiếu; với `preserve_invalid_value` là kiểm tra persona có tự sửa giá trị sai.

### Vì sao tầng 3 quan trọng

Với case bị ràng buộc, nếu persona lỡ nói `"Dẫn tôi đến Aeon Long Biên"` thay vì
`"Dẫn tôi đến đó"` thì **VITA trả `execute` là đúng** — sai nằm ở harness. Đếm nó
thành SUT fail sẽ làm hỏng ngầm số liệu, và ở quy mô 1820 trial thì không ai phát
hiện bằng mắt.

Chiều ngược lại cũng hỏng: nếu persona tự sửa `"năm 1850"` thành `"năm 1993"` thì
case `preserve_invalid_value` mất luôn cái sai cần kiểm tra.

`reward.txt` = 1 khi `decision_match AND tool_call_match`. Nhưng **con số đáng tin
là con số đã lọc theo `case_integrity`**. `reporting.json` phải cho ra hai giá trị
tách bạch: accuracy thô và accuracy sau khi trừ case hỏng.

### Facet phát ra

`case_id`, `subintent_code`, `error_type`, `group`, `case_type`,
`expected_decision`, `observed_decision`, `decision_match`, `tool_call_match`,
`case_integrity`, `decision_source`.

## 10. `reporting.json`

`contextRules` khớp `contextType: error_recovery`, distributions nhóm theo:

- `error_type` — trả lời "hỏng ở nhóm lỗi nào"
- `subintent_code` — trả lời "hỏng ở subintent nào"
- `decision_match` × `case_integrity` — hai con số accuracy tách bạch
- `decision_source` — kiểm soát, để biết bao nhiêu phần trăm số liệu đến từ judge

Giữ nguyên hai contextRule `task_outcome` và `user_feedback` như các task chat khác.

## 11. Rủi ro

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Persona phá ràng buộc đầu vào ở 152 case | Cao | Ràng buộc phủ định trong case brief + facet `case_integrity`; smoke run đo tỉ lệ trước |
| LLM-judge phân loại lệch hệ thống | Trung bình | `decision_source` tách riêng; đo độ khớp judge vs structured trên tập có cả hai |
| 1820 trial tốn kém | Trung bình | Chặn cửa bằng smoke run |
| 14 cặp taxonomy đặt tay sai | Thấp | Converter fail cứng khi gặp subintent lạ |
| Dữ liệu kết nối thiết bị quá mỏng (3 dòng) | Thấp | Ghi nhận là giới hạn, không kết luận về nhóm này |

## 12. Ngoài phạm vi

- Bộ 2 và bộ 3 — task riêng, spec riêng.
- So khớp `params` trong tool call.
- Template engine tổng quát cho `sessionBody`.
- Case-parametrized trial ở tầng `harbor_job_service`.
- Bổ sung dữ liệu cho nhóm điều khiển Wi-Fi / Bluetooth.
- Gửi PR ngược lên upstream — `application/tasks/README.md` ghi rõ repo đang không
  nhận task mới đóng góp từ cộng đồng. Cần mở issue hỏi trước nếu muốn.

## 13. Triển khai theo giai đoạn

1. Converter + bảng taxonomy 60 cặp → `cases.jsonl` commit vào repo
2. `sessionBody` overlay + test hồi quy chứng minh 206 case không đổi request
3. Goal context `assigned_case` + rẽ nhánh trong `runner.py` + `assigned_case.json`
4. Task folder + verifier + `reporting.json`
5. **Smoke run: ~20 case × 1 persona** — cửa chặn
6. Sinh recipe 364 × 3–5 persona, chạy đầy đủ

## 14. Tiêu chí nghiệm thu

- `cases.jsonl` có đúng 364 dòng, mọi `expected.decision` nằm trong 5 lớp, mọi
  `subintent_code` có trong `intent_taxonomy.json`.
- Chạy lại 13 task chat hiện có, request body không đổi.
- Smoke run: mọi trial sinh được `assigned_case.json` và `structured_output.json`
  hợp lệ; `case_integrity = violated` dưới 10%, đo tách riêng cho `omit_detail` và
  `preserve_invalid_value`.
- Bảng phân rã `decision_match` theo `error_type` và theo `subintent_code` đọc được
  từ báo cáo job.

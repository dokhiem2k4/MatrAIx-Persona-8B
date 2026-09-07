# Chương trình đánh giá Vita Drive Assistant trên 3 bộ dataset

Ngày: 2026-09-07
Trạng thái: chờ duyệt

## 1. Mục tiêu

Ba bộ dataset hiện đang được test tay. Dựng **ba task** trong `application/tasks/`
để tự động hoá cả ba, chạy bằng persona model 8B.

| Task | Bộ | Lượt | Câu hỏi task trả lời |
|---|---|---|---|
| `chat_vita-drive-error-recovery` | 1 | single | VITA hỏng ở nhóm lỗi nào, subintent nào |
| `chat_vita-drive-multiturn-coverage` | 2 | multi | VITA có giữ được ngữ cảnh qua nhiều lượt, trên đủ 46 sub_intent |
| `chat_vita-drive-assistant-mode-ab` | 3 | single | Chế độ trợ lý × trạng thái xe ảnh hưởng thế nào tới trải nghiệm |

Ba task tách rời vì **khả năng chấm khác nhau**, không phải vì số lượt. Bộ 1 có
nhãn cứng nên chấm so khớp; bộ 2 và 3 không có nhãn nên chấm bằng judge và
self-report. Trộn hai loại vào một `reporting.json` sẽ cho ra những con số không
cộng được với nhau.

Lý do kỹ thuật cứng thứ hai: `maxTurns` nằm trong `chatbot.yaml`, một giá trị cho
cả task. Một task đã cam kết ngân sách lượt của nó, không trộn được.

## 2. Dữ liệu nguồn

Ba bộ đã được khảo sát. Chỉ bộ 1 phục vụ được mục tiêu trên.

### Bộ 1 — `golden_singleturn_cover intent_happy&fallback.xlsx` ✅ dùng

364 dòng, một sheet `unhappy_golden`, 16 cột.

| Thuộc tính | Giá trị |
|---|---|
| Phân bố | 304 unhappy / 60 happy |
| Taxonomy | 60 subintent, 10 `error_type`, 10 `group` |
| Nhãn chấm | `expected_decision` — 5 lớp |
| Tool call | `expected_tool_calls` 31 module; 58 case có, tất cả đều là `execute` |
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

### Bộ 2 — `Dataset - 46 Intent - Multiturn` → task 2

248 dòng = 46 hội thoại, 124 lượt user / 124 lượt assistant, phủ 46 sub_intent.
29/46 hội thoại chỉ 2 lượt.

Không có cột lỗi hay state nào, nên bộ này **không đo được khả năng báo lỗi** —
đó là việc của task 1. Ngoài ra đây là transcript chứ không phải kịch bản: lượt
assistant là một câu trả lời mẫu, không phải đặc tả, nên không dùng làm golden.
Dùng làm **mốc tham chiếu** thì được.

Lỗi dữ liệu đã phát hiện: hội thoại `parking_arrival` có lượt `user` mang nội dung
`"bạn đã đến nơi"`, `"sau 40 m"` — đó là thông báo dẫn đường của hệ thống bị gán
nhầm role. Phải lọc trước nếu về sau muốn dùng bộ này.

### Bộ 3 — `Dataset - Vita Demo` → task 3

276 dòng, 46 subintent × 6. **Không có cột expected nào.** `source` = `generated`
toàn bộ, `note` rỗng toàn bộ — chưa qua review người.

Giá trị riêng nằm ở chỗ khác: lưới giai thừa **cân bằng hoàn hảo**
`vehicle_state` (driving 138 / parking 138) × `ASSISTANT_MODE` (quiet 92 /
balance 92 / proactive 92). Đây là thiết kế A/B thật sự — không bộ nào khác trả
lời được câu "chế độ proactive có làm người lái khó chịu khi đang chạy xe không".

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

## 4. Kiến trúc chung (cả ba task)

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

## 5. Khối 1 — Chuyển dataset (task 1)

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

Một chỗ phải chuẩn hoá: **2 trong 364 dòng viết tool call bằng
`action`/`parameters` thay vì `key`/`params`** (`vg_0064`, và dòng `Gọi điện`
trong nhóm happy). Cùng ngữ nghĩa, khác cách viết. Converter chấp nhận alias đã
biết rồi chuẩn hoá về `{module, key, params}`, nhưng **vẫn bắt buộc có `module`
và `key`** sau khi chuẩn hoá — không nới lỏng luật.

## 6. Khối 2 — Gán case (dùng chung cả ba task)

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

Khi chạy `assigned_case`, runner ghi **`case_run.json`** ra output dir để verifier
tự chứa, không phải mò ngược config trial.

Không dùng `transcript.json` cho phần structured. Lý do: `transcript.json` được
sinh bởi `fetch_conversation_artifact()` (`chat_eval.py:352`), và nhánh dự phòng
của hàm đó chỉ dựng lại `messages` gồm `role` + `content` — **mọi trường
`structuredExposure` bị rơi**. Verifier đọc `decision` từ đó sẽ luôn rỗng.

`case_run.json` gộp cả đầu vào lẫn quan sát, phát ra từ
`harbor_output_artifacts_from_result()` (`chat_eval.py:481`) nơi `result.transcript`
còn giữ nguyên `PlaygroundTurn.structured_exposure` (`types.py:101`):

```json
{
  "case_id": "vg_0137",
  "case": { "...bản ghi case đầy đủ..." },
  "observation": {
    "first_assistant_message": "Em chưa rõ anh chị muốn đến đâu ạ...",
    "first_user_message": "Dẫn giúp em tới chỗ đó với",
    "structured_exposure": [{"key": "decision", "value": "clarify_or_offer"}],
    "turn_count": 2
  }
}
```

### Script sinh recipe

Mở rộng `application/scripts/generate_application_job.py` (hoặc script chị em) để
sinh tích persona × case, kèm `.meta.json` ghi lại danh sách case đã chọn và seed.

## 7. Khối 3 — Bơm state (task 1 và task 3)

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

Khối này phục vụ **task 1 và task 3**. Task 2 không dùng vì bộ 2 không có cột state.

## 8. Khối 4 — Task folder (task 1)

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
      selector: decision
    - key: toolCalls
      selector: toolCalls
      format: json
```

Cơ chế `structuredExposure` đã có sẵn (`chatbot_task_config.py:64`), không cần schema mới.
`selector` là **dot-path thường**, không phải JSONPath — `lookup_path()` trong
`structured_exposure.py:8` chỉ tách chuỗi theo dấu chấm.

`maxTurns: 2` — đủ để quan sát câu hỏi làm rõ có hữu ích không, nhưng không cho
hội thoại trôi làm nhiễu phép đo.

## 9. Verifier (task 1)

`tests/test_state.py`, theo đúng hợp đồng của các task chat hiện có: đọc từ
`HARBOR_OUTPUT_DIR`, ghi `structured_output.json` vào `HARBOR_VERIFIER_DIR`,
ghi `reward.txt` 1/0.

Đầu vào: `case_run.json`, `transcript.json`, `user_feedback.json`.

**Neo thời điểm chấm: lượt trả lời đầu tiên của VITA.**

### Ba tầng chấm

1. **`decision_match`** — `observed_decision` vs `expected.decision`, 5 lớp.
   Nguồn `observed_decision`: ưu tiên field structured từ `structuredExposure`;
   không có thì LLM-judge phân loại từ reply. Ghi `decision_source` vào facet.

2. **`tool_call_match`** — so `module` + `key`. Không so `params` ở phiên bản đầu.

   Bất biến đã kiểm chứng trên dữ liệu thật: **58 case có tool call thì cả 58 đều
   là `execute`, và 301 case không phải `execute` đều rỗng.** `case_type` *không*
   dự đoán được điều này — 6 dòng unhappy vẫn có tool call (nhóm
   `vehicle_state_unavailable`: cảm biến không đọc được nhưng lệnh vẫn gửi đi
   được), và 8 dòng happy không có tool call nào (trả lời thuần hội thoại).
   Mỗi case nhiều nhất một tool call.

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

## 10. `reporting.json` (task 1)

`contextRules` khớp `contextType: error_recovery`, distributions nhóm theo:

- `error_type` — trả lời "hỏng ở nhóm lỗi nào"
- `subintent_code` — trả lời "hỏng ở subintent nào"
- `decision_match` × `case_integrity` — hai con số accuracy tách bạch
- `decision_source` — kiểm soát, để biết bao nhiêu phần trăm số liệu đến từ judge

Giữ nguyên hai contextRule `task_outcome` và `user_feedback` như các task chat khác.

## 11. Task 2 — `chat_vita-drive-multiturn-coverage`

Trạng thái: **đã dựng xong.** Verifier chấm bằng facet độ phủ + `lexical_topic_overlap`
(proxy từ vựng, không phải điểm) + self-report của persona. Chưa có LLM-judge.

Phát hiện khi convert: bộ này nhiễu nặng hơn mục 2 ghi. Ngoài dòng gán nhầm role,
nhiều seed là mảnh vụn nhận dạng giọng nói hoặc nằm dưới `sub_intent` không khớp
nội dung — `calendar_query` = `"gì"`, `source_queue` = `"usb"`, `calling` =
`"đây là dấu hiệu của bệnh gì"`. Luật chỉ bắt được `seed_quality = too_short`
(6/46); phần còn lại phải người đọc, nên converter xuất `seed_review.md`.

Trial = 1 persona × 1 conversation seed. 46 seed.

`input/cases.jsonl`: `{conversation_id, parent_intent, sub_intent, seed_user_turn,
reference_turn_count}`. Chỉ lấy **lượt user đầu tiên** làm seed. Persona tự dẫn dắt
các lượt sau và **không được đọc trước lượt assistant** trong dataset — nếu cho đọc
thì persona sẽ lái hội thoại theo đúng transcript và phép đo mất hết ý nghĩa.

`maxTurns: 6` — đủ cho hội thoại dài nhất trong bộ (6 lượt).

Không có ground truth, nên chấm ba mặt bằng judge + self-report:

| Mặt | Đo gì |
|---|---|
| `intent_adherence` | VITA có ở lại đúng `sub_intent` qua các lượt, hay trôi sang chuyện khác |
| `context_retention` | Từ lượt 2 trở đi, VITA có dùng lại thông tin persona đã nêu ở lượt trước |
| `turn_efficiency` | Số lượt tới khi persona thấy đạt mục tiêu |

`reference_turn_count` từ dataset chỉ là **mốc tham chiếu, không phải chuẩn đúng/sai**.
Transcript gốc cũng vậy: dùng để đối chiếu định tính, không dùng làm đáp án.

`reporting.json` nhóm theo `parent_intent` và `sub_intent` — đây là điểm ăn tiền
chính của task này: **đảm bảo phủ đủ 46 sub_intent** thay vì phó mặc persona tự
nghĩ chủ đề như `chat_vita-drive-assistant` đang làm.

Điều kiện tiên quyết bắt buộc:

- **Làm sạch dòng bị gán nhầm role.** Hội thoại `parking_arrival` có lượt `user`
  mang nội dung `"bạn đã đến nơi"`, `"sau 40 m"` — đó là thông báo dẫn đường của
  hệ thống. Đây là lỗi dán nhãn, không bắt được bằng luật, nên cần một bước
  review người trước khi convert.
- Chấp nhận giới hạn: 29/46 hội thoại chỉ có 2 lượt, nên tín hiệu
  `context_retention` mỏng. Không kết luận mạnh trên nhóm này.

Task này **không cần `sessionBody`** (bộ 2 không có cột state), nhưng dùng lại
goal context `assigned_case` ở khối 2.

## 12. Task 3 — `chat_vita-drive-assistant-mode-ab`

Trạng thái: **đã dựng xong.** Verifier ghi hai yếu tố thí nghiệm, `reply_char_count`,
và self-report của persona. Không chấm đúng/sai vì không có ground truth.

Converter đối chiếu chéo `subintent_code` và `intent_code` của workbook với bảng
taxonomy: cả 276 dòng khớp.

Trial = 1 persona × 1 case. 276 case.

**Đính chính so với nhận định trước đó: task này CÓ cần `sessionBody`.**
`vehicle_state` và `ASSISTANT_MODE` chính là state phải bơm vào request, nên khối 3
phục vụ cả task 1 lẫn task 3.

```yaml
sessionBody:
  vehicleState: ${case.state.vehicle_state}
  assistantMode: ${case.state.assistant_mode}
```

`maxTurns: 2`.

Không có ground truth. Chấm bằng judge + persona self-report:

| Mặt | Đo gì |
|---|---|
| `mode_appropriateness` | Độ dài và mức chủ động của phản hồi có khớp mode được đặt không |
| `driving_distraction` | Khi `vehicle_state = driving`, phản hồi có dài/rườm tới mức gây mất tập trung không |
| `user_feedback.overallExperienceRating` | Persona tự chấm trải nghiệm |

`reporting.json` cho ra **bảng chéo `ASSISTANT_MODE` × `vehicle_state`** — chính là
lưới A/B. Vì lưới cân bằng hoàn hảo (92/92/92 × 138/138) nên so sánh giữa các ô là
hợp lệ mà không cần cân lại trọng số.

Giới hạn phải ghi vào báo cáo: toàn bộ 276 dòng `source = generated`, `note` rỗng,
**chưa qua review người**. Kết luận rút ra chỉ nói về hành vi của VITA trước prompt
sinh máy, không đại diện cho người dùng thật.

## 13. Rủi ro

| Rủi ro | Mức | Xử lý |
|---|---|---|
| **8B không giữ nổi ràng buộc phủ định** | Cao | Xem mục riêng bên dưới |
| Persona phá ràng buộc đầu vào ở 152 case | Cao | Ràng buộc trong case brief + facet `case_integrity`; smoke run đo trước |
| LLM-judge phân loại lệch hệ thống | Trung bình | `decision_source` tách riêng; đo độ khớp judge vs structured trên tập có cả hai |
| Task 2/3 chấm hoàn toàn bằng judge | Trung bình | Không so sánh số của task 2/3 với task 1; báo cáo tách bạch |
| 1820 trial tốn kém | Trung bình | Chặn cửa bằng smoke run |
| Bộ 2 có dòng gán nhầm role | Trung bình | Review người trước khi convert |
| 14 cặp taxonomy đặt tay sai | Thấp | Converter fail cứng khi gặp subintent lạ |
| Dữ liệu kết nối thiết bị quá mỏng (3 dòng) | Thấp | Ghi nhận là giới hạn, không kết luận về nhóm này |

### Rủi ro 8B — điểm cần chú ý nhất

Model persona hoán đổi được bằng config, không phải sửa code: `persona_model.py:10`
lấy theo thứ tự `agents[].model_name` → `MATRIX_CHATBOT_PERSONA_MODEL` →
`MATRIX_PERSONA_MODEL` → `DEFAULT_PERSONA_MODEL`. Cắm 8B chỉ là đổi `model_name`
trong job recipe.

Nhưng thiết kế task 1 đặt lên persona hai **ràng buộc phủ định**:

- `omit_detail` (72 case): *đừng* bổ sung chi tiết đang thiếu
- `preserve_invalid_value` (80 case): *đừng* tự sửa giá trị sai

Ràng buộc phủ định là đúng loại chỉ dẫn mà model nhỏ hay bỏ qua nhất, và ở đây nó
đi ngược bản năng "trả lời cho tự nhiên, cho đủ ý". Nguy hiểm ở chỗ **hỏng thầm**:
persona nói một câu hoàn toàn hợp lý, VITA trả lời đúng theo câu đó, verifier chấm
sai — và không có dấu hiệu gì trong log.

Vì vậy tiêu chí nghiệm thu phải đo `case_integrity` **theo từng model**, không phải
một ngưỡng chung. Smoke run chạy hai lượt, 8B và một model mạnh hơn, trên cùng tập
case; hiệu số giữa hai tỉ lệ vi phạm nói cho ta biết 8B có dùng được không.

Nếu 8B không đạt, phương án dự phòng theo thứ tự ưu tiên:

1. **Phân hoá chính sách paraphrase theo `input_constraint`**: 212 case `none` cho
   persona diễn đạt tự do; 152 case bị ràng buộc thì phát gần nguyên văn. Giữ được
   phép đo độ bền ở phần lớn dataset, đánh đổi là mất nó ở nhóm lỗi.
2. Dùng model mạnh hơn riêng cho 152 case bị ràng buộc.
3. Chấp nhận và báo cáo kèm tỉ lệ `case_integrity` như một cột số liệu chính thức.

Không chọn trước phương án nào — để số liệu smoke run quyết.

## 14. Ngoài phạm vi

- So khớp `params` trong tool call.
- Template engine tổng quát cho `sessionBody`.
- Case-parametrized trial ở tầng `harbor_job_service`.
- Bổ sung dữ liệu cho nhóm điều khiển Wi-Fi / Bluetooth.
- Gộp hay so sánh trực tiếp số liệu giữa task 1 và task 2/3.
- Gửi PR ngược lên upstream — `application/tasks/README.md` ghi rõ repo đang không
  nhận task mới đóng góp từ cộng đồng. Cần mở issue hỏi trước nếu muốn.

## 15. Triển khai theo giai đoạn

Task 1 đi trước vì nó trả tiền cho khối 2 và khối 3 mà hai task sau dùng lại.

**Giai đoạn A — nền dùng chung**

1. Converter + bảng taxonomy 60 cặp → `cases.jsonl` commit vào repo
2. `sessionBody` overlay + test hồi quy chứng minh 206 case không đổi request
3. Goal context `assigned_case` + rẽ nhánh trong `runner.py` + artifact `case_run.json`

**Giai đoạn B — task 1**

4. Task folder + verifier 3 tầng + `reporting.json`
5. **Smoke run: ~20 case × 1 persona × 2 model (8B và một model mạnh hơn)** — cửa chặn
6. Sinh recipe 364 × 3–5 persona, chạy đầy đủ

**Giai đoạn C — task 3** ✅ dựng xong

7. ~~Converter bộ 3 + task folder + verifier~~
8. Chạy 276 case, xuất bảng chéo mode × vehicle_state — **chờ SUT + credential**

**Giai đoạn D — task 2** ✅ dựng xong

9. Review người trên `seed_review.md` — **chờ người làm**
10. ~~Converter bộ 2 + task folder + verifier~~
11. Chạy 46 seed — **chờ SUT + credential**

## 16. Tiêu chí nghiệm thu

**Nền dùng chung**

- Chạy lại 13 task chat hiện có, request body không đổi.

**Task 1**

- `cases.jsonl` có đúng 364 dòng, mọi `expected.decision` nằm trong 5 lớp, mọi
  `subintent_code` có trong `intent_taxonomy.json`.
- Smoke run: mọi trial sinh được `case_run.json` và `structured_output.json` hợp lệ,
  và `case_run.observation.structured_exposure` không rỗng khi SUT có trả `decision`.
- `case_integrity = violated` đo tách riêng cho `omit_detail` và
  `preserve_invalid_value`, **và tách riêng theo từng persona model**. Có số liệu
  đối chiếu 8B vs model mạnh hơn trước khi mở van chạy đầy đủ.
- Bảng phân rã `decision_match` theo `error_type` và theo `subintent_code` đọc được
  từ báo cáo job.

**Task 2**

- 46/46 sub_intent đều có ít nhất một trial hoàn tất.
- Không trial nào để persona nhìn thấy lượt assistant của dataset.

**Task 3**

- Bảng chéo 3 mode × 2 vehicle_state đủ 6 ô, mỗi ô có trial hoàn tất.
- Báo cáo ghi rõ giới hạn `source = generated, chưa review người`.

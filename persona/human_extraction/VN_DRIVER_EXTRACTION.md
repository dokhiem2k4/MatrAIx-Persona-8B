# Tài xế Việt Nam (người thật) → MatrAIx 1.290 chiều

Chuẩn thu thập persona từ tài xế Việt Nam thật, để dùng cho benchmark trợ lý trên xe
(`application/tasks/chat_vita-drive-assistant`).

Chuẩn máy đọc được: [`standards/vn_driver_persona_v1.json`](standards/vn_driver_persona_v1.json)
Kiểm tra: `scripts/validate_vn_driver_persona.py`

Quy tắc xác định, **không LLM** — giống hệt GSS / ConvAI2 / Afrobarometer. Câu trả lời mơ hồ
resolve về `null`, **không bao giờ đoán**.

## Vì sao cần

Khảo sát toàn bộ **541 persona** hiện có trong `persona/datasets/`:

| | |
|---|---|
| Độ phủ trung bình | 428,7 / 1.290 chiều (33,2%) |
| Dao động | 7 → 1.290 chiều, độ lệch chuẩn **390,5** |
| Giá trị ngoài enum | **6.626** / 238.528 lượt gán (2,78%), chạm 542/1.290 chiều |
| **Không lái được xe** | **475 / 541 persona (88%)** |

Bốn chiều thiết yếu cho một trợ lý trên xe thưa nhất kho:

| Chiều | Tỉ lệ điền |
|---|---|
| `att_electric_vehicles` | 13,9% |
| `topic_cars` | 20,9% |
| `att_self_driving_cars` | 21,8% |
| `skill_driving` | 31,4% |

Bốn chiều `cog_*` — schema tự khai là `personaYamlProbeFields`, quyết định độ dài câu, mức trang
trọng, độ kiên nhẫn và mức hoài nghi khi chấm điểm — chỉ điền 28,7–30,7%, và **rỗng hoàn toàn** ở
cả 3 persona dùng trong job `vita-full-3p9i` (138 hội thoại).

## Nguyên tắc

**1. Đủ và bằng nhau, không phải nhiều.**
Chuẩn vàng của repo là GSS: 75.699 người thật, khảo sát mã hoá đầy đủ, và vẫn chỉ grounded
~14,6 chiều mỗi persona. Chuẩn này yêu cầu **22 chiều Tier A**, không đuổi theo 1.290.

**2. Độ phủ phải đồng đều.**
Trong `vita-full-3p9i`, persona đầy hồ sơ nhất (632 chiều) chấm khắt nhất (6,87); persona thưa hơn
(229 chiều) chấm rộng tay nhất (7,63). Với n=3 đây mới là giả thuyết, nhưng đủ để thấy chênh lệch
độ phủ có thể lẫn vào điểm số. Mọi người trả lời **cùng một bộ câu hỏi**; validator chặn khi độ
lệch chuẩn vượt 3.

**3. Sàng lọc trước.**
`demo_driver_status` phải là `Daily driver` hoặc `Occasional driver`. Người không lái xe không
dùng để chấm trợ lý trên xe.

## Tier A — 22 chiều bắt buộc

| Nhóm | Chiều |
|---|---|
| Sàng lọc | `demo_driver_status` · `lstyle_commute_mode` |
| Nhân khẩu | `age_bracket` · `gender_identity` · `region` · `urbanicity` · `life_stage` · `socioeconomic_band` |
| Lái xe | `skill_driving` · `topic_cars` · `att_electric_vehicles` · `att_self_driving_cars` |
| Cách nói & chấm điểm | `cog_verbosity` · `cog_formality` · `cog_patience` · `cog_skepticism` |
| Thái độ | `tech_savviness` · `risk_tolerance` · `decision_style` |
| Ngôn ngữ | `lang_vietnamese` · `register` · `multilingualism` |

Câu hỏi tiếng Việt và nhãn lựa chọn cho từng chiều nằm trong file JSON chuẩn.

## Hai chỗ schema chưa diễn tả được

**`primary_language` không có "Vietnamese".** Enum chỉ có English/Mandarin/Spanish/Hindi/Arabic/
French/Portuguese/Bengali/Russian/Japanese/German/Swahili. **255 persona trong kho đang ghi giá trị
ngoài enum.**
→ Tạm thời: **để trống** `primary_language`, dùng `lang_vietnamese=Native` + `cult_vietnam=Native`.
→ Sửa đúng: thêm `Vietnamese` vào enum (không đổi số chiều, không đổi index).

**Không có chiều nào cho hệ xưng hô tiếng Việt.** `register` chỉ có Formal/Colloquial/Regional
dialect/Code-switching/Technical jargon. Trong `vita-full-3p9i`, persona lúc xưng "tôi", lúc "mình",
lúc "chị" — không nhất quán vì không chiều nào quy định. Đề xuất chiều mới `vn_address_register`
(anh/em, chị/em, cô-chú/con, bác/cháu, tôi/bạn, mình/bạn) — chi tiết trong file JSON.
→ Đây là **sửa schema**: `targetDimensions` 1290 → 1291, index mới phải cấp ở cuối để không xô lệch
quy ước `persona-bench-dim-{NNN}`.

## Quy trình

```python
from crosswalk_engine import apply_crosswalk
from postprocess_engine import load_schema, normalize
from crosswalks.vn_drivers import CROSSWALK          # cần viết mới

order, allowed = load_schema("persona/schema/dimensions.json")
observed, _, _ = apply_crosswalk(row, CROSSWALK, allowed)
fields = normalize([], order, allowed, observed=observed)   # -> 1.290 trường
```

```bash
# 1. chuẩn tài xế VN — Tier A, đủ điều kiện, độ phủ đồng đều
uv run python scripts/validate_vn_driver_persona.py --input vn_drivers/shard_00.jsonl.gz

# 2. hợp lệ với schema — phải 0 lỗi
uv run python persona/human_extraction/scripts/validate_extraction.py \
    --input vn_drivers/shard_00.jsonl.gz --schema persona/schema/dimensions.json
```

`provenance: observed` cho chiều có câu trả lời thật, `unobserved` cho phần còn lại.

## Cỡ mẫu

Tối thiểu **20** persona để bảng điểm theo persona có nghĩa; khuyến nghị **30**.
`vita-full-3p9i` chỉ có 3 persona — ở quy mô đó bảng theo persona chỉ để tham khảo.

## Soi kho hiện tại

```bash
uv run python scripts/validate_vn_driver_persona.py \
    --input 'persona/datasets/**/persona_*.yaml' --max-report 5
```

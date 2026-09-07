# Hoá đơn — dataset Vita Drive Agent (VN-Drives)

Lập ngày 2026-09-05. Đơn giá theo bảng giá công bố của từng model, áp vào số
token mà job thực sự ghi lại.

## Chi tiết

| Hạng mục | Job | Trial | Input | Cache | Output | Ghi nhận | Tính lại |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v1 · Stage 1 (OpenRouter, 3.5-lite) | 9 | 27 | 473,043 | 6,109 | 67,297 | $0.3085 | $0.3085 |
| v1 · Stage 1 chạy bù | 3 | 3 | 39,228 | 0 | 5,538 | $0.0256 | $0.0256 |
| v1 · Smoke | 1 | 1 | 42,895 | 24,115 | 359 | $0.0073 | $0.0073 |
| v1 · Stage 2 — 67/138 xong | 1 | 138 | 3,903,331 | 2,132,232 | 32,244 | $0.6759 | $0.6759 |
| v2 · Smoke (hỏng, Eco 500) | 1 | 1 | 0 | 0 | 0 | $0.0000 | $0.0000 |
| v2 · Stage 1 (Google, 3.1-lite) | 9 | 27 | 512,667 | 81,476 | 68,458 | $0.2125 | $0.2125 |
| v2 · Smoke | 1 | 1 | 51,025 | 8,110 | 486 | $0.0117 | $0.0117 |
| v2 · Stage 2 — dừng ở 29/138 | 1 | 138 | 236,924 | 77,102 | 2,065 | $0.0450 | $0.0450 |
| **Tổng** | | | | | | **$1.2864** | **$1.2864** |

Cột *Ghi nhận* là `cost_usd` trong `result.json`; cột *Tính lại* là token nhân
đơn giá. Hai cột khớp nhau, nên phép tính không có chỗ nào tự bịa.

## Đơn giá đã dùng

| Model | Input | Cache | Output |
| --- | ---: | ---: | ---: |
| `gemini-3.5-flash-lite` (v1, qua OpenRouter) | $0.30 / 1M | $0.03 / 1M | $2.50 / 1M |
| `gemini-3.1-flash-lite` (v2, Google trực tiếp) | $0.25 / 1M | $0.025 / 1M | $1.50 / 1M |

Đơn giá v1 đã được kiểm chứng ngược: $0.5313 + $0.0640 + $0.0806 = $0.6759,
đúng bằng số OpenRouter tự báo về. Đơn giá v2 kiểm chứng tương tự trên stage 1:
$0.1078 + $0.0020 + $0.1027 = $0.2125.

## Chia theo nhà cung cấp

| | Tiền |
| --- | ---: |
| OpenRouter (v1) | $1.0173 |
| Google AI Studio (v2) | $0.2692 |

## $1.2864 là SÀN, không phải số cuối

Trial hỏng không ghi cost dù nhà cung cấp vẫn tính tiền cho mọi lệnh gọi nó
thực hiện trước khi chết. Bằng chứng: sau lượt v1, số dư OpenRouter tụt từ
+$0.3206 xuống -$0.0883 mà **không job nào chạy trong khoảng đó** — $0.409 tiền
của các trial hỏng được tính chậm, gần gấp ba mức $0.14 ước lượng ban đầu.

Lượt v2 có 25 trial hỏng cùng kiểu. Nếu tỷ lệ tương tự thì hoá đơn thật cao hơn
bảng trên khoảng $0.1–$0.2.

Google AI Studio không trả trường `cost` trong `usage`, nên từ lượt v2 trở đi
con số duy nhất đối soát được là ở bảng điều khiển Google, không phải trong
repo.

## Đã mua được gì

| | |
| --- | --- |
| `data/vita-drive-agent-stimuli-3p9i.csv` | 828 stimuli, 9 intent, 3 persona (v1) |
| `data/vita-drive-agent-results-3p9i.csv` | **67** hội thoại có chấm điểm |
| `data/vita-drive-agent-results-3p9i.jsonl` | 67 hội thoại kèm transcript |
| `data/vita-drive-agent-v2-stimuli-3p9i.csv` | 828 stimuli sinh bởi persona đã cải thiện |

Bộ 138 hội thoại hoàn chỉnh **chưa có**. Cả hai lượt đều chết giữa chừng, và
không lần nào vì lỗi của pipeline: lượt v1 hết credit OpenRouter, lượt v2 gặp
lỗi 500 của server Vita.

## Vì sao lượt v2 dừng

Không phải server sập — `/health` trả `{"ok":true}` suốt. Thử tách bạch:

```
A. "Chuyển sang chế độ lái Eco" ngay lượt 1          → 500
B. hai lượt liên tiếp không nhắc Eco                 → 200, 200
C. lượt 1 bình thường (200), lượt 2 nhắc Eco         → 500
```

Mọi request chạm tới chế độ lái Eco đều 500, bất kể vị trí lượt hay trạng thái
session. Trong 29 trial đã chạy, 25 hỏng vì đúng lỗi này.

Điều đó cũng giải thích dữ liệu của lượt v1: câu
`"Bạn xác nhận muốn chuyển sang chế độ lái Eco chứ?"` lặp 56 lần trên toàn
dataset, và 29/67 hội thoại có agent lặp nguyên văn một câu trả lời. Agent
không cố chấp — nó hỏi lại mãi vì lệnh thực thi Eco luôn crash. Điểm trung bình
của nhóm hội thoại dính lặp là 3.14 so với 7.14 của nhóm sạch, nên bug này một
mình kéo tụt gần như toàn bộ điểm thấp trong dataset.

Sửa xong nhánh Eco thì chạy lại 138 trial mất khoảng **$1.12** và 30–40 phút.

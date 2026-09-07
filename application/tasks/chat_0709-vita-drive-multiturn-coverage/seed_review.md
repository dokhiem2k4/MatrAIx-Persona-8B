# Seed review — chat_0709-vita-drive-multiturn-coverage

Mỗi dòng là lượt user đầu tiên của một hội thoại, dùng làm mục tiêu giao cho persona.

`seed_quality = too_short` là thứ luật bắt được (6 / 46 seed). 
Thứ luật **không** bắt được là seed gán sai nhãn hoặc là nhiễu nhận dạng giọng nói —
phải người đọc. Cột **Duyệt** để trống, người review điền `ok` hoặc `loại`.

| case_id | subintent_code | từ | quality | seed | Duyệt |
|---|---|---|---|---|---|
| vm_0001 | `destination_poi` | 6 | ok | mua giùm ly cà phê sữa | |
| vm_0002 | `route_management` | 5 | ok | nhưng mà bây giờ ai | |
| vm_0003 | `traffic_eta` | 5 | ok | bao lâu nữa thì tới | |
| vm_0004 | `parking_arrival` | 4 | ok | bạn đã đến nơi | |
| vm_0005 | `local_travel_information` | 8 | ok | những nơi nổi tiếng ở huế là gì | |
| vm_0006 | `range_sufficiency` | 7 | ok | xe đó có đủ pin được không | |
| vm_0007 | `charger_search` | 11 | ok | bạn có thể tìm các trạm sạc gần đây được không | |
| vm_0008 | `ev_routing` | 5 | ok | ngày mai có mưa không | |
| vm_0009 | `charging_status` | 9 | ok | bây giờ xe của bạn đang mấy phần trăm | |
| vm_0010 | `calendar_query` | 1 | too_short | gì | |
| vm_0011 | `calendar_create_update_cancel` | 12 | ok | xe của bạn đang bị hỏng nè bị trục trặc mà tớ | |
| vm_0012 | `task_management` | 12 | ok | Thêm việc gửi báo cáo doanh số vào danh sách cần làm. | |
| vm_0013 | `contextual_reminder` | 3 | too_short | tôi khát nước | |
| vm_0014 | `climate` | 7 | ok | tại sao máy lạnh không giảm được | |
| vm_0015 | `seat_comfort` | 8 | ok | xe có massage lưng ở ghế 2 không | |
| vm_0016 | `doors_windows_trunk` | 8 | ok | làm thế nào để đóng cốp VF8 của | |
| vm_0017 | `lights_mirrors_wipers` | 18 | ok | bạn cho tôi hỏi là hai cái gương chiếu hậu thì gầm điện hay gặp tay ở bàn | |
| vm_0018 | `supported_vehicle_settings` | 6 | ok | phanh tái sinh ở mục nào | |
| vm_0019 | `calling` | 8 | ok | đây là dấu hiệu của của bệnh gì | |
| vm_0020 | `messaging` | 12 | ok | làm thế nào được cài đặt zalo với lại đọc ở trên | |
| vm_0021 | `contact_resolution` | 7 | ok | Tìm giúp tôi liên hệ anh Nam. | |
| vm_0022 | `content_discovery` | 2 | too_short | tìm phim | |
| vm_0023 | `playback_control` | 6 | ok | khi nào đến tạm dừng nhạc | |
| vm_0024 | `source_queue` | 1 | too_short | usb | |
| vm_0025 | `volume_audio_zone` | 7 | ok | tại sao em lại giảm âm lượng | |
| vm_0026 | `vehicle_status` | 5 | ok | thông báo trạng thái xe | |
| vm_0027 | `warning_explanation` | 9 | ok | cảnh báo chấm than là cảnh báo gì vậy | |
| vm_0028 | `diagnostics` | 3 | too_short | chẩn đoán xe | |
| vm_0029 | `maintenance_service` | 7 | ok | lịch trình bảo dưỡng dầu phanh xe | |
| vm_0030 | `vehicle_information` | 13 | ok | để mức phanh tái sinh cao trên VF6 có ảnh hưởng gì không | |
| vm_0031 | `vita_capabilities_usage` | 12 | ok | cho mình xin các tính năng mà bạn có thể giúp đỡ | |
| vm_0032 | `vita_preferences` | 4 | ok | trả lời ngắn gọn | |
| vm_0033 | `user_profile_account` | 10 | ok | tài khoản vinfast này được kích hoạt thời điểm nào | |
| vm_0034 | `device_service_connectivity` | 7 | ok | kết nối bluetooth với điện thoại iphone | |
| vm_0035 | `system_app_settings` | 12 | ok | làm cách nào để cập nhật ứng dụng phần mềm từ xa | |
| vm_0036 | `permissions_privacy_data` | 12 | ok | hướng dẫn các định vị để người thứ 3 không biết được | |
| vm_0037 | `vinfast_brand_products` | 11 | ok | xe điện vinfast có ra bàn xe bán cài điện không | |
| vm_0038 | `vinfast_sales_policies` | 6 | ok | giá xe vinfast là bao nhiêu | |
| vm_0039 | `vinfast_service_network` | 8 | ok | xưởng vinfast chủ nhật có làm việc không | |
| vm_0040 | `vingroup_corporate_information` | 5 | ok | tập đoàn vinfast giới thiệu | |
| vm_0041 | `vingroup_member_brands` | 5 | ok | giới thiệu tập đoàn vingroup | |
| vm_0042 | `web_search` | 6 | ok | giá vàng hôm nay bao nhiêu | |
| vm_0043 | `general_qa` | 7 | ok | tại sao bầu trời có màu xanh | |
| vm_0044 | `weather_news` | 6 | ok | thời tiết hôm nay thế nào | |
| vm_0045 | `verified_fact_qa` | 8 | ok | messi với donald trump vĩ đại hơn nè | |
| vm_0046 | `conversation_entertainment` | 3 | too_short | tôi buồn quá | |

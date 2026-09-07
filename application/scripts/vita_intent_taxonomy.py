"""Map Vietnamese subintent display labels to English identifiers.

The 46 pairs below the ``# --- from Vita Demo dataset ---`` marker come from the
``Dataset - Vita Demo`` workbook (``subintent_name`` -> ``subintent_code``,
``intent_code``). The remaining 14 exist only in the golden dataset and are
assigned here; they fall into two parent intents that the demo dataset does not
use: ``services_commerce`` and ``fallback_handling``.
"""

from __future__ import annotations


class UnknownSubintentError(KeyError):
    """Raised when a subintent label has no English identifier."""


SUBINTENT_BY_LABEL_VI: dict[str, tuple[str, str]] = {
    # --- from Vita Demo dataset ---
    "Bảo dưỡng/dịch vụ": ("maintenance_service", "my_car"),
    "Chẩn đoán": ("diagnostics", "my_car"),
    "Cài đặt hệ thống và ứng dụng": ("system_app_settings", "vita_profile_settings"),
    "Các thương hiệu thành viên Vingroup": ("vingroup_member_brands", "vinfast_vingroup_brands"),
    "Cửa/kính/cốp": ("doors_windows_trunk", "cabin_vehicle_control"),
    "Ghế và tiện nghi": ("seat_comfort", "cabin_vehicle_control"),
    "Giao thông và thời gian dự kiến đến nơi (ETA)": ("traffic_eta", "journey_navigation_places"),
    "Giá bán, chính sách và chương trình VinFast": ("vinfast_sales_policies", "vinfast_vingroup_brands"),
    "Giải thích cảnh báo": ("warning_explanation", "my_car"),
    "Gọi điện": ("calling", "communication_media"),
    "Hệ thống bán hàng và dịch vụ VinFast": ("vinfast_service_network", "vinfast_vingroup_brands"),
    "Hỏi đáp": ("general_qa", "general_qa_conversation"),
    "Hỏi đáp có nguồn kiểm chứng": ("verified_fact_qa", "general_qa_conversation"),
    "Hồ sơ và tài khoản người dùng": ("user_profile_account", "vita_profile_settings"),
    "Khả năng và cách sử dụng ViTa": ("vita_capabilities_usage", "vita_profile_settings"),
    "Kết nối thiết bị và dịch vụ": ("device_service_connectivity", "vita_profile_settings"),
    "Lập tuyến EV": ("ev_routing", "energy_charging"),
    "Lập và thay đổi tuyến": ("route_management", "journey_navigation_places"),
    "Nguồn/danh sách phát": ("source_queue", "communication_media"),
    "Nhắc theo thời gian, vị trí, hành trình hoặc trạng thái xe": ("contextual_reminder", "calendar_tasks"),
    "Nhắn tin": ("messaging", "communication_media"),
    "Phạm vi di chuyển": ("range_sufficiency", "energy_charging"),
    "Quyền truy cập, quyền riêng tư và dữ liệu": ("permissions_privacy_data", "vita_profile_settings"),
    "Thiết lập xe được hỗ trợ": ("supported_vehicle_settings", "cabin_vehicle_control"),
    "Thông tin Tập đoàn Vingroup": ("vingroup_corporate_information", "vinfast_vingroup_brands"),
    "Thông tin xe": ("vehicle_information", "my_car"),
    "Thông tin địa phương/du lịch": ("local_travel_information", "journey_navigation_places"),
    "Thương hiệu và sản phẩm VinFast": ("vinfast_brand_products", "vinfast_vingroup_brands"),
    "Thời tiết/tin tức": ("weather_news", "general_qa_conversation"),
    "Tra cứu": ("calendar_query", "calendar_tasks"),
    "Tra cứu Web": ("web_search", "general_qa_conversation"),
    "Trò chuyện và giải trí": ("conversation_entertainment", "general_qa_conversation"),
    "Trạng thái sạc": ("charging_status", "energy_charging"),
    "Trạng thái xe": ("vehicle_status", "my_car"),
    "Tìm nội dung": ("content_discovery", "communication_media"),
    "Tìm trạm sạc": ("charger_search", "energy_charging"),
    "Tìm điểm đến/POI": ("destination_poi", "journey_navigation_places"),
    "Tùy chọn tương tác với ViTa": ("vita_preferences", "vita_profile_settings"),
    "Tạo/sửa/hủy lịch": ("calendar_create_update_cancel", "calendar_tasks"),
    "Việc cần làm": ("task_management", "calendar_tasks"),
    "Xác định liên hệ": ("contact_resolution", "communication_media"),
    "Âm lượng/vùng âm thanh": ("volume_audio_zone", "communication_media"),
    "Điều hòa": ("climate", "cabin_vehicle_control"),
    "Điều khiển phát": ("playback_control", "communication_media"),
    "Đèn/gương/gạt mưa": ("lights_mirrors_wipers", "cabin_vehicle_control"),
    "Đỗ xe/đến nơi": ("parking_arrival", "journey_navigation_places"),
    # --- golden-only labels, identifiers assigned here ---
    "Mua sắm/thanh toán": ("shopping_payment", "services_commerce"),
    "Đặt chỗ/nhà hàng": ("restaurant_reservation", "services_commerce"),
    "Đặt dịch vụ xe": ("ride_service_booking", "services_commerce"),
    "Đặt món ăn": ("food_ordering", "services_commerce"),
    "Đặt vé/khách sạn": ("ticket_hotel_booking", "services_commerce"),
    "Hỏi sâu nối tiếp": ("followup_deep_dive", "general_qa_conversation"),
    "Hỗ trợ ra quyết định": ("decision_support", "general_qa_conversation"),
    "So sánh và gợi ý lựa chọn": ("comparison_recommendation", "general_qa_conversation"),
    "Tư vấn chuyên sâu": ("expert_consultation", "general_qa_conversation"),
    "Câu vô nghĩa/nhiễu nhận dạng": ("unintelligible_input", "fallback_handling"),
    "Cần thêm thông tin": ("needs_more_information", "fallback_handling"),
    "Yêu cầu mơ hồ/thiếu thông tin": ("ambiguous_request", "fallback_handling"),
    "Unsupported intent": ("unsupported_intent", "fallback_handling"),
    "Too many requests": ("rate_limited", "fallback_handling"),
}


def subintent_entry(label_vi: str) -> tuple[str, str]:
    """Return ``(subintent_code, parent_intent_code)`` for a Vietnamese label."""
    key = (label_vi or "").strip()
    try:
        return SUBINTENT_BY_LABEL_VI[key]
    except KeyError:
        raise UnknownSubintentError(
            "no English identifier for subintent label {!r}; add it to "
            "SUBINTENT_BY_LABEL_VI".format(key)
        ) from None

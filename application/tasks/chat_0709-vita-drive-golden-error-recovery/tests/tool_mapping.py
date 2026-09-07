"""Map the golden dataset's tool vocabulary onto the deployment's real tools.

The two vocabularies were written independently. ``GET /api/vehicle/tools``
lists 54 tools; the dataset names 56 ``module.key`` pairs. Only one string
matches literally (``web_search``), so a name-to-name table is the only way to
score the 58 cases that expect a tool call.

Three outcomes, and the third one matters most:

``mapped``          an equivalent tool exists, compare against it
``no_equivalent``   the deployment has no such capability at all. The case can
                    never pass, and that is a finding about the product's
                    surface area, not a failure of the assistant's judgement.
``unmapped``        not yet decided by a human -- never guessed silently
"""

from __future__ import annotations

NO_EQUIVALENT = "__no_equivalent__"

# key: "<module>.<key>" from the golden dataset
# value: the deployment tool name, or NO_EQUIVALENT
TOOL_BY_GOLDEN_CALL: dict[str, str] = {
    # --- climate -----------------------------------------------------------
    "climate.set_temperature": "set_hvac_temperature",
    "climate.increase_temperature": "set_hvac_temperature",
    "climate_control.set_temperature": "set_hvac_temperature",
    "climate_control.set_ac": "set_hvac_power",
    "seat_comfort.driver_seat_heater": "set_seat_heating",
    # --- cabin / body ------------------------------------------------------
    "doors_windows_trunk.open_trunk": "set_tailgate_position",
    "vehicle_control.window_control": "set_window_position",
    "lights_control.high_beam": "set_headlight_mode",
    # The deployment locks doors but cannot open or close one.
    "doors_windows_trunk.close_rear_door": NO_EQUIVALENT,
    # --- media / audio -----------------------------------------------------
    "audio.set_volume": "set_media_volume",
    "media.play": "play_youtube_media",
    "media.search_music": "play_youtube_media",
    "media.switch_source": NO_EQUIVALENT,
    # --- connectivity / profile -------------------------------------------
    "bluetooth.connect_device": "set_bluetooth",
    "user_profile.switch_profile": "set_active_user_profile",
    # --- navigation --------------------------------------------------------
    "navigation.set_route": "open_google_maps_route",
    "navigation.ev_route": "open_google_maps_route",
    "navigation.compare_routes": "open_google_maps_route",
    "navigation.search_poi": "lookup_place_info",
    "navigation.search_charger": "lookup_place_info",
    "navigation.search_nearby_parking": "lookup_place_info",
    "navigation.search_nearby_alternatives": "lookup_place_info",
    "poi.search_detail": "lookup_place_info",
    "local_info.query_poi_info": "lookup_place_info",
    # --- vehicle state reads ----------------------------------------------
    "navigation.calculate_range_sufficiency": "get_vehicle_state",
    "battery.check_charging_status": "get_vehicle_state",
    "vehicle.get_remaining_range": "get_vehicle_state",
    "vehicle_info.get_manufacturing_year": "get_vehicle_state",
    # --- lookup ------------------------------------------------------------
    "web.web_search": "web_search",
    "weather.get_weather": "web_search",
    "information_service.get_verified_info": "web_search",
    "knowledge.abs_system_explanation": "web_search",
    "vinfast_info.query_product_variants": "web_search",
    "vinfast_sales.get_vehicle_price": "web_search",
    "vinfast_service_network.find_nearest_showroom": "web_search",
    "vingroup_brands.get_brand_info": "web_search",
    "vingroup_info.corporate_information": "web_search",
    "vingroup_info.get_corporate_information": "web_search",
    # --- capabilities the deployment simply does not have ------------------
    "booking.search_flights": NO_EQUIVALENT,
    "food_ordering.order_food": NO_EQUIVALENT,
    "payment.make_payment": NO_EQUIVALENT,
    "reservation.book_table": NO_EQUIVALENT,
    "vehicle_service.booking": NO_EQUIVALENT,
    "calendar.create_event": NO_EQUIVALENT,
    "calendar.query_events": NO_EQUIVALENT,
    "task_management.add_task": NO_EQUIVALENT,
    "reminder.create_contextual_reminder": NO_EQUIVALENT,
    "reminder.create_location_based": NO_EQUIVALENT,
    "phone.make_call": NO_EQUIVALENT,
    "messaging.send_message": NO_EQUIVALENT,
    "contacts.search_by_name": NO_EQUIVALENT,
    "diagnostics.run_brake_system_check": NO_EQUIVALENT,
    "maintenance.schedule_service": NO_EQUIVALENT,
    "system_settings.set_screen_brightness": NO_EQUIVALENT,
    "preferences.set_voice": NO_EQUIVALENT,
    "privacy.clear_search_history": NO_EQUIVALENT,
}


def golden_call_id(call: dict) -> str:
    """``module.key`` for one expected tool call."""
    return "{}.{}".format(
        str(call.get("module") or "").strip(), str(call.get("key") or "").strip()
    )


def map_expected_tools(expected_calls) -> tuple[set[str], list[str], list[str]]:
    """Return ``(deployment tool names, no_equivalent ids, unmapped ids)``."""
    names: set[str] = set()
    missing: list[str] = []
    unknown: list[str] = []
    for call in expected_calls or ():
        if not isinstance(call, dict):
            continue
        cid = golden_call_id(call)
        target = TOOL_BY_GOLDEN_CALL.get(cid)
        if target is None:
            unknown.append(cid)
        elif target == NO_EQUIVALENT:
            missing.append(cid)
        else:
            names.add(target)
    return names, missing, unknown

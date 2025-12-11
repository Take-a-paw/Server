from dataclasses import dataclass
from typing import Dict

from app.core.error_handler import error_response
from app.schemas.error_schema import ErrorResponse


@dataclass(frozen=True)
class RecordError:
    status: int
    code: str
    reason: str

    def to_dict(self, path: str) -> Dict:
        return {
            "success": False,
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "timeStamp": "...",
            "path": path,
        }


RECORD_ERRORS: Dict[str, RecordError] = {
    # Walk list
    "WALK_LIST_401_1": RecordError(401, "WALK_LIST_401_1", "Authorization 헤더가 필요합니다."),
    "WALK_LIST_401_2": RecordError(401, "WALK_LIST_401_2", "Authorization 헤더 형식이 잘못되었거나 토큰이 유효하지 않습니다."),
    "WALK_LIST_400_1": RecordError(400, "WALK_LIST_400_1", "pet_id 쿼리 파라미터는 필수입니다."),
    "WALK_LIST_400_2": RecordError(400, "WALK_LIST_400_2", "start_date와 end_date는 'YYYY-MM-DD' 형식이어야 합니다."),
    "WALK_LIST_400_3": RecordError(400, "WALK_LIST_400_3", "start_date는 end_date보다 이후일 수 없습니다."),
    "WALK_LIST_403_1": RecordError(403, "WALK_LIST_403_1", "해당 반려동물의 산책 기록을 조회할 권한이 없습니다."),
    "WALK_LIST_404_1": RecordError(404, "WALK_LIST_404_1", "해당 사용자를 찾을 수 없습니다."),
    "WALK_LIST_404_2": RecordError(404, "WALK_LIST_404_2", "요청하신 반려동물을 찾을 수 없습니다."),
    "WALK_LIST_500_1": RecordError(500, "WALK_LIST_500_1", "산책 목록을 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."),

    # Walk detail
    "WALK_DETAIL_401_1": RecordError(401, "WALK_DETAIL_401_1", "Authorization 헤더가 필요합니다."),
    "WALK_DETAIL_401_2": RecordError(401, "WALK_DETAIL_401_2", "Authorization 헤더 형식이 잘못되었거나 토큰이 유효하지 않습니다."),
    "WALK_DETAIL_400_1": RecordError(400, "WALK_DETAIL_400_1", "include_points 파라미터 값이 올바르지 않습니다."),
    "WALK_DETAIL_403_1": RecordError(403, "WALK_DETAIL_403_1", "해당 산책 기록을 조회할 권한이 없습니다."),
    "WALK_DETAIL_404_1": RecordError(404, "WALK_DETAIL_404_1", "해당 사용자를 찾을 수 없습니다."),
    "WALK_DETAIL_404_2": RecordError(404, "WALK_DETAIL_404_2", "요청하신 산책 세션을 찾을 수 없습니다."),
    "WALK_DETAIL_500_1": RecordError(500, "WALK_DETAIL_500_1", "산책 상세 정보를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."),

    # Photo list
    "PHOTO_LIST_401_1": RecordError(401, "PHOTO_LIST_401_1", "Authorization 헤더가 필요합니다."),
    "PHOTO_LIST_401_2": RecordError(401, "PHOTO_LIST_401_2", "Authorization 헤더 형식이 잘못되었거나 토큰이 유효하지 않습니다."),
    "PHOTO_LIST_400_1": RecordError(400, "PHOTO_LIST_400_1", "start_date와 end_date는 'YYYY-MM-DD' 형식이어야 합니다."),
    "PHOTO_LIST_400_2": RecordError(400, "PHOTO_LIST_400_2", "start_date는 end_date보다 이후일 수 없습니다."),
    "PHOTO_LIST_400_3": RecordError(400, "PHOTO_LIST_400_3", "pet_id 쿼리 파라미터는 필수입니다."),
    "PHOTO_LIST_403_1": RecordError(403, "PHOTO_LIST_403_1", "해당 반려동물의 사진첩을 조회할 권한이 없습니다."),
    "PHOTO_LIST_404_1": RecordError(404, "PHOTO_LIST_404_1", "해당 사용자를 찾을 수 없습니다."),
    "PHOTO_LIST_404_2": RecordError(404, "PHOTO_LIST_404_2", "요청하신 반려동물을 찾을 수 없습니다."),
    "PHOTO_LIST_500_1": RecordError(500, "PHOTO_LIST_500_1", "사진첩을 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."),

    # Activity stats
    "ACTIVITY_401_1": RecordError(401, "ACTIVITY_401_1", "Authorization 헤더가 필요합니다."),
    "ACTIVITY_401_2": RecordError(401, "ACTIVITY_401_2", "Authorization 헤더 형식이 잘못되었거나 토큰이 유효하지 않습니다."),
    "ACTIVITY_400_1": RecordError(400, "ACTIVITY_400_1", "pet_id 쿼리 파라미터는 필수입니다."),
    "ACTIVITY_400_2": RecordError(400, "ACTIVITY_400_2", "period는 'day', 'week', 'month', 'all' 중 하나여야 합니다."),
    "ACTIVITY_400_3": RecordError(400, "ACTIVITY_400_3", "date, start_date, end_date는 'YYYY-MM-DD' 형식이어야 합니다."),
    "ACTIVITY_400_4": RecordError(400, "ACTIVITY_400_4", "start_date는 end_date보다 이후일 수 없습니다."),
    "ACTIVITY_403_1": RecordError(403, "ACTIVITY_403_1", "해당 반려동물의 활동 기록을 조회할 권한이 없습니다."),
    "ACTIVITY_404_1": RecordError(404, "ACTIVITY_404_1", "해당 사용자를 찾을 수 없습니다."),
    "ACTIVITY_404_2": RecordError(404, "ACTIVITY_404_2", "요청하신 반려동물을 찾을 수 없습니다."),
    "ACTIVITY_500_1": RecordError(500, "ACTIVITY_500_1", "활동 통계를 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."),

    # Recent activities
    "RECENT_ACT_401_1": RecordError(401, "RECENT_ACT_401_1", "Authorization 헤더가 필요합니다."),
    "RECENT_ACT_401_2": RecordError(401, "RECENT_ACT_401_2", "Authorization 헤더 형식이 잘못되었거나 토큰이 유효하지 않습니다."),
    "RECENT_ACT_403_1": RecordError(403, "RECENT_ACT_403_1", "해당 반려동물의 활동 기록을 조회할 권한이 없습니다."),
    "RECENT_ACT_404_1": RecordError(404, "RECENT_ACT_404_1", "해당 사용자를 찾을 수 없습니다."),
    "RECENT_ACT_404_2": RecordError(404, "RECENT_ACT_404_2", "요청하신 반려동물을 찾을 수 없습니다."),
    "RECENT_ACT_500_1": RecordError(500, "RECENT_ACT_500_1", "최근 활동을 조회하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."),
}


def record_error(code: str, path: str):
    err = RECORD_ERRORS.get(code)
    if not err:
        return error_response(500, "RECORD_500", "서버 내부 오류가 발생했습니다.", path)
    return error_response(err.status, err.code, err.reason, path)


def _examples_for_codes(path: str, codes: Dict[str, RecordError]) -> Dict:
    return {
        code: {"value": err.to_dict(path)}
        for code, err in codes.items()
    }


# Swagger response presets per endpoint
RECORD_WALK_LIST_RESPONSES = {
    400: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks", {
        "WALK_LIST_400_1": RECORD_ERRORS["WALK_LIST_400_1"],
        "WALK_LIST_400_2": RECORD_ERRORS["WALK_LIST_400_2"],
        "WALK_LIST_400_3": RECORD_ERRORS["WALK_LIST_400_3"],
    })}}},
    401: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks", {
        "WALK_LIST_401_1": RECORD_ERRORS["WALK_LIST_401_1"],
        "WALK_LIST_401_2": RECORD_ERRORS["WALK_LIST_401_2"],
    })}}},
    403: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks", {
        "WALK_LIST_403_1": RECORD_ERRORS["WALK_LIST_403_1"],
    })}}},
    404: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks", {
        "WALK_LIST_404_1": RECORD_ERRORS["WALK_LIST_404_1"],
        "WALK_LIST_404_2": RECORD_ERRORS["WALK_LIST_404_2"],
    })}}},
    500: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks", {
        "WALK_LIST_500_1": RECORD_ERRORS["WALK_LIST_500_1"],
    })}}},
}

RECORD_WALK_DETAIL_RESPONSES = {
    400: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks/{walk_id}", {
        "WALK_DETAIL_400_1": RECORD_ERRORS["WALK_DETAIL_400_1"],
    })}}},
    401: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks/{walk_id}", {
        "WALK_DETAIL_401_1": RECORD_ERRORS["WALK_DETAIL_401_1"],
        "WALK_DETAIL_401_2": RECORD_ERRORS["WALK_DETAIL_401_2"],
    })}}},
    403: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks/{walk_id}", {
        "WALK_DETAIL_403_1": RECORD_ERRORS["WALK_DETAIL_403_1"],
    })}}},
    404: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks/{walk_id}", {
        "WALK_DETAIL_404_1": RECORD_ERRORS["WALK_DETAIL_404_1"],
        "WALK_DETAIL_404_2": RECORD_ERRORS["WALK_DETAIL_404_2"],
    })}}},
    500: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/walks/{walk_id}", {
        "WALK_DETAIL_500_1": RECORD_ERRORS["WALK_DETAIL_500_1"],
    })}}},
}

RECORD_PHOTO_LIST_RESPONSES = {
    400: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/photos", {
        "PHOTO_LIST_400_1": RECORD_ERRORS["PHOTO_LIST_400_1"],
        "PHOTO_LIST_400_2": RECORD_ERRORS["PHOTO_LIST_400_2"],
        "PHOTO_LIST_400_3": RECORD_ERRORS["PHOTO_LIST_400_3"],
    })}}},
    401: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/photos", {
        "PHOTO_LIST_401_1": RECORD_ERRORS["PHOTO_LIST_401_1"],
        "PHOTO_LIST_401_2": RECORD_ERRORS["PHOTO_LIST_401_2"],
    })}}},
    403: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/photos", {
        "PHOTO_LIST_403_1": RECORD_ERRORS["PHOTO_LIST_403_1"],
    })}}},
    404: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/photos", {
        "PHOTO_LIST_404_1": RECORD_ERRORS["PHOTO_LIST_404_1"],
        "PHOTO_LIST_404_2": RECORD_ERRORS["PHOTO_LIST_404_2"],
    })}}},
    500: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/photos", {
        "PHOTO_LIST_500_1": RECORD_ERRORS["PHOTO_LIST_500_1"],
    })}}},
}

RECORD_STATS_RESPONSES = {
    400: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/stats", {
        "ACTIVITY_400_1": RECORD_ERRORS["ACTIVITY_400_1"],
        "ACTIVITY_400_2": RECORD_ERRORS["ACTIVITY_400_2"],
        "ACTIVITY_400_3": RECORD_ERRORS["ACTIVITY_400_3"],
        "ACTIVITY_400_4": RECORD_ERRORS["ACTIVITY_400_4"],
    })}}},
    401: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/stats", {
        "ACTIVITY_401_1": RECORD_ERRORS["ACTIVITY_401_1"],
        "ACTIVITY_401_2": RECORD_ERRORS["ACTIVITY_401_2"],
    })}}},
    403: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/stats", {
        "ACTIVITY_403_1": RECORD_ERRORS["ACTIVITY_403_1"],
    })}}},
    404: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/stats", {
        "ACTIVITY_404_1": RECORD_ERRORS["ACTIVITY_404_1"],
        "ACTIVITY_404_2": RECORD_ERRORS["ACTIVITY_404_2"],
    })}}},
    500: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/stats", {
        "ACTIVITY_500_1": RECORD_ERRORS["ACTIVITY_500_1"],
    })}}},
}

RECORD_RECENT_RESPONSES = {
    400: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/recent", {})}}},
    401: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/recent", {
        "RECENT_ACT_401_1": RECORD_ERRORS["RECENT_ACT_401_1"],
        "RECENT_ACT_401_2": RECORD_ERRORS["RECENT_ACT_401_2"],
    })}}},
    403: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/recent", {
        "RECENT_ACT_403_1": RECORD_ERRORS["RECENT_ACT_403_1"],
    })}}},
    404: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/recent", {
        "RECENT_ACT_404_1": RECORD_ERRORS["RECENT_ACT_404_1"],
        "RECENT_ACT_404_2": RECORD_ERRORS["RECENT_ACT_404_2"],
    })}}},
    500: {"model": ErrorResponse, "content": {"application/json": {"examples": _examples_for_codes("/api/v1/record/recent", {
        "RECENT_ACT_500_1": RECORD_ERRORS["RECENT_ACT_500_1"],
    })}}},
}

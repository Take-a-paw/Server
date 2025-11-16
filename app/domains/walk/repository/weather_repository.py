from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import threading

# 간단한 메모리 기반 캐시 (실제 운영에서는 Redis 등을 사용 권장)
_weather_cache: Dict[Tuple[float, float], Dict] = {}
_cache_lock = threading.Lock()
CACHE_TTL_SECONDS = 600  # 10분


class WeatherRepository:
    def __init__(self):
        pass

    def get_cached_weather(
        self, lat: float, lng: float
    ) -> Optional[Dict]:
        """캐시된 날씨 정보 조회"""
        cache_key = (round(lat, 4), round(lng, 4))  # 소수점 4자리까지 반올림
        
        with _cache_lock:
            if cache_key in _weather_cache:
                cached_data = _weather_cache[cache_key]
                fetched_at = cached_data.get("fetched_at")
                
                if fetched_at:
                    age_seconds = (datetime.utcnow() - fetched_at).total_seconds()
                    if age_seconds < CACHE_TTL_SECONDS:
                        return cached_data
                    else:
                        # 캐시가 오래되었지만 반환 (is_stale=True로 표시)
                        cached_data["cache_age_seconds"] = int(age_seconds)
                        cached_data["is_stale"] = True
                        return cached_data
        
        return None

    def set_cached_weather(
        self, lat: float, lng: float, weather_data: Dict
    ) -> None:
        """날씨 정보 캐시 저장"""
        cache_key = (round(lat, 4), round(lng, 4))
        
        with _cache_lock:
            _weather_cache[cache_key] = {
                **weather_data,
                "fetched_at": datetime.utcnow(),
                "cache_age_seconds": 0,
                "is_stale": False,
            }


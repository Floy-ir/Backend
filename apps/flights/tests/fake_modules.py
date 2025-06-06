# fake modules for tests
from apps.airlines import interfaces as airlines_interfaces
from apps.accounts import interfaces as accounts_interfaces
from apps.flight_crawler import interfaces as flight_crawler_interfaces
from libs.redis_client import interfaces as cache_interfaces
from apps.event_bus import interfaces as event_bus_interfaces
from utils.date_time import interfaces as date_time_interfaces
from typing import Dict, Any


class FakeAirlineService(airlines_interfaces.AbstractAirlineService):
    def get_airlines(self, request: airlines_interfaces.AirlineListReq) -> Dict[str, airlines_interfaces.AirlineDTO]:
        results = {}
        
        for airline in request.uid_list:
            if airline:  # Only add non-None airline UIDs
                results[airline] = airlines_interfaces.AirlineDTO(
                    uid=airline,
                    name=f"Airline {airline}",
                    image=None,  # Test expects None for image
                )

        return results

    def get_airline(self, uid: str) -> airlines_interfaces.AirlineDTO:
        return airlines_interfaces.AirlineDTO(
            uid=uid,
            name=f"Airline {uid}",
            image=None,  # Test expects None for image
        )

    def get_airline_by_name(self, name: str) -> airlines_interfaces.AirlineDTO:
        return airlines_interfaces.AirlineDTO(
            uid=name,  # Test expects the name as the UID
            name=f"Airline {name}",
            image=None,  # Test expects None for image
        )

    def upload_image(self, request: airlines_interfaces.UploadImageReq) -> airlines_interfaces.AirlineDTO:
        return airlines_interfaces.AirlineDTO(
            uid=request.uid,
            name=f"Airline {request.uid}",
            image=None,  # Test expects None for image
        )


class FakeCacheService(cache_interfaces.ICacheService):
    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> Any:
        return self.cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 3600):
        self.cache[key] = value

    def delete(self, key: str):
        del self.cache[key]

    def clear(self):
        self.cache.clear()

    def exists(self, key: str) -> bool:
        pass

    def expire(self, key: str, seconds: int) -> bool:
        pass

    def flush_db(self) -> None:
        pass

    def get_json(self, key: str) -> Any:
        pass

    def incr(self, key: str, amount: int = 1) -> int:
        pass

    def mget(self, keys: list[str]) -> list[Any]:
        pass

    def mget_json(self, keys: list[str]) -> list[Any]:
        pass

    def mset(self, mapping: dict[str, Any]) -> None:
        pass

    def set_json(self, key: str, value: Any, ttl: int = 3600) -> None:
        pass

    def ttl(self, key: str) -> int:
        pass


class FakeFlightCrawlerService(flight_crawler_interfaces.AbstractFlightCrawler):
    def get_websites(self, request: flight_crawler_interfaces.GetWebsitesRequest) -> Dict[str, flight_crawler_interfaces.WebsiteDTO]:
        results = {}
        
        for website in request.uid_list:
            if website:  # Only add non-None website UIDs
                results[website] = flight_crawler_interfaces.WebsiteDTO(
                    uid=website,
                    name=f"Website {website}",
                    name_fa=f"Website {website}",
                    logo=None,  # Test expects None for logo
                )
        
        return results

    def crawl_scheduled_flights(self, days_ahead: int = None) -> None:
        pass

    def upload_image(self, request: flight_crawler_interfaces.UploadImageRequest) -> flight_crawler_interfaces.WebsiteDTO:
        return flight_crawler_interfaces.WebsiteDTO(
            uid=request.uid,
            name=f"Website {request.uid}",
            name_fa=f"Website {request.uid}",
            logo=None,  # Test expects None for logo
        )
    


class FakeEventBus(event_bus_interfaces.AbstractEventBus):
    def emit(self, caller: accounts_interfaces.Session, event_or_command: event_bus_interfaces.EventOrCommand):
        pass

    def subscribe(self, caller: accounts_interfaces.Session, match_string: str, listener: event_bus_interfaces.AbstractEventListener) -> object:
        pass



class FakeDateTime(date_time_interfaces.AbstractDateTime):
    def get_current_timestamp(self) -> int:
        return 10

    def get_timestamp_of_interval_ahead(self, day_interval: int) -> int:
        return 10 + day_interval * 10
    
    def get_start_timestamp_of_day_from_today(self, timedelta_days: int) -> int:
        return 10 + timedelta_days * 10
    
    def get_end_of_day_timestamp_from_today(self, timedelta_days: int) -> int:
        return 10 + timedelta_days * 10
    
    def convert_timestamp_to_date(self, timestamp: int, date_format: str) -> str:
        pass
    
    def convert_timestamp_to_jalali_date(self, timestamp: int, separator: str = '-') -> str:
        pass
    
    def convert_date_time_to_timestamp(self, time: str, date: str) -> int:
        pass
    
    def convert_iso_datetime_to_timestamp(self, datetime_str: str) -> int:
        pass
    
    def convert_datetime_string_to_timestamp(self, datetime_str: str, format_str: str) -> int:
        pass
    
    def miladi_to_shamsi(self, date_str, separator: str = '-') -> str:
        pass

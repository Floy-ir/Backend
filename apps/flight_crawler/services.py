from typing import Dict
import time
import logging
from apps.flight_city import interfaces as flight_city_interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.file_storage import interfaces as file_storage_interfaces
from apps.accounts import interfaces as account_interfaces
from libs.redis_client import interfaces as cache_interfaces
from utils.http_requester import interfaces as http_requester_interfaces
from apps.flight_crawler.models import Website
from . import interfaces


IS_FINISHED_FIELD = 'is_finished_field'

logger = logging.getLogger(__name__)


class FlightCrawlerService(interfaces.AbstractFlightCrawler):
    def __init__(self,
                 claim: account_interfaces.Session,
                 date_time_utils: date_time_interfaces.AbstractDateTime,
                 flight_city_service: flight_city_interfaces.AbstractFlightCityService,
                 file_storage_service: file_storage_interfaces.AbstractFileStorageService,
                 http_requester: http_requester_interfaces.AbstractHTTPRequester,
                 cache_service: cache_interfaces.ICacheService,
                 ):
        self.claim = claim
        self.date_time = date_time_utils
        self.flight_city_service = flight_city_service
        self.file_storage = file_storage_service
        self.cache_service = cache_service
        self.http_requester = http_requester

    def crawl(self, request: interfaces.CrawlRequest) -> interfaces.CrawlResponse:
        pass

    def upload_image(self, request: interfaces.UploadImageRequest) -> interfaces.WebsiteDTO:
        logger.debug(f"Request: {request}")

        try:
            website = Website.objects.get(uid=request.uid)
        except Website.DoesNotExist:
            logger.debug(f"Airline with uid {request.uid} doesn't exist")
            raise interfaces.WebsiteNotFound()

        try:
            image_link = self.file_storage.upload_files(
                caller=self.claim,
                request=file_storage_interfaces.UploadRequest(
                    uid=request.uid,
                    files=[request.image]
                )
            )
        except file_storage_interfaces.InternalFileStorageNotAvailable as e:
            logger.debug(f"Error: {e}")
            raise interfaces.FileStorageNotAvailable()

        website.image = image_link
        website.save()
        result = self._convert_website_to_dataclass(website)

        self.cache_service.set_json(request.uid, result)

        logger.debug(f"Result: {result}")
        return result

    def get_websites(self, request: interfaces.GetWebsitesRequest) -> Dict[str, interfaces.WebsiteDTO]:
        logger.info(f"request: {request}")
        cached_website = self.cache_service.mget_json(request.uid_list)

        result = {}
        missing_uids = []

        for uid, website in zip(request.uid_list, cached_website):
            if website is None:
                missing_uids.append(uid)
                continue

            result[uid] = self._convert_dict_to_website_dataclass(website)

        if not missing_uids:
            return result

        logger.debug(f"Cache miss for airlines with uids: {','.join(missing_uids)}")
        websites = Website.objects.filter(uid__in=missing_uids)

        for website in websites:
            result[website.uid] = self._convert_website_to_dataclass(website)
            # Cache the result for future use
            self.cache_service.set_json(website.uid, result[website.uid])

        return result

    def _fetch_flights(self, source: Website, search_params: interfaces.CrawlRequest):
        method = source.request_method
        headers = source.request_headers
        request_structure = source.request_payload_structure

        formatted_params = self._format_input_params(request_structure, search_params)

        has_search_id = request_structure[IS_FINISHED_FIELD]

        all_flights = []
        is_continued = True
        response_data = None

        while is_continued:
            if method == "get":
                response = self.http_requester.get(url=source.base_url, headers=headers, params=formatted_params)
            elif method == "post":
                response = self.http_requester.post(url=source.base_url, headers=headers, json=formatted_params)
            else:
                logger.warning(f"Unsupported request type for source {source.name}")
                raise interfaces.UnsupportedRequestType()

            if response.status_code != 200:
                raise interfaces.UnsuccessfulRequest()

            response_data = response.content_json

            is_continued = not (
                self._extract_nested_value(data=response_data, path=request_structure[IS_FINISHED_FIELD]))

            if not has_search_id:
                all_flights.extend(self._extract_nested_value(response_data, request_structure["flights_list"]))

            if is_continued:
                time.sleep(2)

        is_continued = request_structure.get("search_id_request_structure", {}) != {}
        while is_continued:
            search_id_request_structure = request_structure["search_id_request_structure"]
            search_id = self._extract_nested_value(response_data, search_id_request_structure["search_id"])
            if search_id_request_structure["method"] == 'get':
                if request_structure["way"] == "params":
                    response = self.http_requester.get(
                        url=search_id_request_structure["url"],
                        headers=headers,
                        params=formatted_params,
                    )
                else:
                    response = self.http_requester.get(
                        url=search_id_request_structure["url"] + search_id,
                        headers=headers,
                    )
            else:
                response = self.http_requester.post(
                    url=request_structure["search_id_request_structure"]["url"],
                    headers=headers,
                    json=formatted_params
                )

            if response.status_code != 200:
                raise interfaces.UnsuccessfulRequest()

            response_data = response.content_json
            all_flights.extend(self._extract_nested_value(response_data, request_structure["flights_list"]))
            is_continued = not(self._extract_nested_value(data=response_data, path=request_structure[IS_FINISHED_FIELD]))
            if is_continued:
                all_flights.extend(self._extract_nested_value(response_data, request_structure["flights_list"]))
                time.sleep(2)

        return all_flights

    def _format_input_params(self, request_structure, search_params: interfaces.CrawlRequest):
        def set_nested_value(target, keys, value):
            for key in keys[:-1]:
                target = target.setdefault(key, {})
            target[keys[-1]] = value

        formatted_params = {}

        mappings = request_structure.get("mappings", {})
        static_fields = request_structure.get("static_fields", {})
        date_fields = request_structure.get("date_fields", {})

        for key, value in search_params.as_dict().items():
            if key in mappings:
                path = mappings[key].split(".")

            if key == "departure_timestamp":
                if date_fields["is_jalali"]:
                    value = self.date_time.convert_timestamp_to_jalali_date(
                        timestamp=value,
                        separator=date_fields["seperator"]
                    )
                else:
                    value = self.date_time.convert_timestamp_to_date(
                        timestamp=value,
                        date_format=date_fields["seperator"]
                    )

            set_nested_value(formatted_params, path, value)

        # Process static fields
        for key, value in static_fields.items():
            path = key.split(".")
            set_nested_value(formatted_params, path, value)

        return formatted_params

    def _parse_response(self, parsing_rules, response_data):
        try:
            if not parsing_rules:
                return {"error": "No parsing rules defined"}

            flights_path = parsing_rules.get("flights_path", "")
            fields_map = parsing_rules.get("fields", {})

            flights_data = self._extract_nested_value(response_data, flights_path)

            parsed_flights = []
            if isinstance(flights_data, list):
                for flight in flights_data:
                    parsed_flights.append({
                        key: self._extract_nested_value(flight, value.split("."))
                        for key, value in fields_map.items()
                    })

            return parsed_flights
        except Exception as e:
            return {"error": f"Parsing error: {e}"}

    @staticmethod
    def _extract_nested_value(data, path):
        """Extracts a nested value from a dictionary using a dot-separated path that may contain list indices."""
        keys = path.split(".")

        for key in keys:
            if key.isdigit():  # If key is a number, treat it as a list index
                index = int(key)
                if isinstance(data, list) and 0 <= index < len(data):
                    data = data[index]
                else:
                    return None  # Index out of bounds
            elif isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None  # Key does not exist

        return data

    @staticmethod
    def _convert_website_to_dataclass(website: Website) -> interfaces.WebsiteDTO:
        return interfaces.WebsiteDTO(
            uid=website.uid,
            name=website.name,
            name_fa=website.name_fa,
            logo=website.logo,
        )

    @staticmethod
    def _convert_dict_to_website_dataclass(website: dict) -> interfaces.WebsiteDTO:
        return interfaces.WebsiteDTO(
            uid=website["uid"],
            name=website["name"],
            name_fa=website["name_fa"],
            logo=website["logo"],
        )

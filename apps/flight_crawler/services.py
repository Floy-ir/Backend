from typing import Dict
import logging
import requests
from apps.flight_city import interfaces as flight_city_interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.file_storage import interfaces as file_storage_interfaces
from apps.accounts import interfaces as account_interfaces
from libs.redis_client import interfaces as cache_interfaces
from apps.flight_crawler.models import Website
from . import interfaces


logger = logging.getLogger(__name__)


class FlightCrawlerService(interfaces.AbstractFlightCrawler):
    def __init__(self,
                 claim: account_interfaces.Session,
                 date_time_utils: date_time_interfaces.AbstractDateTime,
                 flight_city_service: flight_city_interfaces.AbstractFlightCityService,
                 file_storage_service: file_storage_interfaces.AbstractFileStorageService,
                 cache_service: cache_interfaces.ICacheService,
                 ):
        self.claim = claim
        self.date_time = date_time_utils
        self.flight_city_service = flight_city_service
        self.file_storage = file_storage_service
        self.cache_service = cache_service

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


    @staticmethod
    def _fetch_flights(source: Website, search_params):
        method = source.request_method
        headers = source.request_headers
        request_structure = source.request_payload_structure

        formatted_params = FlightCrawlerService._format_input_params(request_structure, search_params)

        # Perform API request
        try:
            if request_structure["type"] == "query":
                response = requests.get(source.base_url, headers=headers, params=formatted_params)
            elif request_structure["type"] == "body":
                response = requests.post(source.base_url, headers=headers, json=formatted_params)
            else:
                return {"error": f"Unsupported request type {request_structure['type']}"}

            if response.status_code == 200:
                return FlightCrawlerService._parse_response(source.response_parsing_rules, response.json())
            return {"error": f"Failed request. Status: {response.status_code}"}
        except requests.RequestException as e:
            return {"error": str(e)}

    @staticmethod
    def _format_input_params(request_structure, search_params):
        mappings = request_structure.get("mappings", {})
        return {mappings[key]: value for key, value in search_params.items() if key in mappings}

    @staticmethod
    def _parse_response(parsing_rules, response_data):
        try:
            if not parsing_rules:
                return {"error": "No parsing rules defined"}

            flights_path = parsing_rules.get("flights_path", "")
            fields_map = parsing_rules.get("fields", {})

            flights_data = FlightCrawlerService._extract_nested_value(response_data, flights_path.split("."))

            parsed_flights = []
            if isinstance(flights_data, list):
                for flight in flights_data:
                    parsed_flights.append({
                        key: FlightCrawlerService._extract_nested_value(flight, value.split("."))
                        for key, value in fields_map.items()
                    })

            return parsed_flights
        except Exception as e:
            return {"error": f"Parsing error: {e}"}

    @staticmethod
    def _extract_nested_value(data, keys):
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
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

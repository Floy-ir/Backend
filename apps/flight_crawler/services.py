from typing import Dict

import requests
from apps.flight_city import interfaces as flight_city_interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.file_storage import interfaces as file_storage_interfaces
from apps.flight_crawler.models import Website
from . import interfaces


class FlightCrawlerService(interfaces.AbstractFlightCrawler):
    def __init__(self,
                 date_time_utils: date_time_interfaces.AbstractDateTime,
                 flight_city_service: flight_city_interfaces.AbstractFlightCityService,
                 file_storage_service: file_storage_interfaces.AbstractFileStorageService
                 ):

        self.date_time = date_time_utils
        self.flight_city_service = flight_city_service
        self.file_storage_service = file_storage_service

    def crawl(self, request: interfaces.CrawlRequest) -> interfaces.CrawlResponse:
        pass

    def upload_photo(self, request: interfaces.UploadPhotoRequest) -> interfaces.Website:
        pass

    def get_websites(self, request: interfaces.GetWebsitesRequest) -> Dict[str, Website]:
        pass


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
                return FlightCrawlerService._parse_response(source.parsing_rules, response.json())
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

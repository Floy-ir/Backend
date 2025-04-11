from typing import Dict, List
from uuid import uuid4
import time
import logging
from apps.flight_city import interfaces as flight_city_interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.file_storage import interfaces as file_storage_interfaces
from apps.event_bus import interfaces as event_bus_interfaces 
from apps.airlines import interfaces as airline_interfaces
from apps.accounts import interfaces as account_interfaces
from libs.redis_client import interfaces as cache_interfaces
from utils.http_requester import interfaces as http_requester_interfaces
from apps.flight_crawler.models import Website, WebsiteRoute
from . import interfaces


# Request structure constants
IS_FINISHED_FIELD = 'is_finished_field'
FLIGHTS_PATH = 'flights_path'
API_URL = 'api_url'
HEADERS = 'headers'
WAY = 'way'
PARAMS = 'params'
SEARCH_ID_REQUEST_STRUCTURE = 'search_id_request_structure'
SEARCH_ID = 'search_id'
URL = 'url'
METHOD = 'method'

# Request method constants
GET_METHOD = 'get'
POST_METHOD = 'post'

# Config constants
CITY_MAPPING = 'city_mapping'
ORIGIN = 'origin'
DESTINATION = 'destination'

# Request structure field constants
MAPPINGS = 'mappings'
STATIC_FIELDS = 'static_fields'
DATE_FIELDS = 'date_fields'
IS_JALALI = 'is_jalali'
SEPARATOR = 'seperator'

# Response parsing constants
FIELDS = 'fields'

logger = logging.getLogger(__name__)


class FlightCrawlerService(interfaces.AbstractFlightCrawler):
    def __init__(self,
                 claim: account_interfaces.Session,
                 date_time_utils: date_time_interfaces.AbstractDateTime,
                 event_bus: event_bus_interfaces.AbstractEventBus,
                 flight_city_service: flight_city_interfaces.AbstractFlightCityService,
                 file_storage_service: file_storage_interfaces.AbstractFileStorageService,
                 http_requester: http_requester_interfaces.AbstractHTTPRequester,
                 cache_service: cache_interfaces.ICacheService,
                 airline_service: airline_interfaces.AbstractAirlineService,
                 max_adults: int = 2,
                 ):
        self.claim = claim
        self.date_time = date_time_utils
        self.flight_city_service = flight_city_service
        self.airline_service = airline_service
        self.event_bus = event_bus
        self.file_storage = file_storage_service
        self.cache_service = cache_service
        self.http_requester = http_requester
        self.max_adults = max_adults

    def crawl_scheduled_flights(self, from_days_ahead: int, to_days_ahead: int) -> None:
        try:
            cities = self.flight_city_service.get_cities()

            for i in range(from_days_ahead, to_days_ahead): 
                target_timestamp = self.date_time.get_timestamp_of_interval_ahead(day_interval=i)
                
                for first_city in cities.results:
                    for sec_city in first_city.destinations:
                        origin = first_city.value 
                        destination = sec_city.value 
                        crawl_uid = str(uuid4())
                        flights = [] 
                        logger.info(f"Processing route: {origin} -> {destination}")

                        try:
                            for adult_cnt in range(1, self.max_adults): 
                                request = interfaces.CrawlRequest(
                                    origin=origin,
                                    destination=destination,
                                    departure_timestamp=target_timestamp,
                                    adult=adult_cnt,
                                    child=0,
                                    infant=0
                                )
                                
                                flights.extend(self._crawl(request=request))
                            
                            self.event_bus.emit(
                                caller=self.claim,
                                event_or_command=event_bus_interfaces.EventOrCommand(
                                    uid=str(uuid4()),
                                    event_type='CRAWLED_FLIGHT',
                                    payload=interfaces.CrawlResponse(
                                        uid=crawl_uid,
                                        crawl_timestamp=target_timestamp,
                                        origin=origin,
                                        destination=destination,
                                        results=flights
                                    )
                                )
                            )
                            
                        except Exception as e:
                            logger.info(f"crawled flights for {origin} -> {destination} error ==>> {e}")
                            continue                  
                    
        except Exception as e:
            logger.error(f"Error in crawl_scheduled_flights: {str(e)}")
            raise

    def _crawl(self, request: interfaces.CrawlRequest) -> List[interfaces.Flight]:
        """
        Initiates the crawling process for flights based on the provided request parameters.
        
        This method filters supported websites for the given origin and destination, and then fetches flights for each of these websites. The fetched flights are aggregated and returned as a list.
        
        Args:
            request (interfaces.CrawlRequest): An object containing the crawl request parameters such as origin, destination, departure timestamp, and passenger details.
            
        Returns:
            List[interfaces.Flight]: A list of Flight objects representing the crawled flights.
        """
        try:
            flights = [] 
            websites_route = WebsiteRoute.objects.filter(
                origin=request.origin,
                destination=request.destination,
                is_supported=True
            )

            for website in websites_route: 
                flights.extend(self._fetch_flights(source=website, search_params=request))
                
            return flights
        except Exception as e: 
            logger.error(f"Error in _crawl: {str(e)}")
            raise e

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
            self.cache_service.set_json(website.uid, result[website.uid])

        return result

    def _fetch_flights(self, source: WebsiteRoute, search_params: interfaces.CrawlRequest) -> List[interfaces.Flight]:
        method = source.website.request_method
        headers = source.website.request_headers
        request_structure = source.website.request_payload_structure
        response_parsing_rules = source.website.response_parsing_rules

        if source.config and CITY_MAPPING in source.config:
            city_mapping = source.config[CITY_MAPPING]
            if ORIGIN in city_mapping:
                search_params.origin = city_mapping[ORIGIN].get(search_params.origin, search_params.origin)
            if DESTINATION in city_mapping:
                search_params.destination = city_mapping[DESTINATION].get(search_params.destination, search_params.destination)

        formatted_params = self._format_inputs(request_structure, search_params)

        has_search_id = request_structure[IS_FINISHED_FIELD]

        all_flights = []
        is_continued = True
        response_data = None

        while is_continued:
            if method == GET_METHOD:
                response = self.http_requester.get(
                    url=request_structure[API_URL], 
                    headers=request_structure[HEADERS],
                    params=formatted_params
                    )
            elif method == POST_METHOD:
                response = self.http_requester.post(
                    url=request_structure[API_URL], 
                    headers=request_structure[HEADERS], 
                    json=formatted_params
                )
            else:
                logger.warning(f"Unsupported request type for source {source.name}")
                raise interfaces.UnsupportedRequestType()

            if response.status_code != 200:
                raise interfaces.UnsuccessfulRequest()

            response_data = response.content_json

            is_continued = not (
                self._extract_nested_value(data=response_data, path=request_structure[IS_FINISHED_FIELD]))

            if not has_search_id:
                all_flights.extend(self._extract_nested_value(response_data, request_structure[FLIGHTS_PATH]))

            if is_continued:
                time.sleep(3)

        is_continued = request_structure.get(SEARCH_ID_REQUEST_STRUCTURE, {}) != {}
        while is_continued:
            search_id_request_structure = request_structure[SEARCH_ID_REQUEST_STRUCTURE]
            search_id = self._extract_nested_value(response_data, search_id_request_structure[SEARCH_ID])
            if search_id_request_structure[METHOD] == GET_METHOD:
                if request_structure[WAY] == PARAMS:
                    response = self.http_requester.get(
                        url=search_id_request_structure[URL],
                        headers=request_structure[HEADERS],
                        params=formatted_params,
                    )
                else:
                    response = self.http_requester.get(
                        url=search_id_request_structure[URL] + search_id,
                        headers=request_structure[HEADERS],
                    )
            else:
                response = self.http_requester.post(
                    url=request_structure[SEARCH_ID_REQUEST_STRUCTURE][URL],
                    headers=headers,
                    json=formatted_params
                )

            if response.status_code != 200:
                raise interfaces.UnsuccessfulRequest()

            response_data = response.content_json
            all_flights.extend(self._extract_nested_value(response_data, request_structure[FLIGHTS_PATH]))
            is_continued = not(self._extract_nested_value(data=response_data, path=request_structure[IS_FINISHED_FIELD]))
            if is_continued:
                all_flights.extend(self._extract_nested_value(response_data, request_structure[FLIGHTS_PATH]))
                time.sleep(2)

        result = self._parse_response(website=source, flights=all_flights, parser=response_parsing_rules, request=search_params)
        logger.info(f"result: {result}")
        return result

    def _format_inputs(self, request_structure, search_params: interfaces.CrawlRequest):
        def set_nested_value(target, keys, value):
            for key in keys[:-1]:
                target = target.setdefault(key, {})
            target[keys[-1]] = value

        formatted_params = {}

        mappings = request_structure.get(MAPPINGS, {})
        static_fields = request_structure.get(STATIC_FIELDS, {})
        date_fields = request_structure.get(DATE_FIELDS, {})

        for key, value in search_params.as_dict().items():
            if key in mappings:
                path = mappings[key].split(".")

            if key == "departure_timestamp":
                if date_fields[IS_JALALI]:
                    value = self.date_time.convert_timestamp_to_jalali_date(
                        timestamp=value,
                        separator=date_fields[SEPARATOR]
                    )
                else:
                    value = self.date_time.convert_timestamp_to_date(
                        timestamp=value,
                        date_format=date_fields[SEPARATOR]
                    )

            set_nested_value(formatted_params, path, value)

        # Process static fields
        for key, value in static_fields.items():
            path = key.split(".")
            set_nested_value(formatted_params, path, value)

        return formatted_params

    def _parse_response(self, source: WebsiteRoute, flights, parser, request) -> List[interfaces.Flight]:
        fields_map = parser.get(FIELDS, {})
        airline_value_map = parser.get("airline_mapping", None)
        parsed_flights = []
        for raw_flight in flights:
            try:
                parsed_dict = {}

                for field_name, json_path in fields_map.items():
                    value = self._extract_nested_value(raw_flight, json_path)
                    parsed_dict[field_name] = value

                parsed_dict["airline"] = self.airline_service.get_airline_by_name(airline_value_map[parsed_dict["airline"]]).uid

                parsed_dict["provider_uid"] = str(source.website.uid)

                if not source.website.redirect_url_config: 
                    redirect_url_departure_date = parsed_dict["departure_timestamp"]

                if source.website.request_payload_structure.get(DATE_FIELDS, {}).get(IS_JALALI, False):
                    parsed_dict["departure_timestamp"] = self.date_time.convert_timestamp_to_jalali_date(
                        timestamp=parsed_dict["departure_timestamp"],
                        separator=source.website.request_payload_structure[DATE_FIELDS][SEPARATOR]
                    )
                else:
                    parsed_dict["departure_timestamp"] = self.date_time.convert_timestamp_to_date(
                        timestamp=parsed_dict["departure_timestamp"],
                        date_format=source.website.request_payload_structure[DATE_FIELDS][SEPARATOR]
                    )

                if source.website.redirect_url_config:
                    date_fields = source.website.redirect_url_config[DATE_FIELDS]
                    if date_fields[IS_JALALI]:
                        redirect_url_departure_date = self.date_time.convert_timestamp_to_jalali_date(
                            timestamp=parsed_dict["departure_timestamp"],
                            separator=date_fields[SEPARATOR]
                        )
                    else:
                        redirect_url_departure_date = self.date_time.convert_timestamp_to_date(
                            timestamp=parsed_dict["departure_timestamp"],
                            date_format=date_fields[SEPARATOR]
                        )

           
                flight_id = self._extract_nested_value(raw_flight, parser.get("flight_id_path", "id"))
                city_mapping = source.website.redirect_url_config.get(CITY_MAPPING, {})
                origin_code = city_mapping.get(request.origin, request.origin)
                dest_code = city_mapping.get(request.destination, request.destination)

                url_params = {
                    "flight_id": flight_id,
                    "origin": origin_code,
                    "destination": dest_code,
                    "departure_date": redirect_url_departure_date,
                }
                
                parsed_dict["base_redirect_url"] = source.website.redirect_url_template.format(**url_params)
                if request.adult == 1: 
                    if source.website.one_adult_url_template:
                        parsed_dict["one_adult_redirect_url"] = source.website.one_adult_url_template.format(**url_params)
                    else:
                        parsed_dict["one_adult_redirect_url"] = None 

                elif request.adult == 2: 
                    if source.website.two_adult_url_template:
                        parsed_dict["two_adult_redirect_url"] = source.website.two_adult_url_template.format(**url_params)
                    else:
                        parsed_dict["two_adult_redirect_url"] = None 
                
                try:
                    parsed_flight = interfaces.Flight(**parsed_dict)
                    parsed_flights.append(parsed_flight)
                except Exception as e:
                    logger.warning(f"Error parsing flight: {e}, raw data: {parsed_dict}")
            except Exception as e:
                logger.warning(f"Error parsing response: {e}, source: {source.__dict__}, flights: {flights}")
                continue 

        return parsed_flights    

    @staticmethod
    def _extract_nested_value(data: dict, path: str):
        """Extracts a nested value from a dictionary using a dot-separated path that may contain list indices."""
        keys = path.split(".")

        for key in keys:
            if key.isdigit():
                index = int(key)
                if isinstance(data, list) and 0 <= index < len(data):
                    data = data[index]
                else:
                    return None
            elif isinstance(data, dict) and key in data:
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

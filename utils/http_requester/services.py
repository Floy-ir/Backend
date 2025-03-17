from typing import List, Tuple
from urllib.parse import urljoin
import requests
import logging
from . import interfaces

logger = logging.getLogger(__name__)


class RequestsHTTPRequester(interfaces.AbstractHTTPRequester):

    def request(self, method: str, base_addresses: List[str], path: str, data=None, retry_statuses: List[int] = None,
                parse_response_as_json: bool = True, timeout: Tuple[int, int] = (10, 301),
                **kwargs) -> interfaces.RequesterResponse:
        logger.info(f"method:{method},base_addresses:{base_addresses},path:{path},data:{data},"
                    f"retry_statuses:{retry_statuses},parse_response_as_json:{parse_response_as_json},"
                    f"timeout:{timeout},kwargs:{kwargs}")
        if retry_statuses is None:
            retry_statuses = [500, 502, 503, 504]
        for base_address in base_addresses:
            the_url = urljoin(base_address, path)
            logger.debug(f"the url is: url: {the_url}")

            try:
                response = requests.request(
                    method=method,
                    url=the_url,
                    data=data,
                    json=kwargs.get("json", None),
                    timeout=timeout,
                    params=kwargs.get("params", None),
                    headers=kwargs.get("headers", None),
                )
            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    'Connection error occurred while requesting URL: %s. Error details: %s',
                    the_url,
                    str(e)
                )
                raise interfaces.ConnectionErrorException(f'Connection error occurred. URL: {the_url}')

            except requests.exceptions.Timeout as e:
                logger.warning(f'Timeout occurred while requesting {the_url}: {e}')
                raise interfaces.TimeOutException(f'Request timed out {the_url}')

            if response.status_code not in retry_statuses:
                break
        else:
            raise interfaces.RequestException(
                status_code=500,
                message="None of base addresses returned a non to-retry response"
            )

        content_json = None
        if parse_response_as_json:
            try:
                content_json = response.json()
            except requests.exceptions.JSONDecodeError as e:
                logger.debug(e)
        result = interfaces.RequesterResponse(
            status_code=response.status_code,
            content_bytes=response.content,
            content_json=content_json,
        )
        logger.info(f"result:{result}")
        return result

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request('PATCH', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('PUT', *args, **kwargs)

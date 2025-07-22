from typing import List, Tuple
import requests
import logging
from . import interfaces
import time

logger = logging.getLogger(__name__)


class RequestsHTTPRequester(interfaces.AbstractHTTPRequester):

    def request(self, method: str, url: str, data=None, retry_statuses: List[int] = None,
                parse_response_as_json: bool = True, timeout: Tuple[int, int] = (10, 30),
                max_retries: int = 3, retry_delay: int = 5, **kwargs) -> interfaces.RequesterResponse:
        logger.info(f"method:{method},url:{url},data:{data},retry_statuses:{retry_statuses},"
                    f"parse_response_as_json:{parse_response_as_json},timeout:{timeout},kwargs:{kwargs}")

        if retry_statuses is None:
            retry_statuses = [500, 502, 503, 504]

        logger.debug(f"Requesting URL: {url}")

        try:
            response = requests.request(
                method=method,
                url=url,
                data=data,
                json=kwargs.get("json", None),
                timeout=timeout,
                params=kwargs.get("params", None),
                headers=kwargs.get("headers", None),
            )
        except requests.exceptions.ConnectionError as e:
            logger.warning(f'Connection error occurred while requesting URL: {url}. Error details: {e}')
            raise interfaces.ConnectionErrorException(f'Connection error occurred. URL: {url}')
        except requests.exceptions.Timeout as e:
            logger.warning(f'Timeout occurred while requesting {url}: {e}')
            raise interfaces.TimeOutException(f'Request timed out {url}')

        # Handle 202 Accepted status with polling
        if response.status_code == 202:
            location = response.headers.get('Location')
            if location:
                # If we have a location header, poll that endpoint
                retry_count = 0
                while retry_count < max_retries:
                    time.sleep(retry_delay)
                    try:
                        poll_response = requests.get(
                            url=location,
                            timeout=timeout,
                            headers=kwargs.get("headers", None),
                        )
                        if poll_response.status_code == 200:
                            response = poll_response
                            break
                    except Exception as e:
                        logger.warning(f'Error polling status endpoint: {e}')
                    retry_count += 1
            else:
                # If no location header, implement simple retry
                retry_count = 0
                while retry_count < max_retries:
                    time.sleep(retry_delay)
                    logger.debug(f"error for {retry_count} st time")
                    try:
                        retry_response = requests.request(
                            method=method,
                            url=url,
                            data=data,
                            json=kwargs.get("json", None),
                            timeout=timeout,
                            params=kwargs.get("params", None),
                            headers=kwargs.get("headers", None),
                        )
                        if retry_response.status_code == 200:
                            response = retry_response
                            break
                    except Exception as e:
                        logger.warning(f'Error retrying request: {e}')
                    retry_count += 1

        if response.status_code in retry_statuses:
            raise interfaces.RequestException(
                status_code=response.status_code,
                message="Response returned with a retryable status code"
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
        return result

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request('PATCH', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('PUT', *args, **kwargs)

from typing import List, Tuple, Optional
import requests
import logging
from . import interfaces
import time
import gc
from utils.proxy_manager.interfaces import ProxyRequest, ProxyResponse

logger = logging.getLogger(__name__)


class RequestsHTTPRequester(interfaces.AbstractHTTPRequester):
    def __init__(self):
        # Create a session for connection pooling
        self.session = requests.Session()
        # Configure session for better memory management
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
        })
        # Set connection pool limits
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3,
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def __del__(self):
        """Cleanup session when object is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()

    def request(self, method: str, url: str, data=None, retry_statuses: List[int] = None,
                parse_response_as_json: bool = True, timeout: Tuple[int, int] = (10, 30),
                max_retries: int = 3, retry_delay: int = 5, use_proxy: bool = False, 
                proxy_manager=None, **kwargs) -> interfaces.RequesterResponse:
        logger.info(f"method:{method},url:{url},data:{data},retry_statuses:{retry_statuses},"
                    f"parse_response_as_json:{parse_response_as_json},timeout:{timeout},use_proxy:{use_proxy},kwargs:{kwargs}")

        if retry_statuses is None:
            retry_statuses = [500, 502, 503, 504]

        logger.debug(f"Requesting URL: {url}")

        # If proxy is enabled and proxy_manager is provided, use proxy rotation
        if use_proxy and proxy_manager:
            return self._make_proxy_request(method, url, data, timeout, parse_response_as_json, kwargs, proxy_manager)

        # Regular request without proxy
        try:
            response = self.session.request(
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
                        poll_response = self.session.get(
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
                        retry_response = self.session.request(
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
            proxy_used=None,
            response_time=response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0.0
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

    def delete(self, *args, **kwargs):
        return self.request('DELETE', *args, **kwargs)

    def _make_proxy_request(self, method: str, url: str, data=None, timeout: Tuple[int, int], 
                           parse_response_as_json: bool, kwargs: dict, proxy_manager) -> interfaces.RequesterResponse:
        """Make a request using proxy rotation"""
        try:
            # Create proxy request
            proxy_request = ProxyRequest(
                url=url,
                method=method,
                headers=kwargs.get("headers", None),
                params=kwargs.get("params", None),
                json=kwargs.get("json", None),
                timeout=max(timeout),
                retry_count=3
            )
            
            # Make request through proxy manager
            proxy_response = proxy_manager.make_request(proxy_request)
            
            # Parse JSON if requested
            content_json = None
            if parse_response_as_json and proxy_response.content_json:
                content_json = proxy_response.content_json
            
            # Return response in the expected format
            return interfaces.RequesterResponse(
                status_code=proxy_response.status_code,
                content_bytes=proxy_response.content_bytes,
                content_json=content_json,
                proxy_used=f"{proxy_response.proxy_used.host}:{proxy_response.proxy_used.port}" if proxy_response.proxy_used else None,
                response_time=proxy_response.response_time
            )
            
        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            raise interfaces.RequestException(
                status_code=500,
                message=f"Proxy request failed: {str(e)}"
            )

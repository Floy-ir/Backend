import abc
from typing import List, Tuple
from pydantic import BaseModel
from libs.exceptions import ServiceExceptions


class RequesterResponse(BaseModel):
    status_code: int
    content_bytes: bytes = None
    content_json: object = None


class HttpRequesterBaseException(ServiceExceptions):
    pass


class TimeOutException(HttpRequesterBaseException):
    def __init__(self, message):
        super().__init__(message)


class ConnectionErrorException(HttpRequesterBaseException):
    def __init__(self, message):
        super().__init__(message)


class RequestException(HttpRequesterBaseException):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(status_code, message)


class AbstractHTTPRequester(abc.ABC):

    def request(self, method: str, url: str, data=None, retry_statuses: List[int] = None,
                parse_response_as_json: bool = True, timeout: Tuple[int, int] = (10, 301), **kwargs) -> RequesterResponse:
        """requests to base_addresses in turn and returns the first non to-retry response.

        Args:
            method (str): one of 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'
            url (List[str]): the url of request
            data (any, optional): This is body of the request; any serializable object. Defaults to None.
            retry_statuses (List[int], optional): if request did not succeed or the response status code was one of these, the requester will try next base address. defaults to [500, 502, 503, 504]
            parse_response_as_json (bool, optional): if True, the requester will parse response in case of 200 or 201 response. Defaults to True.
            timeout (Tuple[int, int], optional): connect timeout and read timeout respectively

        Raises:
            RequestException: None of base addresses returned a non to-retry response

        Returns:
            RequesterResponse: status code and content_bytes always exist. but content_json sometimes exists.
        """
        raise NotImplementedError

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

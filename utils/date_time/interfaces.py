from abc import ABC, abstractmethod


class AbstractDateTime(ABC):
    @abstractmethod
    def get_current_timestamp(self) -> int:
        """return current timestamp in second"""
        raise NotImplementedError

    def get_start_timestamp_of_day_from_today(self, timedelta_days: int) -> int:
        """
        return first timestamp corresponds to a day that is timedelta_days ahead of today.
        """
        raise NotImplementedError

    def get_end_of_day_timestamp_from_today(self, timedelta_days: int) -> int:
        """
        return end timestamp corresponds to a day that is timedelta_days ahead of today.
        """
        raise NotImplementedError

    def convert_timestamp_to_date(self, timestamp: int) -> str:
        """
        return date of a timestamp in format yyyy-mm-dd
        """
        raise NotImplementedError

    def convert_date_time_to_timestamp(self, time: str, date: str) -> int:
        """
            get time with this format hh:mm and get date with this format yyyy-mm-dd in gmt+3:30
            and return timestamp of it
        """
        raise NotImplementedError

    def convert_iso_datetime_to_timestamp(self, datetime_str: str) -> int:
        """
        Convert ISO 8601 datetime string (e.g., '2025-01-15T09:25:00+03:30') to timestamp
        Args:
            datetime_str: datetime string in ISO 8601 format with timezone offset
        Returns:
            Unix timestamp in seconds
        """
        raise NotImplementedError

    def miladi_to_shamsi(self, date_str, separator: str = '-') -> str:
        """
        convert YYYY-MM-DD to SHAMSI

        returns:
        string
        """

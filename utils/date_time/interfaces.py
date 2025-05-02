from abc import ABC, abstractmethod


class AbstractDateTime(ABC):
    @abstractmethod
    def get_current_timestamp(self) -> int:
        """return current timestamp in second"""
        raise NotImplementedError
    
    def get_timestamp_of_interval_ahead(self, day_interval: int) -> int:
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

    def convert_timestamp_to_date(self, timestamp: int, date_format: str) -> str:
        """
        return date of a timestamp in format yyyy-mm-dd
        """
        raise NotImplementedError

    def convert_timestamp_to_jalali_date(self, timestamp: int, separator: str = '-') -> str:
        """
        Converts a given Unix timestamp to a formatted Jalali (Persian) date string.

        Args:
            timestamp (int): The Unix timestamp (seconds since epoch) to be converted.
            separator (str, optional): The separator to be used between year, month, and day in the formatted date string. Default is '-' (e.g., '1403-01-17').

        Returns:
            str: The formatted Jalali date string, e.g., '1403-01-17'.

        Example:
            convert_timestamp_to_jalali_date(1712345600)
            '1403-01-17'

        Notes:
            - The method first converts the Unix timestamp into a Gregorian `datetime` object and then converts that to a Jalali date using the `JalaliDate` library.
            - The returned Jalali date is formatted as 'YYYY-MM-DD', with the option to change the separator between the year, month, and day.
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

    def convert_datetime_string_to_timestamp(self, datetime_str: str, format_str: str) -> int:
        """
        Convert a datetime string in a specific format to a Unix timestamp
        
        Args:
            datetime_str: datetime string in the specified format
            format_str: format string for parsing the datetime (e.g., '%Y-%m-%d %H:%M:%S')
            
        Returns:
            Unix timestamp in seconds
            
        Example:
            convert_datetime_string_to_timestamp('2025-01-15 09:25:00', '%Y-%m-%d %H:%M:%S')
            # Returns timestamp for 2025-01-15 09:25:00
        """
        raise NotImplementedError

    def miladi_to_shamsi(self, date_str, separator: str = '-') -> str:
        """
        convert YYYY-MM-DD to SHAMSI

        returns:
        string
        """

    def convert_jalali_date_to_timestamp(self, jalali_date: str) -> int:
        """
        Convert a Jalali date string to a Unix timestamp

        Args:
            jalali_date: Jalali date string in the format YYYY-MM-DD
        """
        raise NotImplementedError

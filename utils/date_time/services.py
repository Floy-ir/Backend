import logging
from datetime import datetime, timedelta, timezone
from .interfaces import  AbstractDateTime
from khayyam import JalaliDate
import pytz


logger = logging.getLogger(__name__)

class DateTimeUtils(AbstractDateTime):
    def get_current_timestamp(self) -> int:
        return int(datetime.now().timestamp())

    def get_timestamp_of_interval_ahead(self, day_interval: int) -> int:
        return int((datetime.now() + timedelta(days=day_interval)).timestamp())

    def get_start_timestamp_of_day_from_today(self, timedelta_days: int) -> int:
        now = datetime.now()
        next_day_midnight = datetime(now.year, now.month, now.day) + timedelta(days=timedelta_days)
        return int(next_day_midnight.timestamp())

    def get_end_of_day_timestamp_from_today(self, timedelta_days: int) -> int:
        now = datetime.now()
        next_day_midnight = datetime(now.year, now.month, now.day) + timedelta(days=timedelta_days + 1)
        return int(next_day_midnight.timestamp() - 1)

    def convert_timestamp_to_date(self, timestamp: int, date_format: str) -> str:
        date_obj = datetime.fromtimestamp(timestamp)
        formatted_date = date_obj.strftime(date_format)
        return formatted_date

    def convert_timestamp_to_jalali_date(self, timestamp: int, separator: str = '-') -> str:
        # Convert timestamp to datetime in UTC
        date_obj = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        # Convert to Tehran timezone (GMT+3:30)
        tehran_tz = pytz.FixedOffset(210)  # 210 minutes = 3 hours 30 minutes
        date_obj = date_obj.astimezone(tehran_tz)
        
        # Convert to Jalali date
        jalali_date = JalaliDate(date_obj)
        formatted_date = jalali_date.strftime(f"%Y{separator}%m{separator}%d")
        return formatted_date
    
    def convert_jalali_date_to_timestamp(self, jalali_date: str) -> int:
        jalali_parts = [int(part) for part in jalali_date.split('-')]
        jalali = JalaliDate(*jalali_parts) 
        gregorian_date = jalali.todate() 
        gregorian_datetime = datetime.combine(gregorian_date, datetime.min.time())
        
        gmt_plus_3_30 = pytz.FixedOffset(210)
        gregorian_datetime = gmt_plus_3_30.localize(gregorian_datetime)

        return int(gregorian_datetime.timestamp())

    def convert_date_time_to_timestamp(self, time: str, date: str) -> int:
        # Combine date and time into a single string
        datetime_str = f"{date} {time}"

        # Parse the datetime
        local_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

        gmt_plus_3_30 = pytz.FixedOffset(210)  # 210 minutes = 3 hours 30 minutes

        localized_datetime = gmt_plus_3_30.localize(local_datetime)

        # Convert to timestamp (seconds since epoch)
        timestamp = int(localized_datetime.timestamp())

        return timestamp

    def convert_iso_datetime_to_timestamp(self, datetime_str: str) -> int:
        temp = self._convert_to_iso_format_with_offset(datetime_str)
        dt = datetime.strptime(temp, "%Y-%m-%dT%H:%M:%S%z")
        return int(dt.timestamp())

    def convert_datetime_string_to_timestamp(self, datetime_str: str, format_str: str) -> int:
        # Parse the datetime string according to the specified format
        dt = datetime.strptime(datetime_str, format_str)
        
        # Add timezone information (GMT+3:30) if not present
        if dt.tzinfo is None:
            gmt_plus_3_30 = pytz.FixedOffset(210)  # 210 minutes = 3 hours 30 minutes
            dt = gmt_plus_3_30.localize(dt)
            
        # Convert to timestamp (seconds since epoch)
        return int(dt.timestamp())

    def miladi_to_shamsi(self, date_str, separator: str = '-') -> str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        jalali_date = JalaliDate(date_obj)

        formatted_date = jalali_date.strftime(f"%Y{separator}%m{separator}%d")
        return formatted_date

    def _convert_to_iso_format_with_offset(self, date_time_str):
        try:
            iso_format = datetime.fromisoformat(date_time_str)
            if iso_format.tzinfo is not None:
                return date_time_str
            else:
                return iso_format.replace(tzinfo=timezone(timedelta(hours=3, minutes=30))).isoformat()
        except ValueError:
            try:
                custom_format = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
                return custom_format.replace(tzinfo=timezone(timedelta(hours=3, minutes=30))).isoformat()
            except ValueError:
                raise ValueError(f"Input date-time '{date_time_str}' is not in a recognized format")

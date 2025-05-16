from utils.date_time.interfaces import AbstractDateTime


class ConstantDateTimeUtils(AbstractDateTime):
    def __init__(self, current_time):
        self.current_time = current_time

    def get_current_timestamp(self) -> int:
        return self.current_time

    def get_timestamp_after_days(self, days: int) -> int:
        return self.current_time + (days * 24 * 60 * 60)

    def get_timestamp_before_days(self, days: int) -> int:
        return self.current_time - (days * 24 * 60 * 60)

    def get_timestamp_after_hours(self, hours: int) -> int:
        return self.current_time + (hours * 60 * 60)

    def get_timestamp_before_hours(self, hours: int) -> int:
        return self.current_time - (hours * 60 * 60)

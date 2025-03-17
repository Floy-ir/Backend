from apps.settings import interfaces as setting_interfaces


def validate_boolean(value):
    normalized = value.lower()
    return normalized in ['false', 'true']


def validate_string(value: str, max_length: int = 400) -> bool:
    if len(value) > max_length:
        return False
    value = value.translate({ord(letter): None for letter in '_.-@:'})
    if not value.isalnum():
        return False
    return True

def validate_numeric_string(value: str, positive: bool = None) -> bool:
    if value.isnumeric():
        if positive is not None:
            if positive:
                return value >= 0
            else:
                return value < 0
        return True

    return False


def validate_float(value: str, positive: bool = None) -> bool:
    try:
        float(value)
        if positive is not None:
            if positive:
                return value >= 0
            else:
                return value < 0
        return True
    except ValueError:
        return False

def validate_password(value: str) -> bool:
    return len(value) >= 8

def validate_list_of_int(value: str) -> bool:
    lst = value.split(',')
    try:
        if all(map(str.isdigit, lst)):
            return True
        else:
            return False
    except ValueError:
        return False


def validate_list_of_string(value: str) -> bool:
    lst = value.split(',')
    try:
        if all(map(validate_string, lst)):
            return True
        else:
            return False
    except ValueError:
        return False


available_settings_dict = {}

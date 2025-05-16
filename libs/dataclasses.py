from typing import Annotated, Optional
from pydantic.functional_validators import AfterValidator
from pydantic import BaseModel, StringConstraints, field_validator, Field, NonNegativeInt,  model_validator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import FieldValidationInfo


class BaseFilter(BaseModel):
    order_by: str = '-id'
    limit: Optional[int] = 1000
    offset: Optional[int] = 0

    @field_validator('limit')
    def limit_must_be_gt_one(cls, value, info: FieldValidationInfo):
        if value is not None and value < 1:
            raise PydanticCustomError('value_error', 'Limit should be greater than 1')
        return value

    @field_validator('offset')
    def limit_must_be_positive(cls, value, info: FieldValidationInfo):
        if value is not None and value < 0:
            raise PydanticCustomError('value_error', 'Offset should be positive')
        return value

    @model_validator(mode='after')
    def check_limit_offset_default(cls, filter_obj: 'BaseFilter'):
        if filter_obj.limit is None:
            filter_obj.limit = 20
        if filter_obj.offset is None:
            filter_obj.offset = 0
        return filter_obj

    def as_dict(self):
        return {k: v for (k, v) in self.model_dump().items() if v is not None
                and k not in ['limit', 'offset', 'order_by']}


UUIDField = Annotated[str, StringConstraints(pattern=r'^[a-zA-Z0-9_\.\-]{4,64}$')]
IPField = str # todo: change this to validate ips
URLField = str # todo: change this to validate url
PositiveIntegerField = Annotated[NonNegativeInt, Field(gt=0)]
PasswordField = str
DateField = Annotated[str, StringConstraints(pattern=r'^\d{4}-\d{2}-\d{2}$')]

class File(BaseModel):
    buffer: bytes
    name: str

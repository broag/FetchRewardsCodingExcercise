import datetime

from pydantic import BaseModel


# Base Validation Model
class BaseValidationModel(BaseModel):

    @classmethod
    def from_json(cls, json_string):
        return cls.parse_raw(json_string, content_type="application/json")

    @classmethod
    def from_dict(cls, dictionary):
        return cls.parse_obj(dictionary)

    @classmethod
    def from_dict_or_json(cls, json_string_or_dictionary):
        if isinstance(json_string_or_dictionary, str):
            return cls.from_json(json_string_or_dictionary)
        if isinstance(json_string_or_dictionary, dict):
            return cls.from_dict(json_string_or_dictionary)
        raise Exception(f"Input to {cls.__name__}.from_dict_or_json was {type(json_string_or_dictionary)} "
                        f"and not of type str or dict.")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{{{self.__class__.__name__} ({str(self.__dict__).strip('{}')})}}"

    class Config:
        use_enum_values = True
        validate_all = True


class AddPointsRequest(BaseValidationModel):
    payer: str
    points: int
    timestamp: datetime.datetime


class SpendPointsRequest(BaseValidationModel):
    points: int

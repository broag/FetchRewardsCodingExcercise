import datetime
import logging
import typing


logger = logging.getLogger(__name__)


# Service Data Objects
class Transaction:
    def __init__(self,
                 payer: str,
                 points: int,
                 timestamp: datetime.date):
        self.payer = payer
        self.points = points
        self.timestamp = timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{{{self.__class__.__name__} ({str(self.__dict__).strip('{}')})}}"


class Account:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.timestamp_sorted_transactions: typing.List[Transaction] = []
        self.available_points_by_payer: typing.Dict[str, int] = {}
        self.spent_points_by_payer: typing.Dict[str, int] = {}


# Service Logic Exceptions
class NotEnoughPointsException(Exception):
    pass


class AccountDoesntExistException(Exception):
    pass

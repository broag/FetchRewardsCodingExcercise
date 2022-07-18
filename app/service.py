import bisect
import datetime
import logging
import multiprocessing
import time
import typing

from app.model import Account, Transaction, AccountDoesntExistException, NotEnoughPointsException

logger = logging.getLogger(__name__)


class PointsService:
    def __init__(self):
        self.accounts: typing.Dict[str, Account] = {}
        self.account_locks: typing.Dict[str, multiprocessing.Lock] = {}

    def get_account_ids(self) -> typing.List[str]:
        return list(self.accounts.keys())

    def get_account(self, account_id: str) -> typing.Optional[Account]:
        return self.accounts[account_id] if account_id in self.accounts else None

    def remove_account(self, account_id: str):
        # dict.pop() is a C-function call with no bytecode __dunder__ callback, so it is technically an atomic call.
        # There is no need for explicit concurrency safety. Additionally, this method is primarily used for testing...
        self.accounts.pop(account_id)

    def get_points_balances(self, account_id: str):
        points_balances: typing.Dict[str, int] = {}
        if account_id in self.accounts:
            points_balances = self.accounts[account_id].available_points_by_payer.copy()
        return points_balances

    def add_transaction(self, account_id, payer, points, timestamp):
        # Lock mutation on account while transaction is added. `setdefault` is not guaranteed atomic, but may be in
        # some CPython implementations. Either way, handling the race condition here is not worth the performance
        # impact of a global accounts lock and can only cause a problem for the first competing requests to
        # add a create an account that doesn't exist with an add transaction.
        #
        # Note: the `with lock` syntax performs a lock.acquire() and then guarantees lock.release() on successful
        # execution and even if an exception is raised inside the with body block.
        with self.account_locks.setdefault(account_id, multiprocessing.Lock()):
            account = self.accounts.setdefault(account_id, Account(account_id))
            transaction = Transaction(payer, points, timestamp)
            self._add_transaction(account, transaction)
        return transaction

    @staticmethod
    def _add_transaction(account: Account, transaction: Transaction):
        if transaction.payer not in account.spent_points_by_payer:
            account.spent_points_by_payer[transaction.payer] = 0
        if transaction.payer not in account.available_points_by_payer:
            account.available_points_by_payer[transaction.payer] = 0

        previous_available_points = account.available_points_by_payer[transaction.payer]
        if previous_available_points + transaction.points < 0:
            # TODO: Create an alarm for this error because it is indicative of add transaction being used
            #   out of order with negative point values or an error in the spend points transactions calculation.
            # This could be swapped by raising an exception that stops the transaction from being added,
            # though it is not clear from the instructions what edge case functionality is desired.
            logger.error(f"Available Points for payer '{transaction.payer}' in account: '{account}' is negative.")

        # Uncomment millisecond wait below for reliable stress testing. It forces a thread break during a global
        # resource mutation calculation. This could also potentially be tested with a lot more threads and time...
        # time.sleep(0.001)
        account.available_points_by_payer[transaction.payer] = previous_available_points + transaction.points
        # Insert transaction into sorted list by timestamp, this uses the __lt__ function from Transaction.
        bisect.insort(account.timestamp_sorted_transactions, transaction)
        if transaction.points == 0:
            logger.error(f"Transaction {transaction} has a point value of 0. This should not be possible.")
        elif transaction.points < 0:
            # Update spent points
            account.spent_points_by_payer[transaction.payer] -= transaction.points
        logger.info(f"Applied transaction to account '{account.account_id}': {transaction}")

    def spend_points(self, account_id, points):
        # Lock mutation on account while transaction spend is being calculated and spend transactions are being added.
        with self.account_locks.setdefault(account_id, multiprocessing.Lock()):
            if account_id in self.accounts:
                account = self.accounts[account_id]
            else:
                raise AccountDoesntExistException()

            points_to_spend = points
            spend_negation_by_payer = account.spent_points_by_payer.copy()
            transactions: typing.List[Transaction] = []
            for transaction in account.timestamp_sorted_transactions:
                # Iterate over add transactions in timestamp order to accumulate spend negation.
                if transaction.points > 0 and points_to_spend > 0:
                    spend_negation = spend_negation_by_payer[transaction.payer]
                    if spend_negation >= transaction.points:
                        # Spend negation hasn't completed yet.
                        spend_negation_by_payer[transaction.payer] -= transaction.points
                    else:
                        # The accumulated add transactions for this payer have exceeded the already spent,
                        # so we can start to use these transactions and spend against them.
                        spend_negation_by_payer[transaction.payer] = 0
                        # Spend can't be larger than the points to spend and must be negative in the transaction
                        spend = -min(transaction.points - spend_negation, points_to_spend)
                        points_to_spend += spend
                        datetime_now_utc = datetime.datetime.now(datetime.timezone.utc)
                        transactions.append(Transaction(transaction.payer, spend, datetime_now_utc))

            if points_to_spend == 0:
                logger.info(f"Spend Transactions calculated for account {account_id}: {transactions}")
                for transaction in transactions:
                    self._add_transaction(account, transaction)
            else:
                raise NotEnoughPointsException(f"Not enough points to spend... need {points_to_spend} more for "
                                               f"account {account_id}")

        return transactions

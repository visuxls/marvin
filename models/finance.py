from datetime import date as Date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from models.validators import parse_flexible_date

FlexibleDate = Annotated[Date, BeforeValidator(parse_flexible_date)]


class AccountRow(BaseModel):
    """
    Validated row from ``accounts.csv``.

    Each row defines a financial account's identity, type, and institution.
    """

    account_id: str = Field(alias="Account ID")
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    institution: str = Field(alias="Institution")
    note: str | None = Field(default=None, alias="Note")

    model_config = ConfigDict(populate_by_name=True)


class AccountChildRow(BaseModel):
    """
    Base row shape for CSV imports that reference an account ID.
    """

    account_id: str


class HoldingRow(AccountChildRow):
    """
    Validated row from ``holdings.csv``.

    Each row is an investment position with symbol, quantity, and average cost basis.
    """

    symbol: str = Field(alias="Symbol")
    quantity: Decimal = Field(alias="Quantity")
    cost_basis: Decimal = Field(
        alias="Cost Basis",
        description="Average cost paid per share or unit.",
    )
    account_id: str = Field(alias="Account ID")

    model_config = ConfigDict(populate_by_name=True)


class BalanceRow(AccountChildRow):
    """
    Validated row from ``balances.csv``.

    Each row is a cash balance snapshot for an account on a given date.
    """

    account_id: str = Field(alias="Account ID")
    balance_date: FlexibleDate = Field(alias="Date")
    balance: Decimal = Field(alias="Balance")

    model_config = ConfigDict(populate_by_name=True)


class TransactionRow(AccountChildRow):
    """
    Validated row from ``transactions.csv``.

    Each row is a cash-flow transaction. Negative amounts are outflows; positive are inflows.
    """

    transaction_id: str = Field(alias="Transaction ID")
    account_id: str = Field(alias="Account ID")
    transaction_date: FlexibleDate = Field(alias="Date")
    amount: Decimal = Field(alias="Amount")
    category: str | None = Field(default=None, alias="Category")
    merchant: str | None = Field(default=None, alias="Merchant")
    description: str | None = Field(default=None, alias="Description")

    model_config = ConfigDict(populate_by_name=True)

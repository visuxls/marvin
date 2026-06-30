import sqlite3
from decimal import Decimal

from models.summaries import (
    AccountSummary,
    BalanceHistoryEntry,
    BalanceSummary,
    CategorySpending,
    HoldingSummary,
    MonthlyBurnPoint,
    NetWorthSummary,
    TransactionsSummary,
    TransactionSummary,
)

_LATEST_BALANCE_DATE_SUBQUERY = """
    b.date = (
        SELECT MAX(b2.date)
        FROM balances b2
        WHERE b2.account_id = b.account_id
    )
"""


def list_accounts(connection: sqlite3.Connection) -> list[AccountSummary]:
    """
    List all accounts ordered by name.

    Args:
        connection: Open SQLite connection used for the lookup.

    Returns:
        Account metadata for every stored account.
    """
    rows = connection.execute(
        """
                SELECT account_id, name, type, institution, note
                FROM accounts
                ORDER BY name
        """
    ).fetchall()
    return [AccountSummary(**dict(row)) for row in rows]


def get_latest_balances(
    connection: sqlite3.Connection,
    account_id: str | None = None,
) -> list[BalanceSummary]:
    """
    Return the most recent balance snapshot for each account.

    Args:
        connection: Open SQLite connection used for the lookup.
        account_id: Optional account filter.

    Returns:
        Latest balance rows joined with account metadata.
    """
    query = f"""
        SELECT
            b.account_id,
            a.name AS account_name,
            a.type AS account_type,
            b.date,
            b.balance
        FROM balances b
        JOIN accounts a ON a.account_id = b.account_id
        WHERE {_LATEST_BALANCE_DATE_SUBQUERY}
    """
    params: tuple[str, ...] = ()
    if account_id is not None:
        query += " AND b.account_id = ?"
        params = (account_id,)

    query += " ORDER BY a.name"
    rows = connection.execute(query, params).fetchall()
    return [
        BalanceSummary(
            account_id=row["account_id"],
            account_name=row["account_name"],
            account_type=row["account_type"],
            date=row["date"],
            balance=Decimal(row["balance"]),
        )
        for row in rows
    ]


def get_holdings(
    connection: sqlite3.Connection,
    account_id: str | None = None,
) -> list[HoldingSummary]:
    """
    Return investment holdings joined with account metadata.

    Args:
        connection: Open SQLite connection used for the lookup.
        account_id: Optional account filter.

    Returns:
        Holding rows for one or all investment accounts.
    """
    query = """
            SELECT
                h.account_id,
                a.name AS account_name,
                h.symbol,
                h.quantity,
                h.cost_basis
            FROM holdings h
            JOIN accounts a ON a.account_id = h.account_id
    """
    params: tuple[str, ...] = ()
    if account_id is not None:
        query += " WHERE h.account_id = ?"
        params = (account_id,)

    query += " ORDER BY a.name, h.symbol"
    rows = connection.execute(query, params).fetchall()
    return [
        HoldingSummary(
            account_id=row["account_id"],
            account_name=row["account_name"],
            symbol=row["symbol"],
            quantity=Decimal(row["quantity"]),
            cost_basis=Decimal(row["cost_basis"]),
        )
        for row in rows
    ]


def get_balance_history(
    connection: sqlite3.Connection,
    account_id: str | None = None,
) -> list[BalanceHistoryEntry]:
    """
    Return balance snapshots ordered by date and account name.

    Args:
        connection: Open SQLite connection used for the lookup.
        account_id: Optional account filter.

    Returns:
        Historical balance rows joined with account metadata.
    """
    query = """
            SELECT
                b.account_id,
                a.name AS account_name,
                a.type AS account_type,
                b.date,
                b.balance
            FROM balances b
            JOIN accounts a ON a.account_id = b.account_id
    """
    params: tuple[str, ...] = ()
    if account_id is not None:
        query += " WHERE b.account_id = ?"
        params = (account_id,)

    query += " ORDER BY b.date, a.name"
    rows = connection.execute(query, params).fetchall()
    return [
        BalanceHistoryEntry(
            account_id=row["account_id"],
            account_name=row["account_name"],
            account_type=row["account_type"],
            date=row["date"],
            balance=Decimal(row["balance"]),
        )
        for row in rows
    ]


def get_net_worth_summary(connection: sqlite3.Connection) -> NetWorthSummary:
    """
    Summarize net worth from latest balances and holding cost basis.

    Args:
        connection: Open SQLite connection used for the lookup.

    Returns:
        Aggregated net worth totals across cash/credit and investments.
    """
    balance_row = connection.execute(
        f"""
        SELECT COALESCE(SUM(CAST(b.balance AS REAL)), 0) AS total, COUNT(*) AS count
        FROM balances b
        WHERE {_LATEST_BALANCE_DATE_SUBQUERY}
        """
    ).fetchone()
    holdings_row = connection.execute(
        """
                SELECT
                    COALESCE(SUM(CAST(quantity AS REAL) * CAST(cost_basis AS REAL)), 0) AS total,
                    COUNT(DISTINCT account_id) AS count
                FROM holdings
        """
    ).fetchone()

    cash_total = Decimal(str(balance_row["total"]))
    investment_total = Decimal(str(holdings_row["total"]))

    return NetWorthSummary(
        cash_and_credit_balance_total=cash_total,
        investment_cost_basis_total=investment_total,
        net_worth_total=cash_total + investment_total,
        accounts_with_balances=balance_row["count"],
        accounts_with_holdings=holdings_row["count"],
    )


def count_transactions(connection: sqlite3.Connection) -> int:
    """
    Count all stored transactions.

    Args:
        connection: Open SQLite connection used for the lookup.

    Returns:
        Total number of transactions in the database.
    """
    row = connection.execute("SELECT COUNT(*) AS count FROM transactions").fetchone()
    return int(row["count"])


def get_transactions(
    connection: sqlite3.Connection,
    *,
    account_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
) -> TransactionsSummary:
    """
    Return transactions filtered by account and date range.

    Args:
        connection: Open SQLite connection used for the lookup.
        account_id: Optional account filter.
        start_date: Optional inclusive start date (YYYY-MM-DD).
        end_date: Optional inclusive end date (YYYY-MM-DD).
        limit: Maximum number of rows to return.

    Returns:
        Matching transactions ordered by date descending.
    """
    total_count = count_transactions(connection)
    query = """
            SELECT
                t.transaction_id,
                t.account_id,
                a.name AS account_name,
                t.date,
                t.amount,
                t.category,
                t.merchant,
                t.description
            FROM transactions t
            JOIN accounts a ON a.account_id = t.account_id
            WHERE 1 = 1
    """
    params: list[str | int] = []
    if account_id is not None:
        query += " AND t.account_id = ?"
        params.append(account_id)
    if start_date is not None:
        query += " AND t.date >= ?"
        params.append(start_date)
    if end_date is not None:
        query += " AND t.date <= ?"
        params.append(end_date)

    query += " ORDER BY t.date DESC, t.transaction_id LIMIT ?"
    params.append(limit)
    rows = connection.execute(query, params).fetchall()
    transactions = [
        TransactionSummary(
            transaction_id=row["transaction_id"],
            account_id=row["account_id"],
            account_name=row["account_name"],
            date=row["date"],
            amount=Decimal(row["amount"]),
            category=row["category"],
            merchant=row["merchant"],
            description=row["description"],
        )
        for row in rows
    ]
    return TransactionsSummary(
        transactions=transactions,
        total_count=total_count,
        has_data=total_count > 0,
    )


def get_spending_by_category(
    connection: sqlite3.Connection,
    start_date: str,
    end_date: str,
    account_id: str | None = None,
) -> list[CategorySpending]:
    """
    Aggregate outflows by category for a date range.

    Args:
        connection: Open SQLite connection used for the lookup.
        start_date: Inclusive start date (YYYY-MM-DD).
        end_date: Inclusive end date (YYYY-MM-DD).
        account_id: Optional account filter.

    Returns:
        Category totals with positive spending amounts.
    """
    query = """
            SELECT
                COALESCE(t.category, 'Uncategorized') AS category,
                COALESCE(SUM(-CAST(t.amount AS REAL)), 0) AS amount,
                COUNT(*) AS transaction_count
            FROM transactions t
            WHERE CAST(t.amount AS REAL) < 0
              AND t.date >= ?
              AND t.date <= ?
    """
    params: list[str] = [start_date, end_date]
    if account_id is not None:
        query += " AND t.account_id = ?"
        params.append(account_id)

    query += " GROUP BY category ORDER BY amount DESC"
    rows = connection.execute(query, params).fetchall()
    return [
        CategorySpending(
            category=row["category"],
            amount=Decimal(str(row["amount"])),
            transaction_count=row["transaction_count"],
            weight_pct=Decimal("0"),
        )
        for row in rows
    ]


def get_monthly_cashflow(
    connection: sqlite3.Connection,
    months: int,
    account_id: str | None = None,
) -> list[MonthlyBurnPoint]:
    """
    Return monthly income, spending, and net burn for recent months.

    Args:
        connection: Open SQLite connection used for the lookup.
        months: Number of recent calendar months to include.
        account_id: Optional account filter.

    Returns:
        Monthly cash-flow points ordered chronologically.
    """
    query = """
            SELECT
                substr(t.date, 1, 7) AS month,
                COALESCE(
                    SUM(
                        CASE
                            WHEN CAST(t.amount AS REAL) < 0 THEN -CAST(t.amount AS REAL)
                            ELSE 0
                        END
                    ),
                    0
                ) AS spending,
                COALESCE(
                    SUM(
                        CASE
                            WHEN CAST(t.amount AS REAL) > 0 THEN CAST(t.amount AS REAL)
                            ELSE 0
                        END
                    ),
                    0
                ) AS income
            FROM transactions t
            WHERE substr(t.date, 1, 7) >= (
                SELECT strftime('%Y-%m', date(MAX(t2.date), printf('-%d months', ? - 1)))
                FROM transactions t2
            )
    """
    params: list[str | int] = [months]
    if account_id is not None:
        query += " AND t.account_id = ?"
        params.append(account_id)

    query += " GROUP BY month ORDER BY month"
    rows = connection.execute(query, params).fetchall()
    return [
        MonthlyBurnPoint(
            month=row["month"],
            spending=Decimal(str(row["spending"])),
            income=Decimal(str(row["income"])),
            net_burn=Decimal(str(row["spending"])) - Decimal(str(row["income"])),
        )
        for row in rows
    ]


def get_period_income(
    connection: sqlite3.Connection,
    start_date: str,
    end_date: str,
    account_id: str | None = None,
) -> Decimal:
    """
    Sum inflows for a date range.

    Args:
        connection: Open SQLite connection used for the lookup.
        start_date: Inclusive start date (YYYY-MM-DD).
        end_date: Inclusive end date (YYYY-MM-DD).
        account_id: Optional account filter.

    Returns:
        Total positive transaction amounts in the period.
    """
    query = """
            SELECT COALESCE(SUM(CAST(t.amount AS REAL)), 0) AS income
            FROM transactions t
            WHERE CAST(t.amount AS REAL) > 0
              AND t.date >= ?
              AND t.date <= ?
    """
    params: list[str] = [start_date, end_date]
    if account_id is not None:
        query += " AND t.account_id = ?"
        params.append(account_id)

    row = connection.execute(query, params).fetchone()
    return Decimal(str(row["income"]))

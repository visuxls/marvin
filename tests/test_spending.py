from decimal import Decimal

from models.summaries import BalanceSummary, CategorySpending, MonthlyBurnPoint
from services.spending import (
    build_runway_summary,
    build_spending_breakdown,
    calculate_runway,
    sum_liquid_cash,
    summarize_monthly_burn,
    summarize_spending_breakdown,
)


def test_summarize_spending_breakdown_weights_categories():
    categories = [
        CategorySpending(
            category="Rent",
            amount=Decimal("1000"),
            transaction_count=1,
            weight_pct=Decimal("0"),
        ),
        CategorySpending(
            category="Groceries",
            amount=Decimal("500"),
            transaction_count=2,
            weight_pct=Decimal("0"),
        ),
    ]
    summary = summarize_spending_breakdown(
        categories,
        period_start="2026-04-01",
        period_end="2026-06-30",
        total_income=Decimal("3000"),
        has_data=True,
    )
    assert summary.total_spending == Decimal("1500")
    assert summary.categories[0].weight_pct == Decimal("66.67")
    assert summary.categories[1].weight_pct == Decimal("33.33")


def test_summarize_spending_breakdown_empty_categories():
    summary = summarize_spending_breakdown(
        [],
        period_start="2026-04-01",
        period_end="2026-06-30",
        total_income=Decimal("0"),
        has_data=False,
    )
    assert summary.total_spending == Decimal("0")
    assert summary.has_data is False


def test_summarize_monthly_burn():
    points = [
        MonthlyBurnPoint(
            month="2026-05",
            spending=Decimal("1000"),
            income=Decimal("3000"),
            net_burn=Decimal("-2000"),
        ),
        MonthlyBurnPoint(
            month="2026-06",
            spending=Decimal("2000"),
            income=Decimal("1000"),
            net_burn=Decimal("1000"),
        ),
    ]
    summary = summarize_monthly_burn(points, has_data=True)
    assert summary.average_monthly_burn == Decimal("-500.00")


def test_summarize_monthly_burn_without_points():
    summary = summarize_monthly_burn([], has_data=False)
    assert summary.average_monthly_burn == Decimal("0")
    assert summary.has_data is False


def test_calculate_runway():
    assert calculate_runway(Decimal("10000"), Decimal("2000")) == Decimal("5.0")
    assert calculate_runway(Decimal("10000"), Decimal("0")) is None
    assert calculate_runway(Decimal("10000"), Decimal("-100")) is None


def test_sum_liquid_cash():
    balances = [
        BalanceSummary(
            account_id="1",
            account_name="Checking",
            account_type="Checking Account",
            date="2026-06-01",
            balance=Decimal("1500"),
        ),
        BalanceSummary(
            account_id="3",
            account_name="Brokerage",
            account_type="Taxable Brokerage",
            date="2026-06-01",
            balance=Decimal("5000"),
        ),
    ]
    total = sum_liquid_cash(balances, {"1": "Checking Account", "3": "Taxable Brokerage"})
    assert total == Decimal("1500")


def test_build_spending_breakdown(test_settings, db_path):
    from ingestion.importer import import_all
    from storage.session import db_connection

    settings = test_settings.model_copy(update={"db_path": db_path})
    import_all(settings=settings)
    with db_connection(db_path) as connection:
        summary = build_spending_breakdown(connection)
    assert summary.has_data is True
    assert summary.total_spending > 0


def test_build_runway_summary_without_transactions(db_path):
    from storage.session import db_connection

    with db_connection(db_path) as connection:
        summary = build_runway_summary(connection)
    assert summary.has_data is False
    assert summary.note is not None

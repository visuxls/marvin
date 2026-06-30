"""
Marvin CFO agent construction.

Use :func:`build_agent` to create a configured Pydantic AI agent with tools and prompts.
"""

from pydantic_ai import Agent

from agent.deps import CFODeps
from agent.model import build_model, build_model_settings
from agent.prompt import CFO_INSTRUCTIONS, profile_system_prompt, runtime_system_prompt
from agent.tools import (
    get_account_balances,
    get_account_breakdown,
    get_balance_history,
    get_holdings,
    get_holdings_market_value,
    get_liquidity_summary,
    get_monthly_burn,
    get_net_worth_market_value,
    get_net_worth_over_time,
    get_net_worth_summary,
    get_portfolio_allocation,
    get_runway_months,
    get_spending_breakdown,
    get_ticker_prices,
    get_transactions,
    get_unrealized_gains,
    get_user_profile,
    list_accounts,
)


def build_agent() -> Agent[CFODeps, str]:
    """
    Build the Marvin CFO agent with model, tools, and system prompts.

    Returns:
        Configured agent ready for web or CLI use.
    """
    agent = Agent(
        build_model(),
        deps_type=CFODeps,
        instructions=CFO_INSTRUCTIONS,
        model_settings=build_model_settings(),
        retries={"output": 3},
        tools=[
            list_accounts,
            get_account_balances,
            get_balance_history,
            get_holdings,
            get_ticker_prices,
            get_holdings_market_value,
            get_net_worth_summary,
            get_net_worth_market_value,
            get_net_worth_over_time,
            get_portfolio_allocation,
            get_unrealized_gains,
            get_liquidity_summary,
            get_account_breakdown,
            get_transactions,
            get_spending_breakdown,
            get_monthly_burn,
            get_runway_months,
            get_user_profile,
        ],
    )

    agent.system_prompt(runtime_system_prompt)
    agent.system_prompt(profile_system_prompt)
    return agent

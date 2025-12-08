"""Account management tools for Futu MCP Server."""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from futu import TrdEnv
from ..futu_client import FutuClient
from ..models import AccountInfoInput, PositionListInput, CashFlowInput

logger = logging.getLogger(__name__)


def get_account_info(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get account information and funds.
    
    Args:
        client: Futu client instance
        params: Query parameters
        
    Returns:
        Dictionary with account information
    """
    input_data = AccountInfoInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Get account info (accinfo_query only accepts trd_env, not trd_market)
    ret, data = client.trade_ctx.accinfo_query(
        trd_env=trd_env
    )
    result = client.check_response(ret, data, "Failed to get account info")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        account_info = result.to_dict(orient='records')
        count = len(result)
    else:
        account_info = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "account_info": account_info,
        "count": count,
        "environment": input_data.trd_env
    }


def get_positions(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get current positions.
    
    Args:
        client: Futu client instance
        params: Query parameters
        
    Returns:
        Dictionary with position list
    """
    input_data = PositionListInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Get position list (position_list_query only accepts trd_env, not trd_market)
    ret, data = client.trade_ctx.position_list_query(
        trd_env=trd_env
    )
    result = client.check_response(ret, data, "Failed to get position list")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        positions = result.to_dict(orient='records')
        count = len(result)
    else:
        positions = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "positions": positions,
        "count": count,
        "environment": input_data.trd_env
    }


def get_cash_flow(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get cash flow history.
    
    Note: Futu API's get_acc_cash_flow only accepts a single clearing_date,
    not a date range. This function loops through dates to get a range.
    
    Args:
        client: Futu client instance
        params: Query parameters with date range
        
    Returns:
        Dictionary with cash flow data
    """
    input_data = CashFlowInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Parse dates
    start_date = datetime.strptime(input_data.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(input_data.end_date, "%Y-%m-%d")
    
    # Collect cash flows from all dates in range
    all_cash_flows = []
    current_date = start_date
    
    while current_date <= end_date:
        clearing_date_str = current_date.strftime("%Y-%m-%d")
        
        # Get cash flow for this date
        ret, data = client.trade_ctx.get_acc_cash_flow(
            clearing_date=clearing_date_str,
            trd_env=trd_env
        )
        
        # Check response - if error, log but continue (some dates may have no data)
        if ret == 0:  # RET_OK
            if isinstance(data, pd.DataFrame) and not data.empty:
                all_cash_flows.append(data)
        else:
            logger.debug(f"No cash flow data for {clearing_date_str}: {data}")
        
        current_date += timedelta(days=1)
    
    # Combine all results
    if all_cash_flows:
        combined_df = pd.concat(all_cash_flows, ignore_index=True)
        cash_flows = combined_df.to_dict(orient='records')
        count = len(combined_df)
    else:
        cash_flows = []
        count = 0
    
    return {
        "cash_flows": cash_flows,
        "count": count,
        "start_date": input_data.start_date,
        "end_date": input_data.end_date,
        "environment": input_data.trd_env
    }


"""Watchlist and alert tools for Futu MCP Server."""

import logging
from typing import Dict, Any
import pandas as pd
from futu import SetPriceReminderOp
from ..futu_client import FutuClient
from ..models import WatchlistInput, PriceReminderInput

logger = logging.getLogger(__name__)


def get_watchlist(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get user's watchlist securities.
    
    Args:
        client: Futu client instance
        params: Query parameters
        
    Returns:
        Dictionary with watchlist securities
    """
    input_data = WatchlistInput(**params)
    client.ensure_connected()
    
    # Get user securities
    ret, data = client.quote_ctx.get_user_security(
        group_name=input_data.group_name or "All"
    )
    result = client.check_response(ret, data, "Failed to get watchlist")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        securities = result.to_dict(orient='records')
        count = len(result)
    else:
        securities = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "securities": securities,
        "count": count,
        "group_name": input_data.group_name or "All"
    }


def set_price_reminder(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Set or modify price reminder/alert.
    
    Args:
        client: Futu client instance
        params: Reminder parameters
        
    Returns:
        Dictionary with operation result
    """
    input_data = PriceReminderInput(**params)
    client.ensure_connected()
    
    # Convert operation
    op_mapping = {
        "ADD": SetPriceReminderOp.ADD,
        "DEL": SetPriceReminderOp.DEL,
        "ENABLE": SetPriceReminderOp.ENABLE,
        "DISABLE": SetPriceReminderOp.DISABLE,
        "MODIFY": SetPriceReminderOp.MODIFY,
        "DEL_ALL": SetPriceReminderOp.DEL_ALL,
    }
    operation = op_mapping.get(input_data.operation)
    
    # Set price reminder
    ret, data = client.quote_ctx.set_price_reminder(
        code=input_data.stock_code,
        op=operation,
        reminder_type=input_data.reminder_type,
        reminder_freq=input_data.reminder_value,
        value=input_data.reminder_value or 0,
        note=input_data.note
    )
    result = client.check_response(ret, data, "Failed to set price reminder")
    
    logger.info(f"Price reminder set: {input_data.stock_code} - {input_data.operation}")
    
    return {
        "stock_code": input_data.stock_code,
        "operation": input_data.operation,
        "result": str(result)
    }


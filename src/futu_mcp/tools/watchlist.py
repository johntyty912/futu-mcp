"""Watchlist and alert tools for Futu MCP Server."""

import logging
from typing import Dict, Any
import pandas as pd
from futu import SetPriceReminderOp, UserSecurityGroupType, RET_OK, PriceReminderFreq, PriceReminderType
from ..futu_client import FutuClient
from ..models import WatchlistInput, PriceReminderInput

logger = logging.getLogger(__name__)


def get_watchlist(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get user's watchlist securities.
    
    If group_name is not specified or doesn't exist, lists available groups first.
    
    Args:
        client: Futu client instance
        params: Query parameters
        
    Returns:
        Dictionary with watchlist securities
    """
    input_data = WatchlistInput(**params)
    client.ensure_connected()
    
    group_name = input_data.group_name
    
    # If no group name specified, try to get available groups first
    if not group_name:
        ret, data = client.quote_ctx.get_user_security_group(group_type=UserSecurityGroupType.ALL)
        if ret == RET_OK and isinstance(data, pd.DataFrame) and not data.empty:
            # Use the first available group, or "All" if it exists
            available_groups = data['group_name'].tolist() if 'group_name' in data.columns else []
            if "All" in available_groups:
                group_name = "All"
            elif available_groups:
                group_name = available_groups[0]
                logger.info(f"No group specified, using first available group: {group_name}")
            else:
                group_name = "All"  # Fallback
        else:
            group_name = "All"  # Fallback
    
    # Get user securities
    ret, data = client.quote_ctx.get_user_security(group_name=group_name)
    
    # If group doesn't exist, try to get available groups and return error with suggestions
    if ret != RET_OK:
        # Try to get available groups to provide helpful error message
        ret_groups, data_groups = client.quote_ctx.get_user_security_group(group_type=UserSecurityGroupType.ALL)
        available_groups = []
        if ret_groups == RET_OK and isinstance(data_groups, pd.DataFrame) and not data_groups.empty:
            if 'group_name' in data_groups.columns:
                available_groups = data_groups['group_name'].tolist()
        
        error_msg = f"Failed to get watchlist: {data}"
        if available_groups:
            error_msg += f". Available groups: {', '.join(available_groups)}"
        
        raise client.check_response(ret, data, error_msg)
    
    result = data
    
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
        "group_name": group_name
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
    
    # Convert reminder frequency
    freq_mapping = {
        "ALWAYS": PriceReminderFreq.ALWAYS,
        "ONCE": PriceReminderFreq.ONCE,
        "DAILY": PriceReminderFreq.DAILY,
    }
    reminder_freq = freq_mapping.get(input_data.reminder_freq or "ALWAYS", PriceReminderFreq.ALWAYS)
    
    # Convert reminder type if provided
    reminder_type_enum = None
    if input_data.reminder_type:
        # Map string reminder types to enum values
        # Common types: PRICE_UP, PRICE_DOWN, ASK_PRICE_DOWN, BID_PRICE_UP, etc.
        try:
            # Try to get enum value by name (e.g., "PRICE_UP" -> PriceReminderType.PRICE_UP)
            reminder_type_enum = getattr(PriceReminderType, input_data.reminder_type.upper())
        except (AttributeError, TypeError):
            # If not found as enum, use as-is (API may accept string or it might already be an enum)
            reminder_type_enum = input_data.reminder_type
            logger.warning(f"Reminder type '{input_data.reminder_type}' not found as enum, using as-is")
    
    # Set price reminder
    ret, data = client.quote_ctx.set_price_reminder(
        code=input_data.stock_code,
        op=operation,
        reminder_type=reminder_type_enum,
        reminder_freq=reminder_freq,
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


"""Market information tools for Futu MCP Server."""

import logging
from typing import Dict, Any
from ..futu_client import FutuClient
from ..models import TradingDaysInput, StaticInfoInput

logger = logging.getLogger(__name__)


def get_trading_days(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get trading calendar days.
    
    Args:
        client: Futu client instance
        params: Query parameters with market and date range
        
    Returns:
        Dictionary with trading days
    """
    input_data = TradingDaysInput(**params)
    client.ensure_connected()
    
    trd_market = client.convert_trd_market(input_data.market)
    
    # Get trading days
    ret, data = client.quote_ctx.request_trading_days(
        market=trd_market,
        start=input_data.start_date,
        end=input_data.end_date
    )
    result = client.check_response(ret, data, "Failed to get trading days")
    
    return {
        "trading_days": result.to_dict(orient='records') if hasattr(result, 'to_dict') else list(result),
        "market": input_data.market.value,
        "start_date": input_data.start_date,
        "end_date": input_data.end_date
    }


def get_static_info(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get static information for securities.
    
    Args:
        client: Futu client instance
        params: Query parameters with stock codes
        
    Returns:
        Dictionary with static information
    """
    input_data = StaticInfoInput(**params)
    client.ensure_connected()
    
    # Get static info
    ret, data = client.quote_ctx.get_stock_basicinfo(
        stock_code=input_data.stock_codes
    )
    result = client.check_response(ret, data, "Failed to get static info")
    
    return {
        "static_info": result.to_dict(orient='records'),
        "count": len(result)
    }


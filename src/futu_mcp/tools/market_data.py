"""Market data tools for Futu MCP Server."""

import logging
from typing import Dict, Any
import pandas as pd
from ..futu_client import FutuClient
from ..models import (
    StockQuoteInput,
    HistoricalKlineInput,
    MarketSnapshotInput,
    OrderBookInput,
    TickerInput,
    OptionChainInput,
)

logger = logging.getLogger(__name__)


def get_stock_quote(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get real-time stock quotes.
    
    Note: Some markets (e.g., US stocks) may require account permissions/subscriptions.
    Permission errors will be clearly indicated in the error message.
    
    Args:
        client: Futu client instance
        params: Parameters containing stock_codes
        
    Returns:
        Dictionary with quote data
    """
    input_data = StockQuoteInput(**params)
    client.ensure_connected()
    
    # Subscribe to quotes first
    ret, data = client.quote_ctx.subscribe(input_data.stock_codes, ['QUOTE'])
    
    # Check for permission errors and provide helpful message
    if ret != 0:  # Not RET_OK
        error_msg = str(data)
        # Check if it's a permission error (Chinese error message about permissions)
        if "权限" in error_msg or "permission" in error_msg.lower() or "无权限" in error_msg:
            market_hint = ""
            if any(code.startswith("US.") for code in input_data.stock_codes):
                market_hint = " US market quote permissions may need to be enabled in your Futu account settings."
            elif any(code.startswith("HK.") for code in input_data.stock_codes):
                market_hint = " HK market quote permissions may need to be enabled in your Futu account settings."
            
            raise client.check_response(
                ret, 
                data, 
                f"Failed to subscribe to quotes (permission error): {error_msg}.{market_hint} "
                f"Please check your account's market data subscription/permissions in Futu account settings."
            )
        else:
            client.check_response(ret, data, "Failed to subscribe to quotes")
    
    # Get quote data
    ret, data = client.quote_ctx.get_stock_quote(input_data.stock_codes)
    result = client.check_response(ret, data, "Failed to get stock quotes")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        quotes = result.to_dict(orient='records')
        count = len(result)
    else:
        quotes = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "quotes": quotes,
        "count": count
    }


def get_historical_kline(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get historical K-line (candlestick) data.
    
    Args:
        client: Futu client instance
        params: Parameters for historical K-line query
        
    Returns:
        Dictionary with K-line data
    """
    input_data = HistoricalKlineInput(**params)
    client.ensure_connected()
    
    # Convert enums to Futu types
    kl_type = client.convert_kl_type(input_data.kl_type)
    au_type = client.convert_au_type(input_data.autype)
    
    # Request historical K-line data
    ret, data, page_req_key = client.quote_ctx.request_history_kline(
        code=input_data.stock_code,
        start=input_data.start_date,
        end=input_data.end_date,
        ktype=kl_type,
        autype=au_type,
        max_count=input_data.max_count
    )
    result = client.check_response(ret, data, "Failed to get historical K-line")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        klines = result.to_dict(orient='records')
        count = len(result)
    else:
        klines = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "klines": klines,
        "count": count,
        "page_req_key": page_req_key
    }


def get_market_snapshot(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get market snapshot for multiple stocks.
    
    Note: Some markets (e.g., US stocks/ETFs) may require account permissions/subscriptions.
    Permission errors will be clearly indicated in the error message.
    
    Args:
        client: Futu client instance
        params: Parameters containing stock_codes
        
    Returns:
        Dictionary with snapshot data
    """
    input_data = MarketSnapshotInput(**params)
    client.ensure_connected()
    
    # Subscribe first
    ret, data = client.quote_ctx.subscribe(input_data.stock_codes, ['QUOTE'])
    
    # Check for permission errors and provide helpful message
    if ret != 0:  # Not RET_OK
        error_msg = str(data)
        # Check if it's a permission error (Chinese error message about permissions)
        if "权限" in error_msg or "permission" in error_msg.lower() or "无权限" in error_msg:
            market_hint = ""
            if any(code.startswith("US.") for code in input_data.stock_codes):
                market_hint = " US market quote permissions may need to be enabled in your Futu account settings."
            elif any(code.startswith("HK.") for code in input_data.stock_codes):
                market_hint = " HK market quote permissions may need to be enabled in your Futu account settings."
            
            raise client.check_response(
                ret, 
                data, 
                f"Failed to subscribe (permission error): {error_msg}.{market_hint} "
                f"Please check your account's market data subscription/permissions in Futu account settings."
            )
        else:
            client.check_response(ret, data, "Failed to subscribe")
    
    # Get market snapshot
    ret, data = client.quote_ctx.get_market_snapshot(input_data.stock_codes)
    result = client.check_response(ret, data, "Failed to get market snapshot")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        snapshots = result.to_dict(orient='records')
        count = len(result)
    else:
        snapshots = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "snapshots": snapshots,
        "count": count
    }


def get_order_book(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get order book (market depth) data.
    
    Args:
        client: Futu client instance
        params: Parameters containing stock_code
        
    Returns:
        Dictionary with order book data
    """
    input_data = OrderBookInput(**params)
    client.ensure_connected()
    
    # Subscribe to order book
    ret, data = client.quote_ctx.subscribe([input_data.stock_code], ['ORDER_BOOK'])
    client.check_response(ret, data, "Failed to subscribe to order book")
    
    # Get order book
    ret, data = client.quote_ctx.get_order_book(input_data.stock_code)
    result = client.check_response(ret, data, "Failed to get order book")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        order_book = result.to_dict(orient='records')
    elif isinstance(result, dict):
        order_book = result
    else:
        order_book = str(result)
    
    return {
        "stock_code": input_data.stock_code,
        "order_book": order_book
    }


def get_rt_ticker(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get real-time tick-by-tick data.
    
    Args:
        client: Futu client instance
        params: Parameters for ticker query
        
    Returns:
        Dictionary with ticker data
    """
    input_data = TickerInput(**params)
    client.ensure_connected()
    
    # Subscribe to ticker
    ret, data = client.quote_ctx.subscribe([input_data.stock_code], ['TICKER'])
    client.check_response(ret, data, "Failed to subscribe to ticker")
    
    # Get real-time tickers
    ret, data = client.quote_ctx.get_rt_ticker(
        code=input_data.stock_code,
        num=input_data.max_count
    )
    result = client.check_response(ret, data, "Failed to get real-time ticker")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        tickers = result.to_dict(orient='records')
        count = len(result)
    else:
        tickers = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "tickers": tickers,
        "count": count
    }


def get_option_chain(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get option chain data.
    
    Args:
        client: Futu client instance
        params: Parameters for option chain query
        
    Returns:
        Dictionary with option chain data
    """
    input_data = OptionChainInput(**params)
    client.ensure_connected()
    
    # Get option chain
    ret, data = client.quote_ctx.get_option_chain(
        code=input_data.stock_code,
        start=input_data.start_date,
        end=input_data.end_date
    )
    result = client.check_response(ret, data, "Failed to get option chain")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        options = result.to_dict(orient='records')
        count = len(result)
    else:
        options = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "options": options,
        "count": count,
        "underlying": input_data.stock_code
    }


def get_market_state(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get market trading state.
    
    Args:
        client: Futu client instance
        params: Optional parameters containing stock_codes
        
    Returns:
        Dictionary with market state data
    """
    client.ensure_connected()
    
    # Get global market state
    ret, data = client.quote_ctx.get_global_state()
    result = client.check_response(ret, data, "Failed to get market state")
    
    # Handle different return types
    if isinstance(result, pd.DataFrame):
        market_states = result.to_dict(orient='records')
        count = len(result)
    elif isinstance(result, dict):
        market_states = [result]
        count = 1
    elif isinstance(result, list):
        market_states = result
        count = len(result)
    else:
        market_states = str(result)
        count = 1
    
    return {
        "market_states": market_states,
        "count": count
    }


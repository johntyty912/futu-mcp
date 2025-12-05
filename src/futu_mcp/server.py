"""Main Futu MCP Server implementation using FastMCP."""

import logging
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from .config import get_config
from .futu_client import FutuClient
from .tools import market_data, trading, account, watchlist, market_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Futu MCP Server")

# Get configuration
config = get_config()

# Initialize Futu client (will be connected per-request)
futu_client = FutuClient(config)


# Market Data Tools
@mcp.tool()
def get_stock_quote(stock_codes: list[str]) -> Dict[str, Any]:
    """Get real-time stock quotes.
    
    Args:
        stock_codes: List of stock codes (e.g., ['HK.00700', 'US.AAPL'])
        
    Returns:
        Dictionary with real-time quote data including price, volume, bid/ask
    """
    with futu_client:
        return market_data.get_stock_quote(futu_client, {"stock_codes": stock_codes})


@mcp.tool()
def get_historical_kline(
    stock_code: str,
    start_date: str,
    end_date: str,
    kl_type: str = "K_DAY",
    autype: str = "qfq",
    max_count: int = 1000
) -> Dict[str, Any]:
    """Get historical K-line (candlestick) data for backtesting and analysis.
    
    Args:
        stock_code: Stock code (e.g., 'HK.00700')
        start_date: Start date in yyyy-MM-dd format
        end_date: End date in yyyy-MM-dd format
        kl_type: K-line type (K_1M, K_5M, K_15M, K_30M, K_60M, K_DAY, K_WEEK, K_MON)
        autype: Adjustment type (qfq=forward, hfq=backward, None=no adjustment)
        max_count: Maximum number of K-lines to return (default 1000)
        
    Returns:
        Dictionary with K-line data including OHLC, volume, turnover
    """
    with futu_client:
        return market_data.get_historical_kline(futu_client, {
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "kl_type": kl_type,
            "autype": autype,
            "max_count": max_count
        })


@mcp.tool()
def get_market_snapshot(stock_codes: list[str]) -> Dict[str, Any]:
    """Get market snapshot for multiple stocks.
    
    Args:
        stock_codes: List of stock codes
        
    Returns:
        Dictionary with market snapshot data
    """
    with futu_client:
        return market_data.get_market_snapshot(futu_client, {"stock_codes": stock_codes})


@mcp.tool()
def get_order_book(stock_code: str) -> Dict[str, Any]:
    """Get order book (market depth) showing bid/ask levels.
    
    Args:
        stock_code: Stock code
        
    Returns:
        Dictionary with order book data showing multiple bid/ask levels
    """
    with futu_client:
        return market_data.get_order_book(futu_client, {"stock_code": stock_code})


@mcp.tool()
def get_rt_ticker(stock_code: str, max_count: int = 1000) -> Dict[str, Any]:
    """Get real-time tick-by-tick transaction data.
    
    Args:
        stock_code: Stock code
        max_count: Maximum number of tickers to return (default 1000)
        
    Returns:
        Dictionary with tick-by-tick transaction data
    """
    with futu_client:
        return market_data.get_rt_ticker(futu_client, {
            "stock_code": stock_code,
            "max_count": max_count
        })


@mcp.tool()
def get_option_chain(
    stock_code: str,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Get option chain data for an underlying security.
    
    Args:
        stock_code: Underlying stock code
        start_date: Start expiration date (yyyy-MM-dd), optional
        end_date: End expiration date (yyyy-MM-dd), optional
        
    Returns:
        Dictionary with option chain data including strikes, Greeks, IV
    """
    with futu_client:
        return market_data.get_option_chain(futu_client, {
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date
        })


@mcp.tool()
def get_market_state(stock_codes: list[str] = None) -> Dict[str, Any]:
    """Get current market trading state (pre-market, open, closed, etc.).
    
    Args:
        stock_codes: Optional list of stock codes for specific market states
        
    Returns:
        Dictionary with market state information
    """
    with futu_client:
        return market_data.get_market_state(futu_client, {"stock_codes": stock_codes})


# Trading Tools
@mcp.tool()
def place_order(
    stock_code: str,
    trd_side: str,
    order_type: str,
    qty: float,
    price: float = None,
    trd_env: str = "SIMULATE",
    trd_market: str = None,
    remark: str = None
) -> Dict[str, Any]:
    """Place a trading order with full validation and safeguards.
    
    Args:
        stock_code: Stock code to trade
        trd_side: Trading side (BUY or SELL)
        order_type: Order type (NORMAL, MARKET, STOP, STOP_LIMIT, etc.)
        qty: Order quantity
        price: Order price (required for limit orders)
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        trd_market: Trading market (HK, US, CN, etc.), optional
        remark: Order remark (max 64 bytes), optional
        
    Returns:
        Dictionary with order placement result including order ID
    """
    with futu_client:
        return trading.place_order(futu_client, {
            "stock_code": stock_code,
            "trd_side": trd_side,
            "order_type": order_type,
            "qty": qty,
            "price": price,
            "trd_env": trd_env,
            "trd_market": trd_market,
            "remark": remark
        })


@mcp.tool()
def modify_order(
    order_id: str,
    modify_op: str,
    qty: float = None,
    price: float = None,
    trd_env: str = "SIMULATE"
) -> Dict[str, Any]:
    """Modify an existing order.
    
    Args:
        order_id: Order ID to modify
        modify_op: Modification operation (CANCEL, MODIFY, ENABLE, DISABLE)
        qty: New quantity (for MODIFY operation)
        price: New price (for MODIFY operation)
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        
    Returns:
        Dictionary with modification result
    """
    with futu_client:
        return trading.modify_order(futu_client, {
            "order_id": order_id,
            "modify_op": modify_op,
            "qty": qty,
            "price": price,
            "trd_env": trd_env
        })


@mcp.tool()
def cancel_order(order_id: str, trd_env: str = "SIMULATE") -> Dict[str, Any]:
    """Cancel a specific order.
    
    Args:
        order_id: Order ID to cancel
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        
    Returns:
        Dictionary with cancellation result
    """
    with futu_client:
        return trading.cancel_order(futu_client, {
            "order_id": order_id,
            "trd_env": trd_env
        })


@mcp.tool()
def cancel_all_orders(trd_env: str = "SIMULATE") -> Dict[str, Any]:
    """Cancel all orders for the account.
    
    Args:
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        
    Returns:
        Dictionary with bulk cancellation result
    """
    with futu_client:
        return trading.cancel_all_orders(futu_client, {"trd_env": trd_env})


@mcp.tool()
def get_order_list(
    trd_env: str = "SIMULATE",
    trd_market: str = None,
    status_filter: list[str] = None
) -> Dict[str, Any]:
    """Get list of orders.
    
    Args:
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        trd_market: Trading market filter (HK, US, CN, etc.), optional
        status_filter: Order status filter list, optional
        
    Returns:
        Dictionary with order list
    """
    with futu_client:
        return trading.get_order_list(futu_client, {
            "trd_env": trd_env,
            "trd_market": trd_market,
            "status_filter": status_filter
        })


@mcp.tool()
def get_deal_list(
    trd_env: str = "SIMULATE",
    trd_market: str = None
) -> Dict[str, Any]:
    """Get today's deal (transaction) list.
    
    Args:
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        trd_market: Trading market filter (HK, US, CN, etc.), optional
        
    Returns:
        Dictionary with today's deal list
    """
    with futu_client:
        return trading.get_deal_list(futu_client, {
            "trd_env": trd_env,
            "trd_market": trd_market
        })


@mcp.tool()
def get_history_deal_list(
    start_time: str,
    end_time: str,
    trd_env: str = "SIMULATE"
) -> Dict[str, Any]:
    """Get historical deal list (up to 90 days).
    
    Args:
        start_time: Start time (YYYY-MM-DD HH:MM:SS)
        end_time: End time (YYYY-MM-DD HH:MM:SS)
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        
    Returns:
        Dictionary with historical deal list
    """
    with futu_client:
        return trading.get_history_deal_list(futu_client, {
            "start_time": start_time,
            "end_time": end_time,
            "trd_env": trd_env
        })


@mcp.tool()
def get_max_trd_qtys(
    stock_code: str,
    order_type: str,
    trd_side: str,
    price: float = None,
    trd_env: str = "SIMULATE"
) -> Dict[str, Any]:
    """Get maximum tradable quantities for a security.
    
    Args:
        stock_code: Stock code
        order_type: Order type
        trd_side: Trading side (BUY or SELL)
        price: Order price, optional
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        
    Returns:
        Dictionary with max tradable quantities and buying power
    """
    with futu_client:
        return trading.get_max_trd_qtys(futu_client, {
            "stock_code": stock_code,
            "order_type": order_type,
            "trd_side": trd_side,
            "price": price,
            "trd_env": trd_env
        })


# Account Management Tools
@mcp.tool()
def get_account_info(
    trd_env: str = "SIMULATE",
    trd_market: str = None
) -> Dict[str, Any]:
    """Get account information including balance, buying power, and assets.
    
    Args:
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        trd_market: Trading market (HK, US, CN, etc.), optional
        
    Returns:
        Dictionary with detailed account information and funds
    """
    with futu_client:
        return account.get_account_info(futu_client, {
            "trd_env": trd_env,
            "trd_market": trd_market
        })


@mcp.tool()
def get_positions(
    trd_env: str = "SIMULATE",
    trd_market: str = None
) -> Dict[str, Any]:
    """Get current positions.
    
    Args:
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        trd_market: Trading market filter (HK, US, CN, etc.), optional
        
    Returns:
        Dictionary with position list including cost, P&L, quantity
    """
    with futu_client:
        return account.get_positions(futu_client, {
            "trd_env": trd_env,
            "trd_market": trd_market
        })


@mcp.tool()
def get_cash_flow(
    start_date: str,
    end_date: str,
    trd_env: str = "SIMULATE"
) -> Dict[str, Any]:
    """Get cash flow transaction history.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        trd_env: Trading environment (REAL or SIMULATE, default SIMULATE)
        
    Returns:
        Dictionary with cash flow transactions
    """
    with futu_client:
        return account.get_cash_flow(futu_client, {
            "start_date": start_date,
            "end_date": end_date,
            "trd_env": trd_env
        })


# Watchlist and Alert Tools
@mcp.tool()
def get_watchlist(group_name: str = None) -> Dict[str, Any]:
    """Get securities in watchlist.
    
    Args:
        group_name: Watchlist group name, optional (default "All")
        
    Returns:
        Dictionary with watchlist securities
    """
    with futu_client:
        return watchlist.get_watchlist(futu_client, {"group_name": group_name})


@mcp.tool()
def set_price_reminder(
    stock_code: str,
    operation: str,
    reminder_type: str = None,
    reminder_value: float = None,
    note: str = None
) -> Dict[str, Any]:
    """Set or modify price reminder/alert.
    
    Args:
        stock_code: Stock code
        operation: Operation type (ADD, DEL, ENABLE, DISABLE, MODIFY, DEL_ALL)
        reminder_type: Reminder type (PRICE_UP, PRICE_DOWN, etc.), required for ADD/MODIFY
        reminder_value: Threshold value, required for ADD/MODIFY
        note: Reminder note (max 64 bytes), optional
        
    Returns:
        Dictionary with operation result
    """
    with futu_client:
        return watchlist.set_price_reminder(futu_client, {
            "stock_code": stock_code,
            "operation": operation,
            "reminder_type": reminder_type,
            "reminder_value": reminder_value,
            "note": note
        })


# Market Info Tools
@mcp.tool()
def get_trading_days(
    market: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Get trading calendar days (excludes weekends and holidays).
    
    Args:
        market: Trading market (HK, US, CN, etc.)
        start_date: Start date (yyyy-MM-dd)
        end_date: End date (yyyy-MM-dd)
        
    Returns:
        Dictionary with trading days list
    """
    with futu_client:
        return market_info.get_trading_days(futu_client, {
            "market": market,
            "start_date": start_date,
            "end_date": end_date
        })


@mcp.tool()
def get_static_info(stock_codes: list[str]) -> Dict[str, Any]:
    """Get static information for securities (lot size, type, listing date, etc.).
    
    Args:
        stock_codes: List of stock codes
        
    Returns:
        Dictionary with static security information
    """
    with futu_client:
        return market_info.get_static_info(futu_client, {"stock_codes": stock_codes})


# Main entry point
def create_app():
    """Create ASGI application for HTTP transport.
    
    Returns:
        ASGI application that can be run with uvicorn or other ASGI servers
    """
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route, Mount
    
    # Get the MCP ASGI app from FastMCP
    mcp_app = mcp.streamable_http_app
    
    # Health check endpoint
    async def health_check(request):
        """Health check endpoint for Docker and load balancers."""
        return JSONResponse({
            "status": "healthy",
            "service": "futu-mcp-server",
            "version": "0.1.0"
        })
    
    # Create Starlette app with routes
    app = Starlette(
        routes=[
            Route("/health", health_check, methods=["GET"]),
            Mount("/mcp", mcp_app),
        ]
    )
    
    return app


def main():
    """Run the Futu MCP server.
    
    Supports two modes:
    - stdio mode (default): For local MCP clients like Cursor and Claude Desktop
    - HTTP mode: For remote access and Antigravity integration
    
    Usage:
        # Run in stdio mode (default)
        python -m futu_mcp.server
        
        # Run in HTTP mode
        python -m futu_mcp.server --http
    """
    import sys
    
    logger.info("Starting Futu MCP Server...")
    logger.info(f"FutuOpenD connection: {config.host}:{config.port}")
    
    # Check if HTTP mode is requested via command line or config
    http_mode = "--http" in sys.argv or config.server_mode.lower() == "http"
    
    if http_mode:
        logger.info(f"Running in HTTP mode on {config.server_host}:{config.server_port}")
        logger.info("Health check endpoint: /health")
        logger.info("MCP endpoint: /mcp")
        
        # Run with uvicorn
        import uvicorn
        uvicorn.run(
            create_app(),
            host=config.server_host,
            port=config.server_port,
            log_level=config.log_level.lower()
        )
    else:
        logger.info("Running in stdio mode")
        logger.info("Use --http flag or set SERVER_MODE=http for HTTP mode")
        mcp.run()


if __name__ == "__main__":
    main()


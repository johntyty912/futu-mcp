# Futu MCP Server Tools Reference

This is a quick reference for the available MCP tools when using this server through Cursor.

**Note**: All tools are prefixed with `mcp_futu_` when called through the MCP interface.

## Account Management

### `get_account_info`
Get account information including balance, buying power, and assets.

**Parameters:**
- `trd_env`: str = "SIMULATE" - Trading environment (REAL or SIMULATE)
- `trd_market`: str = None - Trading market (HK, US, CN, etc.), optional

**MCP Tool Name:** `mcp_futu_get_account_info`

---

### `get_positions`
Get current positions.

**Parameters:**
- `trd_env`: str = "SIMULATE" - Trading environment
- `trd_market`: str = None - Trading market filter

**MCP Tool Name:** `mcp_futu_get_positions`

---

### `get_cash_flow`
Get cash flow transaction history.

**Parameters:**
- `start_date`: str - Start date (YYYY-MM-DD)
- `end_date`: str - End date (YYYY-MM-DD)
- `trd_env`: str = "SIMULATE" - Trading environment

**MCP Tool Name:** `mcp_futu_get_cash_flow`

---

## Market Data

### `get_stock_quote`
Get real-time stock quotes.

**Parameters:**
- `stock_codes`: list[str] - List of stock codes (e.g., ['HK.00700', 'US.AAPL'])

**MCP Tool Name:** `mcp_futu_get_stock_quote`

---

### `get_historical_kline`
Get historical K-line (candlestick) data.

**Parameters:**
- `stock_code`: str - Stock code
- `start_date`: str - Start date (yyyy-MM-dd)
- `end_date`: str - End date (yyyy-MM-dd)
- `kl_type`: str = "K_DAY" - K-line type
- `autype`: str = "qfq" - Adjustment type
- `max_count`: int = 1000 - Maximum number of K-lines

**MCP Tool Name:** `mcp_futu_get_historical_kline`

---

### `get_market_snapshot`
Get market snapshot for multiple stocks.

**Parameters:**
- `stock_codes`: list[str] - List of stock codes

**MCP Tool Name:** `mcp_futu_get_market_snapshot`

---

### `get_order_book`
Get order book (market depth) showing bid/ask levels.

**Parameters:**
- `stock_code`: str - Stock code

**MCP Tool Name:** `mcp_futu_get_order_book`

---

### `get_market_state`
Get current market trading state.

**Parameters:**
- `stock_codes`: list[str] = None - Optional list of stock codes

**MCP Tool Name:** `mcp_futu_get_market_state`

---

## Trading Operations

### `place_order`
Place a trading order.

**Parameters:**
- `stock_code`: str - Stock code to trade
- `trd_side`: str - Trading side (BUY or SELL)
- `order_type`: str - Order type (NORMAL, MARKET, etc.)
- `qty`: float - Order quantity
- `price`: float = None - Order price (required for limit orders)
- `trd_env`: str = "SIMULATE" - Trading environment
- `trd_market`: str = None - Trading market
- `remark`: str = None - Order remark

**MCP Tool Name:** `mcp_futu_place_order`

---

### `get_order_list`
Get list of orders.

**Parameters:**
- `trd_env`: str = "SIMULATE" - Trading environment
- `trd_market`: str = None - Trading market filter
- `status_filter`: list[str] = None - Order status filter

**MCP Tool Name:** `mcp_futu_get_order_list`

---

### `cancel_order`
Cancel a specific order.

**Parameters:**
- `order_id`: str - Order ID to cancel
- `trd_env`: str = "SIMULATE" - Trading environment

**MCP Tool Name:** `mcp_futu_cancel_order`

---

## Other Tools

Full list of available tools:
- `mcp_futu_get_rt_ticker` - Real-time tick data
- `mcp_futu_get_option_chain` - Option chain data
- `mcp_futu_modify_order` - Modify existing order
- `mcp_futu_cancel_all_orders` - Cancel all orders
- `mcp_futu_get_deal_list` - Today's deal list
- `mcp_futu_get_history_deal_list` - Historical deals
- `mcp_futu_get_max_trd_qtys` - Maximum tradable quantities
- `mcp_futu_get_watchlist` - Get watchlist
- `mcp_futu_set_price_reminder` - Set price alerts
- `mcp_futu_get_trading_days` - Get trading calendar
- `mcp_futu_get_static_info` - Get security static info

---

## Configuration

Make sure your `~/.cursor/mcp.json` includes:

```json
{
  "mcpServers": {
    "futu": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/Users/john/work/john/futu-mcp",
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111",
        "FUTU_TRADE_PWD": "your_trading_password",
        "FUTU_CONNECTION_TIMEOUT": "30",
        "FUTU_REQUEST_TIMEOUT": "60",
        "FUTU_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Troubleshooting

1. **Trading unlock fails**: Make sure `FUTU_TRADE_PWD` is set in the MCP configuration
2. **Connection fails**: Ensure FutuOpenD is running on the specified host:port
3. **Server won't start**: Check logs and verify all dependencies are installed (`uv sync`)
4. **After config changes**: Restart Cursor completely to reload the MCP server

## Testing Connection

Run this from the project directory to test your connection:

```bash
cd /Users/john/work/john/futu-mcp
FUTU_TRADE_PWD="your_password" uv run python -c "
from futu import OpenSecTradeContext, TrdEnv
import os

trade_pwd = os.getenv('FUTU_TRADE_PWD')
ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
ret, data = ctx.unlock_trade(trade_pwd)

if ret == 0:
    print('✅ Trading unlocked!')
    ret2, data2 = ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
    if ret2 == 0:
        print('✅ Account info retrieved!')
        print(data2)
else:
    print(f'❌ Error: {data}')
    
ctx.close()
"
```


# Futu MCP Server

A comprehensive **Model Context Protocol (MCP)** server for the **Futu trading platform**, providing AI assistants with access to real-time market data, trading operations, account management, and more.

## Features

### 🔍 Market Data Tools (8 tools)
- **Real-time Quotes** - Get current stock prices, volume, bid/ask
- **Historical K-Line Data** - Access candlestick data for backtesting
- **Market Snapshots** - Overview of multiple securities
- **Order Book** - Market depth with bid/ask levels
- **Tick-by-Tick Data** - Real-time transaction stream
- **Option Chains** - Options data with Greeks and IV
- **Market State** - Trading hours and market status
- **Static Info** - Security fundamentals

### 💹 Trading Tools (9 tools)
- **Place Orders** - Buy/sell with multiple order types (limit, market, stop, etc.)
- **Modify Orders** - Update price, quantity, or cancel orders
- **Cancel Orders** - Single or bulk order cancellation
- **Order List** - View open and historical orders
- **Deal List** - Today's executed transactions
- **Historical Deals** - Up to 90 days of transaction history
- **Max Tradable Quantities** - Calculate buying power

### 💰 Account Management Tools (3 tools)
- **Account Info** - Balance, buying power, assets
- **Positions** - Current holdings with P&L
- **Cash Flow** - Transaction history

### 📊 Watchlist & Alerts (2 tools)
- **Watchlists** - Manage security groups
- **Price Reminders** - Set price alerts and notifications

### 📅 Market Info (2 tools)
- **Trading Calendar** - Get trading days
- **Static Information** - Security details

**Total: 24 comprehensive tools** covering all aspects of trading and market analysis.

## Prerequisites

### 1. FutuOpenD Gateway

FutuOpenD is required to communicate with Futu servers. Download and install:

- **Download**: [Futu OpenAPI](https://www.futunn.com/download/OpenAPI)
- **Documentation**: [Futu API Docs](https://openapi.futunn.com/futu-api-doc/)

**Start FutuOpenD**:
```bash
# Default: localhost:11111
./FutuOpenD
```

### 2. Futu Account

- Create a Futu account at [Futu](https://www.futunn.com/)
- For trading: Complete KYC and fund your account
- For paper trading: Use simulation mode (no real money required)

### 3. Python 3.12+

Ensure Python 3.12 or higher is installed.

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd futu-mcp

# Install with uv
uv sync

# Or install from PyPI (when published)
uv pip install futu-mcp
```

### Using pip

```bash
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# FutuOpenD Connection
FUTU_HOST=127.0.0.1
FUTU_PORT=11111

# Trading Password (required for real trading)
FUTU_TRADE_PWD=your_trading_password

# Timeouts (seconds)
FUTU_CONNECTION_TIMEOUT=30
FUTU_REQUEST_TIMEOUT=60

# Market Data
FUTU_MAX_SUBSCRIPTION_QUOTA=500
```

**Security Note**: Never commit `.env` files to version control!

## Usage

### Running the MCP Server

The server runs in stdio mode (standard input/output), which is the standard way MCP servers communicate with clients.

```bash
# Using uv
uv run futu-mcp-server

# Or directly with Python
python -m futu_mcp.server
```

The server will start and wait for MCP requests via stdio. It's typically launched by MCP clients (Cursor, Claude Desktop, etc.) automatically.

### Docker Deployment

#### Quick Start with Docker Compose

```bash
# Build and start the server
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f futu-mcp

# Stop the server
docker-compose down
```

#### Manual Docker Build and Run

```bash
# Build the image
docker build -t futu-mcp:latest .

# Run with host networking (easiest for FutuOpenD access)
docker run -d \
  --name futu-mcp-server \
  --network host \
  -e FUTU_HOST=127.0.0.1 \
  -e FUTU_PORT=11111 \
  futu-mcp:latest

# View logs
docker logs futu-mcp-server
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guides.


### MCP Client Configuration

#### For Cursor IDE

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "futu": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/path/to/futu-mcp",
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111"
      }
    }
  }
}
```

#### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "futu": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/path/to/futu-mcp",
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111"
      }
    }
  }
}
```

#### For Antigravity

Add to your Antigravity `mcp_config.json`:

```json
{
  "mcpServers": {
    "futu": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/path/to/futu-mcp",
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111"
      }
    }
  }
}
```

See [mcp-config-examples/antigravity-config.json](mcp-config-examples/antigravity-config.json) for the complete example configuration.


## Example Queries

Once connected to an MCP client, you can ask:

### Market Data
- *"Get real-time quote for Tencent (HK.00700)"*
- *"Show me historical daily data for AAPL from 2024-01-01 to 2024-12-31"*
- *"What's the current market state for US stocks?"*
- *"Get the order book for Tesla"*

### Trading
- *"Place a limit buy order for 100 shares of AAPL at $150"*
- *"Cancel order ID 12345"*
- *"Show me all my open orders"*
- *"What's my maximum buying power for TSLA?"*

### Account
- *"Show my account balance and buying power"*
- *"List all my current positions"*
- *"Get my cash flow history for the last month"*

### Analysis
- *"Get the option chain for SPY"*
- *"Show me trading days in January 2024 for US market"*
- *"Set a price alert when AAPL goes above $200"*

## Tool Reference

### Market Data

#### `get_stock_quote`
```python
stock_codes: list[str]  # e.g., ["HK.00700", "US.AAPL"]
```

#### `get_historical_kline`
```python
stock_code: str         # e.g., "HK.00700"
start_date: str        # "2024-01-01"
end_date: str          # "2024-12-31"
kl_type: str          # K_1M, K_5M, K_15M, K_30M, K_60M, K_DAY, K_WEEK, K_MON
autype: str           # qfq (forward), hfq (backward), None
max_count: int        # default 1000
```

#### `get_market_snapshot`
```python
stock_codes: list[str]
```

#### `get_order_book`
```python
stock_code: str
```

#### `get_rt_ticker`
```python
stock_code: str
max_count: int        # default 1000
```

#### `get_option_chain`
```python
stock_code: str       # underlying
start_date: str      # optional, "yyyy-MM-dd"
end_date: str        # optional, "yyyy-MM-dd"
```

#### `get_market_state`
```python
stock_codes: list[str]  # optional
```

### Trading

#### `place_order`
```python
stock_code: str
trd_side: str         # BUY or SELL
order_type: str       # NORMAL, MARKET, STOP, STOP_LIMIT, etc.
qty: float
price: float         # optional, required for limit orders
trd_env: str         # REAL or SIMULATE (default SIMULATE)
trd_market: str      # HK, US, CN, etc. (optional)
remark: str          # optional, max 64 bytes
```

#### `modify_order`
```python
order_id: str
modify_op: str       # CANCEL, MODIFY, ENABLE, DISABLE
qty: float          # optional, for MODIFY
price: float        # optional, for MODIFY
trd_env: str        # default SIMULATE
```

#### `cancel_order`
```python
order_id: str
trd_env: str        # default SIMULATE
```

#### `cancel_all_orders`
```python
trd_env: str        # default SIMULATE
```

#### `get_order_list`
```python
trd_env: str         # default SIMULATE
trd_market: str      # optional
status_filter: list[str]  # optional
```

#### `get_deal_list`
```python
trd_env: str         # default SIMULATE
trd_market: str      # optional
```

#### `get_history_deal_list`
```python
start_time: str      # "YYYY-MM-DD HH:MM:SS"
end_time: str        # "YYYY-MM-DD HH:MM:SS"
trd_env: str         # default SIMULATE
```

#### `get_max_trd_qtys`
```python
stock_code: str
order_type: str
trd_side: str
price: float         # optional
trd_env: str         # default SIMULATE
```

### Account Management

#### `get_account_info`
```python
trd_env: str         # default SIMULATE
trd_market: str      # optional
```

#### `get_positions`
```python
trd_env: str         # default SIMULATE
trd_market: str      # optional
```

#### `get_cash_flow`
```python
start_date: str      # "YYYY-MM-DD"
end_date: str        # "YYYY-MM-DD"
trd_env: str         # default SIMULATE
```

### Watchlist & Alerts

#### `get_watchlist`
```python
group_name: str      # optional, default "All"
```

#### `set_price_reminder`
```python
stock_code: str
operation: str       # ADD, DEL, ENABLE, DISABLE, MODIFY, DEL_ALL
reminder_type: str   # optional, PRICE_UP, PRICE_DOWN, etc.
reminder_value: float  # optional, threshold
note: str           # optional, max 64 bytes
```

### Market Info

#### `get_trading_days`
```python
market: str          # HK, US, CN, etc.
start_date: str      # "yyyy-MM-dd"
end_date: str        # "yyyy-MM-dd"
```

#### `get_static_info`
```python
stock_codes: list[str]
```

## Trading Safety

### Paper Trading (Default)

All trading operations default to **SIMULATE** mode (paper trading) for safety. No real money is at risk.

```python
# Paper trading (default)
place_order(..., trd_env="SIMULATE")
```

### Real Trading

To trade with real money:

1. Set `FUTU_TRADE_PWD` in your `.env` file
2. Use `trd_env="REAL"` in trading operations
3. Ensure FutuOpenD is connected to your real account

```python
# Real trading (use with caution!)
place_order(..., trd_env="REAL")
```

**⚠️ Warning**: Real trading involves financial risk. Always verify orders before execution.

## Stock Code Format

Futu uses a specific format for stock codes:

- **Hong Kong**: `HK.00700` (Tencent)
- **US Stocks**: `US.AAPL` (Apple)
- **China A-shares**: `SH.600000` (Shanghai), `SZ.000001` (Shenzhen)
- **Singapore**: `SG.D05` (DBS)
- **Japan**: `JP.7203` (Toyota)

## Error Handling

The server implements comprehensive error handling:

- **Connection Errors**: FutuOpenD not running or wrong host/port
- **Authentication Errors**: Invalid trading password
- **API Errors**: Invalid parameters, insufficient permissions
- **Rate Limiting**: Automatic retry with exponential backoff

All errors are returned with clear, actionable messages.

## Logging

Logs are output to stdout with the following format:

```
2024-01-01 12:00:00 - futu_mcp.server - INFO - Order placed: HK.00700 BUY 100 @ 350.0
```

Adjust log level by setting `LOG_LEVEL` environment variable:

```bash
LOG_LEVEL=DEBUG uv run futu-mcp-server
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=futu_mcp
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Type check
uv run mypy src/futu_mcp
```

### Project Structure

```
futu-mcp/
├── src/
│   └── futu_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── config.py          # Configuration
│       ├── models.py          # Pydantic models
│       ├── futu_client.py     # Futu API wrapper
│       └── tools/             # Tool implementations
│           ├── __init__.py
│           ├── market_data.py
│           ├── trading.py
│           ├── account.py
│           ├── watchlist.py
│           └── market_info.py
├── tests/
├── pyproject.toml
├── README.md
└── .env.example
```

## Troubleshooting

### FutuOpenD Connection Failed

```
FutuConnectionError: Failed to connect to FutuOpenD
```

**Solution**: 
- Ensure FutuOpenD is running
- Check `FUTU_HOST` and `FUTU_PORT` settings
- Verify firewall settings

### Unlock Trade Failed

```
FutuConnectionError: Failed to unlock trade
```

**Solution**:
- Verify `FUTU_TRADE_PWD` is correct
- Ensure you're using `trd_env="REAL"`
- Check if your account has trading permissions

### Subscription Quota Exceeded

```
FutuAPIError: Subscription quota exceeded
```

**Solution**:
- Unsubscribe from unused securities
- Increase quota by upgrading account level
- Use `max_subscription_quota` configuration

### Invalid Stock Code

```
FutuAPIError: Invalid stock code format
```

**Solution**:
- Use correct format: `HK.00700`, `US.AAPL`, `SH.600000`
- Verify the security exists and is tradable

## Supported Markets

- 🇭🇰 Hong Kong (HK) - Stocks, ETFs, Warrants, Options, Futures
- 🇺🇸 United States (US) - Stocks, ETFs, Options, Futures
- 🇨🇳 China (CN) - A-shares, ETFs
- 🇸🇬 Singapore (SG) - Stocks, ETFs, Futures
- 🇯🇵 Japan (JP) - Stocks, ETFs, Futures

## Limitations

- **Paper Trading**: Some features may not be available in simulate mode
- **Rate Limits**: API calls are subject to Futu's rate limiting
- **Market Data**: Requires appropriate subscription level
- **Real Trading**: Requires funded account and trading password

## Resources

- [Futu OpenAPI Documentation](https://openapi.futunn.com/futu-api-doc/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Disclaimer

This software is for educational and research purposes. Trading stocks involves risk. The authors are not responsible for any financial losses incurred through the use of this software. Always verify trades and understand the risks before trading with real money.

## Support

For issues and questions:
- Open an issue on GitHub
- Check Futu API documentation
- Review MCP protocol specifications

---

**Built with ❤️ using the Model Context Protocol**


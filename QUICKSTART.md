# Futu MCP Server - Quick Start Guide

Get up and running with the Futu MCP Server in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.12+ installed
- [ ] `uv` package manager installed ([install guide](https://github.com/astral-sh/uv))
- [ ] FutuOpenD downloaded and installed ([download](https://www.futunn.com/download/OpenAPI))
- [ ] Futu account created (optional for paper trading)

## Step 1: Start FutuOpenD (Required!)

Before running the MCP server, you **must** start FutuOpenD:

```bash
# Navigate to your FutuOpenD installation directory
cd /path/to/FutuOpenD

# Start FutuOpenD (it will run on localhost:11111 by default)
./FutuOpenD
```

Keep FutuOpenD running in a separate terminal window.

## Step 2: Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

For **paper trading** (no real money), the defaults are fine!

For **real trading**, edit `.env` and set:
```bash
FUTU_TRADE_PWD=your_trading_password
```

## Step 3: Install Dependencies

```bash
# Sync all dependencies
uv sync
```

## Step 4: Test the Server

```bash
# Run the server directly to test
uv run python -m futu_mcp.server
```

If you see "Starting Futu MCP Server..." without errors, it's working! Press `Ctrl+C` to stop.

## Step 5: Configure Your MCP Client

### For Cursor IDE

1. Open `~/.cursor/mcp.json` (create if it doesn't exist)
2. Add the Futu MCP server configuration:

```json
{
  "mcpServers": {
    "futu": {
      "command": "uv",
      "args": ["run", "python", "-m", "futu_mcp.server"],
      "cwd": "/absolute/path/to/futu-mcp"
    }
  }
}
```

**Important**: Replace `/absolute/path/to/futu-mcp` with your actual path!

3. Restart Cursor IDE

### For Claude Desktop

1. Open the config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the same configuration as above
3. Restart Claude Desktop

## Step 6: Try It Out!

Once your MCP client is configured, try these queries:

### Basic Market Data
```
Get a real-time quote for Apple (US.AAPL)
```

### Historical Data
```
Get daily K-line data for Tencent (HK.00700) from 2024-01-01 to 2024-12-31
```

### Paper Trading (Safe!)
```
Place a simulated buy order for 100 shares of Tesla at market price
```

### Account Info
```
Show me my simulated account balance and positions
```

## Common Issues & Solutions

### ❌ "Failed to connect to FutuOpenD"

**Solution**: Make sure FutuOpenD is running! Check:
```bash
# On macOS/Linux, check if FutuOpenD is running
ps aux | grep FutuOpenD

# Try connecting manually
telnet localhost 11111
```

### ❌ "Invalid stock code format"

**Solution**: Use the correct format:
- Hong Kong: `HK.00700` (Tencent)
- US stocks: `US.AAPL` (Apple)
- China A-shares: `SH.600000` (Pudong Bank)

### ❌ "Module not found" or "Command not found"

**Solution**: Make sure you're in the project directory and dependencies are installed:
```bash
cd /path/to/futu-mcp
uv sync
```

### ❌ MCP server not appearing in Cursor/Claude

**Solution**: 
1. Check the config file path is correct
2. Ensure `cwd` uses absolute path (not relative)
3. Restart the application
4. Check application logs for errors

## What's Next?

### Learn the Tools

The server provides **24 tools** organized into categories:

1. **Market Data** (8 tools) - Quotes, charts, order books, options
2. **Trading** (9 tools) - Place orders, manage positions
3. **Account** (3 tools) - Balance, positions, cash flow
4. **Watchlists** (2 tools) - Manage favorites and alerts
5. **Market Info** (2 tools) - Trading calendar, security details

See the [main README](README.md) for complete tool documentation.

### Safe Trading Practices

1. **Always test in SIMULATE mode first** (default)
2. **Verify orders** before submitting
3. **Use limit orders** for price control
4. **Set stop losses** for risk management
5. **Monitor positions** regularly

### Supported Markets

- 🇭🇰 Hong Kong - `HK.00700`
- 🇺🇸 United States - `US.AAPL`
- 🇨🇳 China A-shares - `SH.600000`, `SZ.000001`
- 🇸🇬 Singapore - `SG.D05`
- 🇯🇵 Japan - `JP.7203`

## Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Configuration Examples**: [mcp-config-examples/](mcp-config-examples/)
- **Futu API Docs**: https://openapi.futunn.com/futu-api-doc/
- **MCP Protocol**: https://modelcontextprotocol.io/

## Getting Help

If you encounter issues:

1. Check FutuOpenD is running
2. Verify your `.env` configuration
3. Review the [README.md](README.md) troubleshooting section
4. Check Futu API documentation for API-specific questions

---

## Pro Tips

💡 **Tip 1**: Keep FutuOpenD running in a dedicated terminal window with:
```bash
# Run in background (macOS/Linux)
nohup ./FutuOpenD > futu.log 2>&1 &
```

💡 **Tip 2**: Use paper trading mode extensively before real trading:
```
Test my trading strategy in simulate mode for AAPL
```

💡 **Tip 3**: Set up watchlists for quick access:
```
Add AAPL, MSFT, and GOOGL to my watchlist
```

💡 **Tip 4**: Monitor market state before trading:
```
Check if US market is open for trading
```

---

**Happy Trading! 🚀📈**

Remember: This software is for educational purposes. Always understand the risks before trading with real money.


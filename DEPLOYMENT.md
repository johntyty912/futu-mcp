# Deployment Guide for Futu MCP Server

This guide covers deploying the Futu MCP Server, which runs in stdio mode (standard input/output) for communication with MCP clients.

## Prerequisites

1. **FutuOpenD** running on your machine (localhost:11111)
2. **Python 3.12+** installed
3. **uv** package manager (recommended) or pip

## Local Deployment

### 1. Install Dependencies

```bash
cd /path/to/futu-mcp
uv sync
```

### 2. Configure Environment

Create or update your `.env` file:

```bash
# FutuOpenD Connection
FUTU_HOST=127.0.0.1
FUTU_PORT=11111

# Optional: Trading Password (for real trading)
# FUTU_TRADE_PWD=your_password

# Optional: Timeouts
FUTU_CONNECTION_TIMEOUT=30
FUTU_REQUEST_TIMEOUT=60

# Optional: Logging
LOG_LEVEL=INFO
```

### 3. Test the Server

```bash
# Test that the server starts correctly
uv run futu-mcp-server

# Or directly with Python
python -m futu_mcp.server
```

The server will start in stdio mode and wait for MCP requests. It's typically launched automatically by MCP clients (Cursor, Claude Desktop, etc.).

## MCP Client Configuration

The server is configured in your MCP client's configuration file. See the main [README.md](README.md) for client-specific configuration examples.

### For Cursor IDE

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "futu": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/absolute/path/to/futu-mcp",
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111"
      }
    }
  }
}
```

### For Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "futu": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/absolute/path/to/futu-mcp",
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111"
      }
    }
  }
}
```

## Remote FutuOpenD

If FutuOpenD is running on a remote server:

```json
"env": {
  "FUTU_HOST": "192.168.1.100",  // Remote server IP
  "FUTU_PORT": "11111",
  "FUTU_CONNECTION_TIMEOUT": "60"  // Increase for remote connections
}
```

**Security Note**: Ensure secure network connection when using remote FutuOpenD.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FUTU_HOST` | `127.0.0.1` | FutuOpenD host address |
| `FUTU_PORT` | `11111` | FutuOpenD port number |
| `FUTU_TRADE_PWD` | `None` | Trading password (required for real trading) |
| `FUTU_CONNECTION_TIMEOUT` | `30` | Connection timeout in seconds |
| `FUTU_REQUEST_TIMEOUT` | `60` | Request timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Troubleshooting

### Server won't start

**Error**: `ModuleNotFoundError` or import errors

**Solutions**:
- Ensure dependencies are installed: `uv sync`
- Verify Python version: `python --version` (should be 3.12+)
- Check virtual environment is activated

### Connection Failed

**Error**: `FutuConnectionError: Failed to connect to FutuOpenD`

**Solutions**:
- Ensure FutuOpenD is running
- Verify `FUTU_HOST` and `FUTU_PORT` in environment variables
- Check firewall settings
- For remote FutuOpenD, verify network connectivity

### Permission Denied

**Error**: Permission denied or access issues

**Solutions**:
- Ensure the MCP client has permission to execute the command
- Check file permissions on the futu-mcp directory
- On macOS/Linux, verify the script is executable

### MCP Client Not Finding Server

**Error**: `MCP server "futu" not found`

**Solutions**:
- Verify `cwd` path is correct and absolute
- Check that `futu-mcp-server` is installed: `uv run futu-mcp-server --help`
- Try running the command manually in terminal
- Check MCP client logs for detailed error messages

## Multiple Accounts

To configure multiple Futu accounts, use different MCP server instances:

```json
{
  "mcpServers": {
    "futu-account1": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/path/to/futu-mcp",
      "env": {
        "FUTU_PORT": "11111"
      }
    },
    "futu-account2": {
      "command": "uv",
      "args": ["run", "futu-mcp-server"],
      "cwd": "/path/to/futu-mcp",
      "env": {
        "FUTU_PORT": "11112"
      }
    }
  }
}
```

Run multiple FutuOpenD instances on different ports.

## Security Considerations

1. **Trading Password**: Never commit `.env` files with trading passwords to version control
2. **Network Security**: When using remote FutuOpenD, ensure secure network connection
3. **File Permissions**: Restrict access to configuration files containing sensitive data
4. **Environment Variables**: Use environment variables instead of hardcoding credentials

## Support

For deployment issues:
- Check main [README.md](README.md) for detailed documentation
- Verify FutuOpenD is properly installed and running
- Review MCP client logs for error messages
- Test connection manually: `uv run futu-mcp-server` in terminal

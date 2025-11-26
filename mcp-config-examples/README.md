# MCP Client Configuration Examples

This directory contains example configuration files for various MCP clients.

## Cursor IDE

**Location**: `~/.cursor/mcp.json` (or workspace-specific `.cursor/mcp.json`)

**Example**: See `cursor-mcp.json`

**Usage**:
1. Copy `cursor-mcp.json` content to `~/.cursor/mcp.json`
2. Update `cwd` to your actual futu-mcp installation path
3. Restart Cursor IDE
4. The Futu MCP server will be available in Cursor's AI assistant

## Claude Desktop

**Location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Example**: See `claude-desktop-config.json`

**Usage**:
1. Copy `claude-desktop-config.json` content to the appropriate location
2. Update `cwd` to your actual futu-mcp installation path
3. Restart Claude Desktop
4. The Futu MCP server tools will be available in Claude

## VS Code with MCP Extension

**Location**: Workspace `.vscode/mcp.json` or user settings

**Example**: Same format as `cursor-mcp.json`

## Configuration Options

### Required Fields

- `command`: The command to run (use "uv" for uv-managed projects)
- `args`: Arguments to pass to the command
- `cwd`: **Absolute path** to the futu-mcp directory

### Optional Environment Variables

```json
"env": {
  "FUTU_HOST": "127.0.0.1",          // FutuOpenD host
  "FUTU_PORT": "11111",              // FutuOpenD port
  "FUTU_TRADE_PWD": "",              // Trading password (for real trading)
  "FUTU_CONNECTION_TIMEOUT": "30",   // Connection timeout (seconds)
  "FUTU_REQUEST_TIMEOUT": "60",      // Request timeout (seconds)
  "LOG_LEVEL": "INFO"                // Logging level
}
```

### Alternative: Python-based Configuration

If not using uv, you can run with Python directly:

```json
{
  "mcpServers": {
    "futu": {
      "command": "python",
      "args": [
        "-m",
        "futu_mcp.server"
      ],
      "cwd": "/absolute/path/to/futu-mcp",
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111"
      }
    }
  }
}
```

### Alternative: Direct Script Configuration

If installed globally:

```json
{
  "mcpServers": {
    "futu": {
      "command": "futu-mcp-server",
      "args": [],
      "env": {
        "FUTU_HOST": "127.0.0.1",
        "FUTU_PORT": "11111"
      }
    }
  }
}
```

## Verification

After configuration:

1. **Check FutuOpenD**: Ensure FutuOpenD is running on the configured host/port
2. **Restart Client**: Restart your MCP client (Cursor, Claude Desktop, etc.)
3. **Test Connection**: Try a simple query like "Get quote for AAPL"
4. **Check Logs**: Look for connection messages in the client's output

## Troubleshooting

### Server Not Found

**Error**: `MCP server "futu" not found`

**Solutions**:
- Verify `cwd` path is correct and absolute
- Check that `futu-mcp-server` is installed
- Try running `uv run futu-mcp-server` manually in the terminal

### Connection Failed

**Error**: `FutuConnectionError: Failed to connect to FutuOpenD`

**Solutions**:
- Ensure FutuOpenD is running
- Verify `FUTU_HOST` and `FUTU_PORT` in env variables
- Check firewall settings

### Permission Denied

**Error**: Permission denied or access issues

**Solutions**:
- Ensure the MCP client has permission to execute the command
- Check file permissions on the futu-mcp directory
- On macOS/Linux, verify the script is executable

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

## Support

For configuration issues:
- Check main README.md for detailed documentation
- Verify FutuOpenD is properly installed and running
- Review MCP client logs for error messages
- Test connection manually: `uv run futu-mcp-server` in terminal


import asyncio
import sys
import os
from main import DiscordMCP
from http_mcp_server import StreamableHTTPMCP

async def main():
    """Main entry point that starts both Discord bot and HTTP MCP server"""
    
    print("Starting Discord MCP with HTTP interface...")
    
    # Initialize the Discord MCP
    discord_mcp = DiscordMCP()
    
    # Initialize the HTTP MCP server
    http_server = StreamableHTTPMCP()
    
    # Set the Discord MCP instance in the HTTP server
    http_server.discord_mcp = discord_mcp
    
    # Start both services concurrently
    # Start the Discord bot
    discord_task = asyncio.create_task(discord_mcp.start())
    
    # Give the bot a moment to initialize
    await asyncio.sleep(3)
    
    # Start the HTTP server
    print("Starting HTTP MCP server on port 8080...")
    try:
        # Run the HTTP server
        await http_server.initialize()
        http_server.run(host="0.0.0.0", port=8080)
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to start application: {e}")
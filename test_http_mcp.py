import asyncio
import aiohttp
import json
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_http_mcp_server():
    """Test script for the HTTP MCP server"""
    
    base_url = "http://localhost:8080"
    
    print("Testing HTTP MCP Server...")
    
    # Test health endpoint
    try:
        async with aiohttp.ClientSession() as session:
            # Test health check
            async with session.get(f"{base_url}/health") as resp:
                print(f"Health check: {resp.status}")
                health_data = await resp.json()
                print(f"Health response: {health_data}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test an endpoint that requires Discord bot (will fail if bot isn't running)
    # For testing purposes, let's just make sure the server handles the request properly
    try:
        async with aiohttp.ClientSession() as session:
            # Test list_servers endpoint
            async with session.post(f"{base_url}/list_servers", json={}) as resp:
                print(f"List servers: {resp.status}")
                servers_data = await resp.json()
                print(f"Servers response: {servers_data}")
    except Exception as e:
        print(f"List servers test failed: {e}")
    
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(test_http_mcp_server())
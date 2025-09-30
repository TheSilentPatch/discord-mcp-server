import asyncio
import json
import logging
from typing import Dict, Any, Optional
from aiohttp import web, WSMsgType
from multidict import CIMultiDict
import os
from main import DiscordMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("http-mcp-server")

class StreamableHTTPMCP:
    """
    Streamable HTTP MCP Server implementation that provides HTTP-based access 
    to Discord operations implemented in the DiscordMCP class.
    """
    
    def __init__(self):
        self.discord_mcp: Optional[DiscordMCP] = None
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Setup HTTP routes for MCP operations"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/send_message', self.handle_send_message)
        self.app.router.add_post('/read_messages', self.handle_read_messages)
        self.app.router.add_post('/get_user_info', self.handle_get_user_info)
        self.app.router.add_post('/list_servers', self.handle_list_servers)
        self.app.router.add_post('/create_text_channel', self.handle_create_text_channel)
        self.app.router.add_post('/delete_channel', self.handle_delete_channel)
        self.app.router.add_post('/add_reaction', self.handle_add_reaction)
        self.app.router.add_post('/remove_reaction', self.handle_remove_reaction)
        
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "discord-mcp-http"})
    
    async def handle_send_message(self, request):
        """HTTP handler for sending messages"""
        try:
            data = await request.json()
            channel_id = data.get("channel_id")
            content = data.get("content")
            
            if not channel_id or not content:
                return web.json_response(
                    {"error": "channel_id and content are required"}, 
                    status=400
                )
                
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.send_message(int(channel_id), content)
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error in handle_send_message: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_read_messages(self, request):
        """HTTP handler for reading messages"""
        try:
            data = await request.json()
            channel_id = data.get("channel_id")
            limit = data.get("limit", 10)
            
            if not channel_id:
                return web.json_response(
                    {"error": "channel_id is required"}, 
                    status=400
                )
                
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.read_messages(int(channel_id), int(limit))
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error in handle_read_messages: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_get_user_info(self, request):
        """HTTP handler for getting user information"""
        try:
            data = await request.json()
            user_id = data.get("user_id")
            
            if not user_id:
                return web.json_response(
                    {"error": "user_id is required"}, 
                    status=400
                )
                
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.get_user_info(int(user_id))
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error in handle_get_user_info: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_list_servers(self, request):
        """HTTP handler for listing servers"""
        try:
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.list_servers()
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Error in handle_list_servers: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_create_text_channel(self, request):
        """HTTP handler for creating text channels"""
        try:
            data = await request.json()
            server_id = data.get("server_id")
            name = data.get("name")
            category_id = data.get("category_id")
            
            if not server_id or not name:
                return web.json_response(
                    {"error": "server_id and name are required"}, 
                    status=400
                )
                
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.create_text_channel(
                int(server_id), name, int(category_id) if category_id else None
            )
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error in handle_create_text_channel: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_delete_channel(self, request):
        """HTTP handler for deleting channels"""
        try:
            data = await request.json()
            channel_id = data.get("channel_id")
            
            if not channel_id:
                return web.json_response(
                    {"error": "channel_id is required"}, 
                    status=400
                )
                
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.delete_channel(int(channel_id))
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error in handle_delete_channel: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_add_reaction(self, request):
        """HTTP handler for adding reactions"""
        try:
            data = await request.json()
            channel_id = data.get("channel_id")
            message_id = data.get("message_id")
            emoji = data.get("emoji")
            
            if not channel_id or not message_id or not emoji:
                return web.json_response(
                    {"error": "channel_id, message_id, and emoji are required"}, 
                    status=400
                )
                
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.add_reaction(int(channel_id), int(message_id), emoji)
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error in handle_add_reaction: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_remove_reaction(self, request):
        """HTTP handler for removing reactions"""
        try:
            data = await request.json()
            channel_id = data.get("channel_id")
            message_id = data.get("message_id")
            emoji = data.get("emoji")
            
            if not channel_id or not message_id or not emoji:
                return web.json_response(
                    {"error": "channel_id, message_id, and emoji are required"}, 
                    status=400
                )
                
            if not self.discord_mcp or not self.discord_mcp.bot:
                return web.json_response(
                    {"error": "Discord bot not initialized"}, 
                    status=500
                )
                
            result = await self.discord_mcp.remove_reaction(int(channel_id), int(message_id), emoji)
            return web.json_response(result)
            
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error in handle_remove_reaction: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def start_discord_bot(self):
        """Start the Discord bot in the background"""
        self.discord_mcp = DiscordMCP()
        # Run the bot in the background
        asyncio.create_task(self.discord_mcp.start())
        
        # Give the bot a moment to initialize
        await asyncio.sleep(3)
    
    async def initialize(self):
        """Initialize the HTTP MCP server with the Discord bot"""
        logger.info("Initializing HTTP MCP server with Discord bot...")
        await self.start_discord_bot()
    
    def run(self, host="0.0.0.0", port=8080):
        """Run the HTTP MCP server"""
        logger.info(f"Starting HTTP MCP server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)

# WebSocket support for streaming responses
class StreamableHTTPMCPWithWebSocket(StreamableHTTPMCP):
    """
    Enhanced version with WebSocket support for streaming responses
    """
    
    def setup_routes(self):
        """Setup HTTP routes including WebSocket"""
        super().setup_routes()
        self.app.router.add_get('/ws', self.websocket_handler)
        
    async def websocket_handler(self, request):
        """Handle WebSocket connections for streaming responses"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        logger.info("New WebSocket connection established")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        action = data.get("action")
                        
                        if action == "send_message":
                            result = await self.handle_send_message_via_ws(data)
                        elif action == "read_messages":
                            result = await self.handle_read_messages_via_ws(data)
                        elif action == "get_user_info":
                            result = await self.handle_get_user_info_via_ws(data)
                        elif action == "list_servers":
                            result = await self.handle_list_servers_via_ws(data)
                        elif action == "create_text_channel":
                            result = await self.handle_create_text_channel_via_ws(data)
                        elif action == "delete_channel":
                            result = await self.handle_delete_channel_via_ws(data)
                        elif action == "add_reaction":
                            result = await self.handle_add_reaction_via_ws(data)
                        elif action == "remove_reaction":
                            result = await self.handle_remove_reaction_via_ws(data)
                        else:
                            result = {"error": "Unknown action", "action": action}
                        
                        await ws.send_str(json.dumps(result))
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({"error": "Invalid JSON"}))
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")
                        await ws.send_str(json.dumps({"error": str(e)}))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket connection closed with exception {ws.exception()}")
                    break
        finally:
            logger.info("WebSocket connection closed")
        
        return ws
    
    # WebSocket handler methods (these would call the same underlying methods as HTTP)
    async def handle_send_message_via_ws(self, data):
        channel_id = data.get("channel_id")
        content = data.get("content")
        if not channel_id or not content:
            return {"error": "channel_id and content are required"}
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.send_message(int(channel_id), content)
    
    async def handle_read_messages_via_ws(self, data):
        channel_id = data.get("channel_id")
        limit = data.get("limit", 10)
        if not channel_id:
            return {"error": "channel_id is required"}
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.read_messages(int(channel_id), int(limit))
    
    async def handle_get_user_info_via_ws(self, data):
        user_id = data.get("user_id")
        if not user_id:
            return {"error": "user_id is required"}
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.get_user_info(int(user_id))
    
    async def handle_list_servers_via_ws(self, data):
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.list_servers()
    
    async def handle_create_text_channel_via_ws(self, data):
        server_id = data.get("server_id")
        name = data.get("name")
        category_id = data.get("category_id")
        if not server_id or not name:
            return {"error": "server_id and name are required"}
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.create_text_channel(
            int(server_id), name, int(category_id) if category_id else None
        )
    
    async def handle_delete_channel_via_ws(self, data):
        channel_id = data.get("channel_id")
        if not channel_id:
            return {"error": "channel_id is required"}
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.delete_channel(int(channel_id))
    
    async def handle_add_reaction_via_ws(self, data):
        channel_id = data.get("channel_id")
        message_id = data.get("message_id")
        emoji = data.get("emoji")
        if not channel_id or not message_id or not emoji:
            return {"error": "channel_id, message_id, and emoji are required"}
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.add_reaction(int(channel_id), int(message_id), emoji)
    
    async def handle_remove_reaction_via_ws(self, data):
        channel_id = data.get("channel_id")
        message_id = data.get("message_id")
        emoji = data.get("emoji")
        if not channel_id or not message_id or not emoji:
            return {"error": "channel_id, message_id, and emoji are required"}
        if not self.discord_mcp or not self.discord_mcp.bot:
            return {"error": "Discord bot not initialized"}
        return await self.discord_mcp.remove_reaction(int(channel_id), int(message_id), emoji)

# Example usage
if __name__ == "__main__":
    import sys
    
    # Check if we want WebSocket support
    use_websocket = "--websocket" in sys.argv
    
    if use_websocket:
        server = StreamableHTTPMCPWithWebSocket()
    else:
        server = StreamableHTTPMCP()
    
    # Initialize and run the server
    async def run_server():
        await server.initialize()
        server.run()
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
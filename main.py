import os
import discord
from discord.ext import commands
import logging
from typing import List, Dict, Any, Optional
import asyncio
import argparse
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.models import InitializationOptions
from mcp.server.session import ServerSession
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discord-mcp")

load_dotenv()

class DiscordMCP(commands.Bot):
    def __init__(self):
        # Get token but don't validate here - let the startup handle it
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        @self.event
        async def on_ready():
            logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
            logger.info(f"Connected to {len(self.guilds)} servers")
            print("------")
        
        self._register_commands()
        
    
    async def start_bot(self, token: str):
        """Start the Discord bot with the provided token"""
        try:
            await self.start(token)
        except discord.LoginFailure:
            logger.error("Failed to login - invalid token")
            raise
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def send_message(self, channel_id: int, content: str):
        """Send a message to a specific channel"""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                message = await channel.send(content)
                logger.info(f"Message sent to channel {channel_id}: {content[:50]}...")
                return {
                    "status": "success",
                    "message": "Message sent",
                    "message_id": message.id
                }
            else:
                logger.warning(f"Channel not found: {channel_id}")
                return {"status": "error", "message": "Channel not found"}
        except discord.Forbidden:
            logger.error(f"Permission denied to send message to channel {channel_id}")
            return {"status": "error", "message": "Permission denied"}
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {"status": "error", "message": str(e)}
    
    async def read_messages(self, channel_id: int, limit: int = 10):
        """Read recent messages from a channel"""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                messages = []
                async for message in channel.history(limit=limit):
                    messages.append({
                        "id": message.id,
                        "author": str(message.author),
                        "content": message.content,
                        "timestamp": message.created_at.isoformat(),
                        "reactions": [str(reaction.emoji) for reaction in message.reactions]
                    })
                logger.info(f"Read {len(messages)} messages from channel {channel_id}")
                return {"messages": messages}
            logger.warning(f"Channel not found: {channel_id}")
            return {"error": "Channel not found"}
        except discord.Forbidden:
            logger.error(f"Permission denied to read messages from channel {channel_id}")
            return {"error": "Permission denied"}
        except Exception as e:
            logger.error(f"Failed to read messages: {e}")
            return {"error": str(e)}
    
    async def get_user_info(self, user_id: int):
        """Get information about a specific user"""
        try:
            user = self.get_user(user_id)
            if user:
                user_info = {
                    "id": user.id,
                    "name": user.name,
                    "discriminator": user.discriminator,
                    "bot": user.bot,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                logger.info(f"Retrieved info for user {user_id}")
                return user_info
            logger.warning(f"User not found: {user_id}")
            return {"error": "User not found"}
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {"error": str(e)}
    
    async def list_servers(self):
        """List all servers (guilds) the bot is in"""
        try:
            servers = [{
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count,
                "owner_id": guild.owner_id,
                "created_at": guild.created_at.isoformat() if guild.created_at else None
            } for guild in self.guilds]
            logger.info(f"Listed {len(servers)} servers")
            return servers
        except Exception as e:
            logger.error(f"Failed to list servers: {e}")
            return {"error": str(e)}
    
    async def create_text_channel(self, server_id: int, name: str, category_id: int = None):
        """Create a new text channel in a server"""
        try:
            guild = self.get_guild(server_id)
            if guild:
                category = guild.get_channel(category_id) if category_id else None
                channel = await guild.create_text_channel(
                    name=name,
                    category=category,
                    reason="Created via MCP"
                )
                logger.info(f"Created text channel '{name}' in server {server_id}")
                return {
                    "id": channel.id,
                    "name": channel.name,
                    "topic": channel.topic,
                    "category_id": channel.category_id
                }
            logger.warning(f"Server not found: {server_id}")
            return {"error": "Server not found"}
        except discord.Forbidden:
            logger.error(f"Permission denied to create channel in server {server_id}")
            return {"error": "Permission denied"}
        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
            return {"error": str(e)}
    
    async def delete_channel(self, channel_id: int):
        """Delete a channel"""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                await channel.delete(reason="Deleted via MCP")
                logger.info(f"Deleted channel {channel_id}")
                return {"status": "success"}
            logger.warning(f"Channel not found: {channel_id}")
            return {"error": "Channel not found"}
        except discord.Forbidden:
            logger.error(f"Permission denied to delete channel {channel_id}")
            return {"error": "Permission denied"}
        except Exception as e:
            logger.error(f"Failed to delete channel: {e}")
            return {"error": str(e)}
    
    async def add_reaction(self, channel_id: int, message_id: int, emoji: str):
        """Add a reaction to a message"""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                message = await channel.fetch_message(message_id)
                await message.add_reaction(emoji)
                logger.info(f"Added reaction {emoji} to message {message_id}")
                return {"status": "success"}
            logger.warning(f"Channel not found: {channel_id}")
            return {"error": "Channel not found"}
        except discord.NotFound:
            logger.warning(f"Message not found: {message_id}")
            return {"error": "Message not found"}
        except discord.Forbidden:
            logger.error(f"Permission denied to add reaction to message {message_id}")
            return {"error": "Permission denied"}
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
            return {"error": str(e)}
    
    async def add_multiple_reactions(self, channel_id: int, message_id: int, emojis: List[str]):
        """Add multiple reactions to a message"""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                message = await channel.fetch_message(message_id)
                for emoji in emojis:
                    await message.add_reaction(emoji)
                logger.info(f"Added reactions {emojis} to message {message_id}")
                return {"status": "success"}
            logger.warning(f"Channel not found: {channel_id}")
            return {"error": "Channel not found"}
        except discord.NotFound:
            logger.warning(f"Message not found: {message_id}")
            return {"error": "Message not found"}
        except discord.Forbidden:
            logger.error(f"Permission denied to add reactions to message {message_id}")
            return {"error": "Permission denied"}
        except Exception as e:
            logger.error(f"Failed to add reactions: {e}")
            return {"error": str(e)}
    
    async def remove_reaction(self, channel_id: int, message_id: int, emoji: str):
        """Remove a reaction from a message"""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                message = await channel.fetch_message(message_id)
                await message.remove_reaction(emoji, self.user)
                logger.info(f"Removed reaction {emoji} from message {message_id}")
                return {"status": "success"}
            logger.warning(f"Channel not found: {channel_id}")
            return {"error": "Channel not found"}
        except discord.NotFound:
            logger.warning(f"Message not found: {message_id}")
            return {"error": "Message not found"}
        except discord.Forbidden:
            logger.error(f"Permission denied to remove reaction from message {message_id}")
            return {"error": "Permission denied"}
        except Exception as e:
            logger.error(f"Failed to remove reaction: {e}")
            return {"error": str(e)}
    
    # Lists available channels in a server
    async def list_channels(self, server_id: int):
        """List all channels in a server"""
        try:
            guild = self.get_guild(server_id)
            if guild:
                channels = [{
                    "id": channel.id,
                    "name": channel.name,
                    "type": str(channel.type),
                    "category_id": channel.category_id
                } for channel in guild.channels]
                logger.info(f"Listed {len(channels)} channels in server {server_id}")
                return channels
            logger.warning(f"Server not found: {server_id}")
            return {"error": "Server not found"}
        except Exception as e:
            logger.error(f"Failed to list channels: {e}")
            return {"error": str(e)}
    
    def _register_commands(self):
        """Register bot commands if needed"""
        @self.command(name="ping")
        async def ping(ctx):
            await ctx.send("Pong!")
            logger.info(f"Ping command used by {ctx.author} in {ctx.channel}")

        @self.slash_command(name="servers", description="List servers the bot is in")
        async def servers(ctx):
            servers = await self.list_servers()
            if isinstance(servers, dict) and "error" in servers:
                await ctx.respond(f"Error: {servers['error']}")
            else:
                response = "\n".join([f"{srv['name']} (ID: {srv['id']}, Members: {srv['member_count']})" for srv in servers])
                await ctx.respond(f"Servers:\n{response}")
            logger.info(f"Servers command used by {ctx.author} in {ctx.channel}")
        
        @self.slash_command(name="userinfo", description="get user info")
        async def userinfo(ctx, user: discord.Member):
            user_info = await self.get_user_info(user.id)
            if isinstance(user_info, dict) and "error" in user_info:
                await ctx.respond(f"Error: {user_info['error']}")
            else:
                response = (f"User Info:\n"
                            f"Name: {user_info['name']}#{user_info['discriminator']}\n"
                            f"ID: {user_info['id']}\n"
                            f"Bot: {user_info['bot']}\n"
                            f"Created At: {user_info['created_at']}")
                await ctx.respond(response)
    
    

# Global bot instance
bot_instance: Optional[DiscordMCP] = None

# Initialize MCP server with proper configuration
mcp = FastMCP("discord-mcp")

@mcp.tool()
async def send_message(channel_id: int, content: str) -> Dict[str, Any]:
    """Send a message to a specific Discord channel.
    
    Args:
        channel_id: The ID of the Discord channel to send the message to
        content: The message content to send
        
    Returns:
        Dictionary with status and message details or error information
    """
    if not bot_instance:
        return {"status": "error", "message": "Discord bot not initialized"}
    
    try:
        channel = bot_instance.get_channel(channel_id)
        if channel:
            message = await channel.send(content)
            logger.info(f"Message sent to channel {channel_id}: {content[:50]}...")
            return {
                "status": "success",
                "message": "Message sent",
                "message_id": message.id
            }
        else:
            logger.warning(f"Channel not found: {channel_id}")
            return {"status": "error", "message": "Channel not found"}
    except discord.Forbidden:
        logger.error(f"Permission denied to send message to channel {channel_id}")
        return {"status": "error", "message": "Permission denied"}
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def read_messages(channel_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Read recent messages from a Discord channel.
    
    Args:
        channel_id: The ID of the Discord channel to read messages from
        limit: Maximum number of messages to retrieve (default: 10, max: 100)
        
    Returns:
        List of message dictionaries or empty list on error
    """
    if not bot_instance:
        return [{"error": "Discord bot not initialized"}]
    
    try:
        channel = bot_instance.get_channel(channel_id)
        if channel:
            messages = []
            async for message in channel.history(limit=min(max(1, limit), 100)):
                messages.append({
                    "id": message.id,
                    "author": str(message.author),
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "reactions": [str(reaction.emoji) for reaction in message.reactions]
                })
            logger.info(f"Read {len(messages)} messages from channel {channel_id}")
            return messages
        else:
            logger.warning(f"Channel not found: {channel_id}")
            return [{"error": "Channel not found"}]
    except discord.Forbidden:
        logger.error(f"Permission denied to read messages from channel {channel_id}")
        return [{"error": "Permission denied"}]
    except Exception as e:
        logger.error(f"Failed to read messages: {e}")
        return [{"error": str(e)}]

@mcp.resource("users://{user_id}/info")
async def user_info_resource(user_id: int) -> Dict[str, Any]:
    """
    Get information about a specific Discord user.
    
    Args:
        user_id: The ID of the user to fetch information for
        
    Returns:
        Dictionary containing user information or error details
    """
    if not bot_instance:
        return {"error": "Discord bot not initialized"}
    
    try:
        user = await bot_instance.fetch_user(user_id)
        if user:
            user_info = {
                "id": user.id,
                "name": user.name,
                "discriminator": user.discriminator,
                "bot": user.bot,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            logger.info(f"Retrieved info for user {user_id}")
            return user_info
        else:
            logger.warning(f"User not found: {user_id}")
            return {"error": "User not found"}
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        return {"error": str(e)}

@mcp.resource("servers://list")
async def list_servers_resource() -> List[Dict[str, Any]]:
    """List all Discord servers (guilds) the bot is in.
    
    Returns:
        List of server dictionaries or error information
    """
    if not bot_instance:
        return [{"error": "Discord bot not initialized"}]
    
    try:
        servers = []
        for guild in bot_instance.guilds:
            servers.append({
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count,
                "owner_id": guild.owner_id,
                "created_at": guild.created_at.isoformat() if guild.created_at else None
            })
        logger.info(f"Listed {len(servers)} servers")
        return servers
    except Exception as e:
        logger.error(f"Failed to list servers: {e}")
        return [{"error": str(e)}]

@mcp.resource("channels://{server_id}/list")
async def list_channels_resource(server_id: int) -> List[Dict[str, Any]]:
    """List all channels in a Discord server.
    
    Args:
        server_id: The ID of the server to list channels from
        
    Returns:
        List of channel dictionaries or error information
    """
    if not bot_instance:
        return [{"error": "Discord bot not initialized"}]
    
    try:
        guild = bot_instance.get_guild(server_id)
        if guild:
            channels = []
            for channel in guild.channels:
                channels.append({
                    "id": channel.id,
                    "name": channel.name,
                    "type": str(channel.type),
                    "category_id": channel.category_id
                })
            logger.info(f"Listed {len(channels)} channels in server {server_id}")
            return channels
        else:
            logger.warning(f"Server not found: {server_id}")
            return [{"error": "Server not found"}]
    except Exception as e:
        logger.error(f"Failed to list channels: {e}")
        return [{"error": str(e)}]

@mcp.tool()
async def create_text_channel(server_id: int, name: str, ctx: Context[ServerSession, None], category_id: int = None) -> Dict[str, Any]:
    """Create a new text channel in a Discord server.
    
    Args:
        server_id: The ID of the server to create the channel in
        name: The name of the new channel
        category_id: Optional ID of the category to place the channel in
        ctx: MCP context for logging and session management
        
    Returns:
        Dictionary with channel details or error information
    """
    await ctx.info(f"Creating text channel '{name}' in server {server_id}")
    if not bot_instance:
        await ctx.error("Discord bot not initialized")
        return {"error": "Discord bot not initialized"}
    
    result = await bot_instance.create_text_channel(server_id, name, category_id)
    if "error" not in result:
        await ctx.info(f"Channel '{name}' created with ID {result.get('id')}")
    else:
        await ctx.error(f"Failed to create channel: {result.get('error')}")
    return result

@mcp.tool()
async def delete_channel(channel_id: int, ctx: Context[ServerSession, None]) -> Dict[str, Any]:
    """Delete a Discord channel.
    
    Args:
        channel_id: The ID of the channel to delete
        ctx: MCP context for logging and session management
        
    Returns:
        Dictionary with status or error information
    """
    await ctx.info(f"Deleting channel {channel_id}")
    if not bot_instance:
        await ctx.error("Discord bot not initialized")
        return {"error": "Discord bot not initialized"}
    
    result = await bot_instance.delete_channel(channel_id)
    if result.get("status") == "success":
        await ctx.info(f"Channel {channel_id} deleted successfully")
    else:
        await ctx.error(f"Failed to delete channel: {result.get('error')}")
    return result

@mcp.tool()
async def add_reaction(channel_id: int, message_id: int, emoji: str, ctx: Context[ServerSession, None]) -> Dict[str, Any]:
    """Add a reaction to a Discord message.
    
    Args:
        channel_id: The ID of the channel containing the message
        message_id: The ID of the message to react to
        emoji: The emoji to add as a reaction
        ctx: MCP context for logging and session management
        
    Returns:
        Dictionary with status or error information
    """
    await ctx.info(f"Adding reaction {emoji} to message {message_id} in channel {channel_id}")
    if not bot_instance:
        await ctx.error("Discord bot not initialized")
        return {"error": "Discord bot not initialized"}
    
    result = await bot_instance.add_reaction(channel_id, message_id, emoji)
    if result.get("status") == "success":
        await ctx.info(f"Reaction {emoji} added to message {message_id}")
    else:
        await ctx.error(f"Failed to add reaction: {result.get('error')}")
    return result

@mcp.tool()
async def add_multiple_reactions(channel_id: int, message_id: int, emojis: List[str], ctx: Context[ServerSession, None]) -> Dict[str, Any]:
    """Add multiple reactions to a Discord message.
    
    Args:
        channel_id: The ID of the channel containing the message
        message_id: The ID of the message to react to
        emojis: List of emojis to add as reactions
        ctx: MCP context for logging and session management
        
    Returns:
        Dictionary with status or error information
    """
    await ctx.info(f"Adding reactions {emojis} to message {message_id} in channel {channel_id}")
    if not bot_instance:
        await ctx.error("Discord bot not initialized")
        return {"error": "Discord bot not initialized"}
    
    result = await bot_instance.add_multiple_reactions(channel_id, message_id, emojis)
    if result.get("status") == "success":
        await ctx.info(f"Reactions {emojis} added to message {message_id}")
    else:
        await ctx.error(f"Failed to add reactions: {result.get('error')}")
    return result

@mcp.tool()
async def remove_reaction(channel_id: int, message_id: int, emoji: str, ctx: Context[ServerSession, None]) -> Dict[str, Any]:
    """Remove a reaction from a Discord message.
    
    Args:
        channel_id: The ID of the channel containing the message
        message_id: The ID of the message to remove reaction from
        emoji: The emoji to remove from reactions
        ctx: MCP context for logging and session management
        
    Returns:
        Dictionary with status or error information
    """
    await ctx.info(f"Removing reaction {emoji} from message {message_id} in channel {channel_id}")
    if not bot_instance:
        await ctx.error("Discord bot not initialized")
        return {"error": "Discord bot not initialized"}
    
    result = await bot_instance.remove_reaction(channel_id, message_id, emoji)
    if result.get("status") == "success":
        await ctx.info(f"Reaction {emoji} removed from message {message_id}")
    else:
        await ctx.error(f"Failed to remove reaction: {result.get('error')}")
    return result

@mcp.resource("channels://{server_id}/list")
async def list_channels_resource(server_id: int) -> List[Dict[str, Any]]:
    """List all channels in a Discord server.
    
    Args:
        server_id: The ID of the server to list channels from
        
    Returns:
        List of channel dictionaries or error information
    """
    if not bot_instance:
        return [{"error": "Discord bot not initialized"}]
    
    result = await bot_instance.list_channels(server_id)
    return result

async def main():
    """Main function to start the Discord MCP server with configurable transport"""
    global bot_instance
    
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Discord MCP Server with Multiple Transport Options")
        parser.add_argument("--transport", choices=["stdio", "http", "streamable-http", "sse"], default="stdio", help="Transport type")
        parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP transport")
        parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport")
        parser.add_argument("--path", default="/mcp", help="Path for HTTP transport")
        args = parser.parse_args()
        
        logger.info("Starting Discord MCP server...")
        
        # Check for valid Discord token
        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token or discord_token == "your_discord_bot_token_here":
            logger.warning("No valid DISCORD_TOKEN found. MCP tools will be available but Discord functionality will not work.")
            logger.warning("Please set a valid DISCORD_TOKEN in your .env file to enable Discord integration.")
            bot_instance = None
        else:
            # Initialize and start the Discord bot
            bot_instance = DiscordMCP()
            # Start bot in background
            await bot_instance.run(discord_token)
            logger.info("Discord bot started successfully")

        # Choose transport based on arguments
        if args.transport == "sse":
            # Start MCP server with SSE transport (HTTP-based)
            logger.info(f"MCP server ready for SSE communication on {args.host}:{args.port}{args.path}")
            await mcp.run_http_async(
                host=args.host,
                port=args.port,
                path=args.path
            )
        else:
            # Start MCP server with stdio transport
            logger.info("MCP server ready for stdio communication")
            await mcp.serve_stdio()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Discord MCP server...")
        if bot_instance:
            await bot_instance.close()
    except Exception as e:
        logger.error(f"Failed to start Discord MCP server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
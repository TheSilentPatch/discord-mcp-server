import os
import discord
from discord.ext import commands
import logging
from typing import List, Dict, Any
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discord-mcp")

# Discord MCP Server Implementation
class DiscordMCP:
    def __init__(self):
        self.bot = None
        self.token = os.getenv("DISCORD_TOKEN")
        
        if not self.token:
            logger.error("DISCORD_TOKEN environment variable is required")
            raise ValueError("DISCORD_TOKEN environment variable is required")
        
    async def start(self):
        """Initialize and start the Discord bot"""
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            
            self.bot = commands.Bot(command_prefix="!", intents=intents)
            
            # Register event handlers
            @self.bot.event
            async def on_ready():
                logger.info(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
                logger.info(f"Connected to {len(self.bot.guilds)} servers")
                
            # Start the bot
            await self.bot.start(self.token)
            
        except discord.LoginFailure:
            logger.error("Failed to login - invalid token")
            raise
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def send_message(self, channel_id: int, content: str):
        """Send a message to a specific channel"""
        try:
            channel = self.bot.get_channel(channel_id)
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
            channel = self.bot.get_channel(channel_id)
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
            user = self.bot.get_user(user_id)
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
            } for guild in self.bot.guilds]
            logger.info(f"Listed {len(servers)} servers")
            return servers
        except Exception as e:
            logger.error(f"Failed to list servers: {e}")
            return {"error": str(e)}
    
    async def create_text_channel(self, server_id: int, name: str, category_id: int = None):
        """Create a new text channel in a server"""
        try:
            guild = self.bot.get_guild(server_id)
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
            channel = self.bot.get_channel(channel_id)
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
            channel = self.bot.get_channel(channel_id)
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
    
    async def remove_reaction(self, channel_id: int, message_id: int, emoji: str):
        """Remove a reaction from a message"""
        try:
            channel = self.bot.get_channel(channel_id)
            if channel:
                message = await channel.fetch_message(message_id)
                await message.remove_reaction(emoji, self.bot.user)
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

# Example usage
if __name__ == "__main__":
    try:
        # Initialize the MCP server
        mcp = DiscordMCP()
        print("Discord MCP server implementation ready")
        
        # To start the bot, you would use:
        # asyncio.run(mcp.start())
        
        # To start both Discord bot and HTTP server together, use:
        # python start_server.py
        
    except Exception as e:
        logger.error(f"Failed to initialize Discord MCP: {e}")
        print(f"Error: {e}")
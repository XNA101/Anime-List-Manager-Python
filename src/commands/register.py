import discord;
from database.serverDetails import *;

async def register_command(interaction: discord.Interaction, channel: discord.channel.TextChannel):
  serverName = interaction.guild.name;
  serverId = str(interaction.guild.id);
  channelId = str(channel.id);
  channelName = channel.name;

  if not interaction.permissions.administrator:
    await interaction.response.send_message(f"This command is restricted to Administrators only.");
    return
  
  status = addServerDetail(serverName, channelId, serverId, channelName);
  
  if status == "Not Done":
    await interaction.response.send_message(f"Sorry an error occurred. If this persists please contact the creator");
    return
  
  if status == "Already registered":
    await interaction.response.send_message(f"**{channelName}** is already registered");
    return
  
  if status == "Done":
    await interaction.response.send_message(f"**{channelName}** has been registered. Commands work in **{channelName}**");
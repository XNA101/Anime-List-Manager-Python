import discord;

Embed = discord.Embed;

def embedCreator(title, color, imageUrl, footerText = None, description = None, footerUrl = None):
  if footerText and footerUrl:
    embed = Embed(title=title, description=description, color=color)
    embed.set_image(url=imageUrl)
    embed.set_footer(text=footerText, icon_url=footerUrl)
    
    return embed
  
  if footerText and not footerUrl:
    embed = Embed(title=title, description=description, color=color)
    embed.set_image(url=imageUrl)
    embed.set_footer(text=footerText)
    
    return embed
  
  if not footerText and not footerUrl:
    embed = Embed(title=title, description=description, color=color)
    embed.set_thumbnail(url=imageUrl)

    return embed
  
  
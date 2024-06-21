import discord;
from helpers.embedCreator import *;

# class create_button(discord.ui.View):
#   def __init__(self, _label: str, _style: str):
#     super().__init__();
#     self._label = _label;
#     self._style = _style;

#   @discord.ui.button(label=)

class create_button(discord.ui.View):
  def __init__(self, List: dict, currentIndex: int, embed: discord.embeds.Embed, createDescription, getCurrentEmbed, createFooterText = None, ):
    super().__init__();
    self.List = List["list"]
    self.format = List["format"]
    self.createDescription = createDescription
    self.createFooterText = createFooterText
    self.getCurrentEmbed = getCurrentEmbed
    self.currentIndex = currentIndex
    self.embed = embed

  def get_current_embed(self):
      embed = self.getCurrentEmbed(self)
      return embed

  @discord.ui.button(label="Back", custom_id="back", style=discord.ButtonStyle.primary)
  async def BackBtn(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.currentIndex = (self.currentIndex - 1) % len(self.List);
    embed = self.get_current_embed();
    await interaction.response.edit_message(embeds=[embed], view=self)

  @discord.ui.button(label="Next", custom_id="next", style=discord.ButtonStyle.primary)
  async def NextBtn(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.currentIndex = (self.currentIndex + 1) % len(self.List);
    embed = self.get_current_embed();
    await interaction.response.edit_message(embeds=[embed], view=self)

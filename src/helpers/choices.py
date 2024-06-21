from discord import app_commands;

Choice = app_commands.Choice;

status_choices = [
  Choice(name="Current", value="CURRENT"),
  Choice(name="Planning", value="PLANNING"),
  Choice(name="Completed", value="COMPLETED"),
  Choice(name="Dropped", value="DROPPED"),
  Choice(name="Paused", value="PAUSED"),
  Choice(name="Repeating", value="REPEATING")
]

type_choices = [
  Choice(name="Anime", value="ANIME"),
  Choice(name="Manga", value="MANGA")
]

format_choices = [
  Choice(name="TV", value="TV"),
  Choice(name="Manga", value="MANGA"),
  Choice(name="Movie", value="MOVIE"),
  Choice(name="Special", value="SPECIAL"),
  Choice(name="OVA", value="OVA"),
  Choice(name="ONA", value="ONA"),
  Choice(name="Music", value="MUSIC"),
  Choice(name="Novel", value="NOVEL"),
  Choice(name="One Shot", value="ONE_SHOT")
]

genre_choices = [
  Choice(name="Action", value="Action"),
  Choice(name="Adventure", value="Adventure"),
  Choice(name="Comedy", value="Comedy"),
  Choice(name="Drama", value="Drama"),
  Choice(name="Ecchi", value="Ecchi"),
  Choice(name="Fantasy", value="Fantasy"),
  Choice(name="Horror", value="Horror"),
  Choice(name="Mahou Shoujo", value="Mahou Shoujo"),
  Choice(name="Mecha", value="Mecha"),
  Choice(name="Music", value="Music"),
  Choice(name="Mystery", value="Mystery"),
  Choice(name="Psychological", value="Psychological"),
  Choice(name="Romance", value="Romance"),
  Choice(name="Sci-Fi", value="Sci-Fi"),
  Choice(name="Slice of Life", value="Slice of Life"),
  Choice(name="Sports", value="Sports"),
  Choice(name="Supernatural", value="Supernatural"),
  Choice(name="Thriller", value="Thriller")
]
import functools
import math
from discord.ext.commands import Context
from src.util.embed_func import msg_embed
from src.util.room_func import get_guild_room_create_channel
from src.util import database
from src.lang.lang import get_locale_fm
import discord

class ProgressBar():
  '''
  The class used for handling progress bars
  '''
  def __init__(self, width=None, step=None, title=None, progress_char=None, other_char=None):
    #default values
    if width == None: self.width = 20
    if step == None: self.step = 0.01
    self.set_title(title)
    if progress_char == None: self.progress_char="█"
    if other_char == None: self.other_char = "-"

    #ensure all of correct types
    if not isinstance(self.width, int): raise TypeError("width must be an int")
    if not (isinstance(self.step, float) or isinstance(step, int)): raise TypeError("step must be a float")
    if not isinstance(self.progress_char, str): raise TypeError("progress_char must string of length 1")
    if not isinstance(self.other_char, str): raise TypeError("other_char must be a string of length 1")

    #parameter constraints
    if not 0.01 <= self.step <= 1: raise ValueError("step must be in range: 0.01 <= step <= 1")
    if len(self.progress_char) != 1: raise ValueError("progress_char must be a string of length 1")
    if len(self.other_char) != 1: raise ValueError("other_char must be a string of length 1")
    self.progress = 0
    
  def set_progress(self, progress):
    if progress < 0 or progress > 1: raise ValueError("Progress must be between 0 and 1")
    self.progress = progress

  def set_title(self, title:str):
    if title == None: 
        self.title = " "
    else:
        self.title = " " + title + " "
    
  def __str__(self):
    progress = math.floor(self.progress * self.width)
    remaining = (self.width - progress)
    result =  self.progress_char * progress + self.other_char * remaining + self.title + str(round(self.progress*100)) + "%" 
    return result

def requires(room: bool = False, users_registered: bool = False):
    """
    Requrires decorator - used for checking prerequisites for commands
    * users registered - all users must be registered before command usage
    * room - whether the command needs to be in a room for usage ( only applies if rooms are enabled )
    """

    def decorator(function):
        async def wrapper(*args, **kwargs):
            ctx, *_ = args
            ctx: Context
            user_data = database.user_data.find_one({"_id": ctx.author.id})

            if user_data is None:
                lang = "en"
            else:
                lang = user_data["lang"]

            # ensure all users in call are registered before proceeding
            if users_registered:
                if user_data is None:
                    await msg_embed(ctx, get_locale_fm(lang, "author_not_registered"))
                    return

                for arg in _:
                    if isinstance(arg, discord.Member):
                        if database.user_data.find_one({"_id": arg.id}) is None:
                            await msg_embed(
                                ctx,
                                get_locale_fm(lang, "user_not_registered", arg.name),
                            )
                            return

            lang = user_data["lang"]

            if room:
                guild_data = database.guild_data.find_one({"_id": ctx.guild.id})

                HAS_GUILD_DATA = (
                    guild_data is not None
                    and guild_data["unbox_room_creation_channel_id"] is not None
                )
                if HAS_GUILD_DATA:
                    INVALID_PARENT_CHANNEL = (
                        hasattr(ctx.channel, "parent")
                        and ctx.channel.parent.id
                        != guild_data["unbox_room_creation_channel_id"]
                    )
                    NO_PARENT_CHANNEL = hasattr(ctx.channel, "parent") is False

                    if INVALID_PARENT_CHANNEL or NO_PARENT_CHANNEL:
                        channel = get_guild_room_create_channel(ctx.guild, guild_data)
                        if channel is not None:
                            await msg_embed(
                                ctx,
                                get_locale_fm(
                                    lang, "command_error.room", channel.mention
                                ),
                            )
                            return

            await function(*args, **kwargs)

        return wrapper

    return decorator

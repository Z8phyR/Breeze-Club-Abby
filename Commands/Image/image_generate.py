import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import base64
import requests
from dotenv import load_dotenv
import os
import math

ABBY_RUN = "<a:Abby_run:1135375927589748899>"
ABBY_IDLE = "<a:Abby_idle:1135376647495884820>"
UP_ARROW = ":arrow_up:"
NEXT = ":arrow_forward:"
PREV = ":arrow_backward:"

load_dotenv()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
DAY = 86400

url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-beta-v2-2-2/text-to-image"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {STABILITY_API_KEY}",
}


# Create a mapping of style presets to their corresponding variables
style_presets = {
    "3d-model": "3d-model",
    "analog-film": "analog-film",
    "anime": "anime",
    "cinematic": "cinematic",
    "comic-book": "comic-book",
    "digital-art": "digital-art",
    "enhance": "enhance",
    "fantasy-art": "fantasy-art",
    "isometric": "isometric",
    "line-art": "line-art",
    "low-poly": "low-poly",
    "modeling-compound": "modeling-compound",
    "neon-punk": "neon-punk",
    "origami": "origami",
    "photographic": "photographic",
    "pixel-art": "pixel-art",
    "tile-texture": "tile-texture"
}

#User can use the command only 1 times a day
@commands.cooldown(1, DAY, BucketType.user)
@commands.command()
async def imagine(ctx,style_preset="enhance", *, text):
    await ctx.typing()
    processing = await ctx.send(f"{ABBY_RUN} Generating image...")
    processing.add_reaction(ABBY_RUN)
        # Check if the style preset is valid and select it, otherwise default to "enhance"
    if style_preset == "help":
        await ctx.send("Available style presets: `3d-model, analog-film, anime, cinematic, comic-book, digital-art, enhance, fantasy-art, isometric, line-art, low-poly, modeling-compound, neon-punk, origami, photographic, pixel-art, tile-texture`")
        ctx.command.reset_cooldown(ctx)
        return
    
    style_preset = style_preset.lower()
    if style_preset not in style_presets:
        style_preset = "enhance"

    body = {
        "width": 512,
        "height": 512,
        "steps": 50,
        "seed": 0,
        "cfg_scale": 7,
        "samples": 1,
        "style_preset": style_presets[style_preset],
        "text_prompts": [
            {
                "text": text,

                "weight": 1
            }
        ],
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    for i, image in enumerate(data["artifacts"]):
        with open(f"/home/Abby_BreezeClub/Images/generate_image.png", "wb") as f:
            f.write(base64.b64decode(image["base64"]))

        file = discord.File(f"/home/Abby_BreezeClub/Images/generate_image.png")
        await processing.delete()
        sent_message = await ctx.send(file=file)
        
        # Add Reaction to the message
        await sent_message.add_reaction(ABBY_IDLE)
        await sent_message.add_reaction(UP_ARROW)
        await sent_message.add_reaction(NEXT)
        
        #Keep the ID of the message
        message_id = sent_message.id


@imagine.error
async def imagine_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide some text to generate an image.")
        ctx.command.reset_cooldown(ctx)  # Don't count it as a cooldown
    elif isinstance(error, commands.CommandOnCooldown):
        user_display_name = ctx.author.mention
        retry_after_hours = math.ceil(error.retry_after / 3600)  # Convert seconds to hours
        await ctx.send(f"Sorry {user_display_name}, this can only be used once per day! Please wait {retry_after_hours} hours before using this command again.")
    else:
        raise error

imagine.description = """
Generate an image from text using the ABBY AI API.
Available style presets: `3d-model, analog-film, anime, cinematic, comic-book, digital-art, enhance, fantasy-art, isometric, line-art, low-poly, modeling-compound, neon-punk, origami, photographic, pixel-art, tile-texture`
How to use:
    `!imagine <style_preset> <text>`
    `!imagine <text>`

*Note: If no style preset is provided, the default is "enhance"*
**Cooldown: 1 use per day** (Higher uses for higher levels))    
"""

@commands.cooldown(1, DAY, BucketType.user)
@commands.command()
async def imgimg(ctx, *, text):
    await ctx.typing()
    processing = await ctx.send(f"{ABBY_RUN} Generating image...")
    # Fetch the last image generated by Abby (the bot)
    messages = []
    async for message in ctx.channel.history(limit=30):
        messages.append(message)


    last_image = None
    for message in messages:
        if message.author.bot:
            continue
        for attachment in message.attachments:
            if attachment.content_type.startswith("image"):
                # await ctx.send(f"Found attachment: {attachment.url}")
                last_image = attachment.url
                break
        if last_image:
            break

    if not last_image:
        await processing.edit("No user image found in the last 30 messages.")
        return
    
    # file_path="/home/Abby_BreezeClub/Images/abby.png"

    try:
        engine_id = "stable-diffusion-xl-1024-v1-0"
        api_host = os.getenv("API_HOST", "https://api.stability.ai")
        api_key = os.getenv("STABILITY_API_KEY")

        if api_key is None:
            raise Exception("Missing Stability API key.")
        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/image-to-image",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            files={
                "init_image": requests.get(last_image).content
            },
            data={
                "image_strength": 0.35,
                "init_image_mode": "IMAGE_STRENGTH",
                "text_prompts[0][text]": f"{text}",
                "cfg_scale": 7,
                "samples": 1,
                "steps": 30,
            }
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))
        data = response.json()
        
        for i, image in enumerate(data["artifacts"]):
            with open(f"/home/Abby_BreezeClub/Images/edited_image.png", "wb") as f:
                f.write(base64.b64decode(image["base64"]))

        file = discord.File(f"/home/Abby_BreezeClub/Images/edited_image.png")
        await processing.delete()
        sent_message = await ctx.send(file=file)
        await sent_message.add_reaction(ABBY_IDLE)

    except Exception as e:
            error_message = f"Your image is improper size - Your image should be 1024x1024 pixels minimum and be a square. - Please upload a new image."
            await processing.edit(error_message) 

@imgimg.error
async def imgimg_error(ctx, error):
    user_display_name = ctx.author.mention
    retry_after_hours = math.ceil(error.retry_after / 3600)
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Sorry {user_display_name}! This can onle be used once per day! You've already used yours up. Please wait {retry_after_hours} hours before using this command again.")
    else:
        raise error    

imgimg.description = """
Generate an image from previous image using the ABBY AI API.
How to use:
    `!imgimg <text>`
This command will use the last image sent in the channel.
And will generate a new image based on the text provided.
Exceptions:
    - If the last image sent in the channel is not a square, the command will fail.
    - If the last image sent in the channel is not 1024x1024px or larger, the command will fail.


**Cooldown: 1 use per day** (Higher uses for higher levels))    
"""

@commands.cooldown(1, DAY, BucketType.user)
@commands.command()
async def upscale(ctx):
    await ctx.typing()
    processing = await ctx.send(f"{ABBY_RUN} Upscaling image...")
        # Fetch the last 10 messages in the channel
    messages = []
    async for message in ctx.channel.history(limit=30):
        messages.append(message)  

    last_image = None
    for message in messages:
        if message.author.bot:
            continue
        for attachment in message.attachments:
            if attachment.content_type.startswith("image"):
                # await ctx.send(f"Found attachment: {attachment.url}")
                last_image = attachment.url
                break
        if last_image:
            break

    if not last_image:
        await processing.edit("No user image found in the last 30 messages.")
        return
    try:
        engine_id = "esrgan-v1-x2plus"
        api_host = os.getenv("API_HOST", "https://api.stability.ai")
        api_key = os.getenv("STABILITY_API_KEY")

        if api_key is None:
            raise Exception("Missing Stability API key.")


        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/image-to-image/upscale",
            headers={
                "Accept": "image/png",
                "Authorization": f"Bearer {api_key}"
            },
            files={
                "image":requests.get(last_image).content
            },
            data={
                "width": 1024,
            }
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        with open(f"/home/Abby_BreezeClub/Images/upscaled_image.png", "wb") as f:
            f.write(response.content)
        
        file = discord.File(f"/home/Abby_BreezeClub/Images/upscaled_image.png")
        await processing.delete()
        sent_message = await ctx.send(file=file)
        await sent_message.add_reaction(ABBY_IDLE)    
    except Exception as e:
            error_message = f"Your image is improper size - Your image should be 512x512px or smaller and be a square. - Please upload a new image."
            print(str(e))
            await processing.edit(error_message)


def setup(bot):
    bot.add_command(imagine)
    bot.add_command(imgimg)
    bot.add_command(upscale)
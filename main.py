import discord, config, os, dotenv, random, string, shutil
from Wandbox import WandboxAsync as Wandbox

dotenv.load_dotenv()

client = discord.Client()

if not os.path.isdir("temp"):
    os.mkdir("temp")

@client.event
async def on_ready():
    print("Successfully connected to discord as", client.user)

@client.event
async def on_message(message):
    author  = message.author
    channel = message.channel
    content = message.content

    if not content.startswith(config.prefix):
        return

    command_raw = content[len(config.prefix):].strip().split()
    command = command_raw[0]

    if command == "help":
        embed = getEmbed("Help", "List of all commands")
        embed.add_field(
            name = f"`{config.prefix}lang` OR `{config.prefix}languages`",
            value = "Get a list of available languages.",
            inline = False
        )
        embed.add_field(
            name = f"`{config.prefix}run <language> <code>`",
            value = "Compile & Run Code",
            inline = False
        )
        embed.add_field(
            name = f"`{config.prefix}help`",
            value = "Get the list of commands",
            inline = False
        )
        embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/818043664835149894/818069414409928734/info.png")
        return await channel.send(embed = embed)

    elif command in ("lang", "languages",):
        embed = getEmbed("Available Languages")
        for language, data in config.languages.items():
            aliases = ", ".join(["`" + i + "`" for i in ([language] + data["aliases"])])
            embed.add_field(
                name = data["emoji"] + " " + data["name"],
                value = f"Aliases: {aliases}",
                inline = False
            )
        embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/818043664835149894/818070074908213258/code_1.png")
        return await channel.send(embed = embed)

    elif command == "run":
        if len(command_raw) < 3:
            embed = getEmbed(
                "Invalid Command",
                f"Correct Use: `{config.prefix}run <language> ```<code>``` `"
            )
            embed.add_field(
                name = "Example",
                value = f"""
{config.prefix}run javascript
\```
function showMessage() {{
    console.log("Hello")
}}

showMessage();
```
""",
                inline = False
            )
            return await channel.send(embed = embed)

        language = command_raw[1].lower()

        languageName = None
        compiler = None

        for langName, data in config.languages.items():
            if language == langName or language in data["aliases"]:
                languageName = data["name"]
                compiler = data["compiler"]
                break

        if not languageName:
            embed = getEmbed(
                "Invalid Language",
                f"This language isn't supported yet. Use `{config.prefix}languages` to get the list of available languages."
            )
            return await channel.send(embed = embed)
        
        code = message.content[message.content.index(command_raw[1]) + len(command_raw[1]):].strip().strip("```")
        
        embed = getEmbed(
            "Executing your Code...",
            f"""**Language:** {data["emoji"]} {languageName}
```
{code}
```
""",
        )
        embed.set_thumbnail(url = "https://cdn.discordapp.com/emojis/752440820036272139.gif")
        loadingMessage = await channel.send(embed = embed)

        response = await Wandbox.compileCode(compiler, code)
        message = response["message"]

        fileName = None
        if len(message) > 1500:
            directoryName = f"temp/{getRandomString()}"
            os.mkdir(directoryName)
            fileName = f"{directoryName}/output.txt"

            open(fileName, "w+").write(message)

            message = message[:1500]
            message += "\nMESSAGE TOO LONG!"

        if response["status"] == "success":
            embed = getEmbed(
                "Successfully Executed",
                f"Output: ```\n{message}\n```",
                0x00ff00
            )
            embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/818043664835149894/818064800365019176/check.png")
            await loadingMessage.edit(embed = embed)

        elif response["status"] == "fail":
            embed = getEmbed(
                "Error",
                f"```\n{message}\n```",
                0xff0000
            )
            embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/818043664835149894/818064809874292786/cancel.png")
            await loadingMessage.edit(embed = embed)

        elif response["status"] == "killed":
            embed = getEmbed(
                "Program Killed",
                f"```\n{message}\n```",
                0xff0000
            )
            embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/818043664835149894/818071433111928912/warning.png")
            await loadingMessage.edit(embed = embed)

        if fileName:
            await channel.send(
                "The output message was too long. Here's the complete output in text format:",
                file = discord.File(fileName)
            )
            shutil.rmtree(directoryName)

def getEmbed(title, description = "", color = config.themeColor):
    return discord.Embed(
        title = title,
        description = description,
        color = color
    )

def getRandomString(length = 100):
    return "".join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])

client.run(os.getenv("BOT_TOKEN"))

import discord
from discord.ext import commands
import re

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_ROLE_IDS = [
    1250114225616064512,
]

# Словарь для хранения текущего языка пользователя
user_languages = {}  # user_id: 'ru'/'en'
default_language = 'ru'  # Язык по умолчанию

# Тексты на разных языках
translations = {
    'ru': {
        'no_role': "У вас нет прав для использования этой команды.",
        'no_message': "Пожалуйста, введите сообщение после команды. Например: `!anns привет` или `!anns #канал привет`",
        'channel_sent': "Сообщение отправлено в канал {channel}.",
        'channel_not_found': "Указанный канал не найден.",
        'no_permission': "У меня нет прав на отправку сообщений в канал {channel}.",
    },
    'en': {
        'no_role': "You do not have permission to use this command.",
        'no_message': "Please enter a message after the command. For example: `!anns hello` or `!anns #channel hello`",
        'channel_sent': "Message sent to channel {channel}.",
        'channel_not_found': "The specified channel was not found.",
        'no_permission': "I don't have permission to send messages to channel {channel}.",
    }
}


def get_translation(user_id, key):
    """Получает перевод для пользователя."""
    language = user_languages.get(user_id, default_language)
    return translations[language][key]


def has_allowed_role():
    async def predicate(ctx):
        return any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)

    return commands.check(predicate)


@bot.command()
async def lang(ctx, language):
    """Переключает язык пользователя."""
    if language in ['ru', 'en']:
        user_languages[ctx.author.id] = language
        await ctx.send(f"Язык переключен на {language}.")
    else:
        await ctx.send("Неверный язык. Используйте 'ru' или 'en'.")


@bot.command()
@has_allowed_role()
async def anns(ctx, *, message=""):
    if not message:
        await ctx.send(get_translation(ctx.author.id, 'no_message'))
        return

    channel_mention_pattern = r'^<#(\d+)>\s+'
    channel_match = re.match(channel_mention_pattern, message)

    if channel_match:
        channel_id = int(channel_match.group(1))
        message_text = re.sub(channel_mention_pattern, '', message)

        target_channel = bot.get_channel(channel_id)

        if target_channel:
            permissions = target_channel.permissions_for(ctx.guild.me)
            if not permissions.send_messages:
                await ctx.send(get_translation(ctx.author.id, 'no_permission').format(channel=target_channel.mention))
                return

            await target_channel.send(message_text)

            confirmation = await ctx.send(
                get_translation(ctx.author.id, 'channel_sent').format(channel=target_channel.mention))
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
            await confirmation.delete()
        else:
            await ctx.send(get_translation(ctx.author.id, 'channel_not_found'))
            return
    else:
        await ctx.send(message)

    await ctx.message.delete()


@anns.error
async def anns_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        error_message = await ctx.send(get_translation(ctx.author.id, 'no_role'))
        await ctx.message.delete()
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        await error_message.delete()




bot.run('ENTER YOUR BOT TOKEN')


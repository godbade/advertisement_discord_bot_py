import discord
from discord.ext import commands
import re

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Список ID ролей, которым разрешено использовать команду anns
ALLOWED_ROLE_IDS = [
    1250114225616064512,  # ID роли из вашего примера
    # Добавьте сюда другие ID ролей при необходимости
]


# Проверка наличия роли у пользователя
def has_allowed_role():
    async def predicate(ctx):
        # Проверяем, есть ли у пользователя хотя бы одна из разрешенных ролей
        return any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)

    return commands.check(predicate)


@bot.command()
@has_allowed_role()
async def anns(ctx, *, message=""):
    # Проверяем, было ли введено сообщение
    if not message:
        await ctx.send(
            "Пожалуйста, введите сообщение после команды. Например: `!anns привет` или `!anns #канал привет`")
        return

    # Проверяем, есть ли упоминание канала в начале сообщения
    channel_mention_pattern = r'^<#(\d+)>\s+'
    channel_match = re.match(channel_mention_pattern, message)

    if channel_match:
        # Если указан канал, извлекаем ID канала и текст сообщения
        channel_id = int(channel_match.group(1))
        message_text = re.sub(channel_mention_pattern, '', message)

        # Получаем канал по ID
        target_channel = bot.get_channel(channel_id)

        if target_channel:
            # Проверяем права на отправку сообщений в указанный канал
            permissions = target_channel.permissions_for(ctx.guild.me)
            if not permissions.send_messages:
                await ctx.send(f"У меня нет прав на отправку сообщений в канал {target_channel.mention}.")
                return

            # Отправляем сообщение в указанный канал
            await target_channel.send(message_text)

            # Отправляем подтверждение
            confirmation = await ctx.send(f"Сообщение отправлено в канал {target_channel.mention}.")
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
            await confirmation.delete()  # Удаляем подтверждение через 5 секунд
        else:
            await ctx.send("Указанный канал не найден.")
            return
    else:
        # Если канал не указан, отправляем сообщение в текущий канал
        await ctx.send(message)

    # Удаляем сообщение с командой
    await ctx.message.delete()


# Обработка ошибки, если у пользователя нет нужной роли
@anns.error
async def anns_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Отправляем сообщение об ошибке и удаляем его через 5 секунд
        error_message = await ctx.send("У вас нет прав для использования этой команды.")
        await ctx.message.delete()  # Удаляем сообщение с командой
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        await error_message.delete()  # Удаляем сообщение об ошибке через 5 секунд



bot.run('ENTER YOUR BOT TOKEN')

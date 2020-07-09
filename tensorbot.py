"""
link to server https://discordapp.com/oauth2/authorize?&client_id=722440194506096641&sco
    pe=bot&permissions={2081422583}
"""

from discord.ext import commands
import asyncio
import psycopg2
from psycopg2 import OperationalError, errors, errorcodes

# испорт токена , инициализация команд
TOKEN = open('token.txt', 'r').read()
CHANNEL_ID = 722454412458590260
client = commands.Bot(command_prefix='/')


# приветствие пользователей после запуска бота
@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)

    await channel.send('Bot is ready.'
                       '\nType /bot_help to see bot fucntions')


@client.event
async def on_member_join():
    pass


# Руководство к командам бота
@client.command()
async def bot_help(message):
    guid = ('This bot is allow u to store files.'
            '\n\n/send "file" "discription" - to send file to bot. '
            '\n\n/get_doc_list - to see all your documents and discriptions u send before.'
            '\n\n/get_answer_list - to see your answers.'
            '\n\n/get_answer "answer id" - to set your answer by id for your file. '
            '\n\n/delete_doc "doc id" - to delete your document by id.'
            '\n\n/delete_answer "answer id" - to delete your answer bu id.'
            '\n\nget_user_doc "user id" - to see user documents list.')
    await message.channel.send(guid)


# Функция очистки чата
@client.command()
async def clear(ctx, amount):
    pass


# команда сохранения файла
@client.command()
async def send(ctx):
    # информация для записи в БД
    download_link = ctx.message.attachments[0].url
    # filename = ctx.message.attachments[0].filename
    users_file_name = ctx.message.content[6:]
    client_username = ctx.author.id

    # добавление информации пользователя в БД
    try:
        conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO file_store (user_id,document_url,filename) VALUES (%s,%s,%s)",
                       (client_username, download_link, users_file_name))
        conn.commit()

    except Exception as ex:
        print(ex)

    else:
        await ctx.message.channel.send('added successfully')


# команда получения списка документов из базы данных
@client.command()
async def get_doc_list(ctx):
    try:
        # вывод всех документов по id пользователя
        conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
        cursor = conn.cursor()

        client_username = str(ctx.author.id)

        cursor.execute("SELECT id,document_url, filename FROM file_store WHERE user_id = %s",
                       (client_username,))
        rows = cursor.fetchall()
        if not rows:
            ctx.message.channel.send('Empty list')
        else:
            for row in rows:
                await ctx.message.channel.send(f'id: {row[0]} text: {row[2]} \n{row[1]}')

    except psycopg2.DatabaseError as ex:
        await ctx.message.channel.send(ex)


# команда получения списка ответов
@client.command()
async def get_answer_list(ctx):
    # вывод всех ответов по id пользователя
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()

    client_username = str(ctx.author.id)

    cursor.execute("SELECT answer_id, answer FROM user_answers WHERE user_id = %s", (client_username,))
    rows = cursor.fetchall()

    for row in rows:
        if row[0] is None:
            await ctx.message.channel.send('Empty')
            break
        else:
            await ctx.message.channel.send(f'id: {row[0]} text: {row[1]}')


# команда создания ответа статуса сохранения файла по id
@client.command()
async def get_answer(ctx, num):
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()

    client_username = str(ctx.author.id)
    num = int(num)

    try:
        cursor.execute(f"SELECT id, filename FROM file_store WHERE (user_id = %s) AND (id = %s)",
                       (client_username, num))
        row = cursor.fetchall()

        answer = f'Answer for "{row[0][0]}" with text "{row[0][1]}"'
        await ctx.message.channel.send(answer)

        cursor.execute("INSERT INTO user_answers (user_id, answer) VALUES (%s, %s)",
                       (client_username, answer))
        conn.commit()

    except psycopg2.DatabaseError as error:
        await ctx.message.channel.send('This file already deleted ', error)
    except Exception as error:
        print('error')
        await ctx.message.channel.send('Error')


# команда удаления файла из базы данных
@client.command()
async def delete_doc(ctx, num):
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()

    client_username = str(ctx.author.id)
    num = int(num)

    cursor.execute(f"DELETE FROM file_store WHERE (id = %s) AND (user_id =%s)", (num, client_username))
    conn.commit()

    await ctx.message.channel.send('deleting answer done')


# команда удаления ответа
@client.command()
async def delete_answer(ctx, num):
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()

    client_username = str(ctx.author.id)
    num = int(num)

    cursor.execute(f"DELETE  FROM user_answers WHERE (answer_id = %s) AND (user_id = %s)", (num, client_username))
    conn.commit()

    await ctx.message.channel.send('deleting answer done')


# получение списка документов пользователей по id
@client.command()
async def get_user_doc(ctx, user_id):
    try:
        # вывод всех документов по id пользователя
        conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
        cursor = conn.cursor()

        cursor.execute("SELECT id,document_url, filename FROM file_store WHERE user_id = %s",
                       (user_id,))
        rows = cursor.fetchall()

        for row in rows:
            await ctx.message.channel.send(f'id: {row[0]} text: {row[2]} \n{row[1]}')

    except Exception as ex:
        print(ex)
    finally:
        pass


# запуск бота
client.run(TOKEN)

# password admin
# port 5432 default

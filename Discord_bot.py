"""
link to server https://discordapp.com/oauth2/authorize?&client_id=722440194506096641&sco
    pe=bot&permissions={2081422583}
"""

from discord.ext import commands
import asyncio
import psycopg2

TOKEN = open('token.txt', 'r').read()
client = commands.Bot(command_prefix='/')


@client.event
async def on_ready():
    print('Bot is ready.\nType /bot_help to see bot fucntions')


# Ответ бота на сообщения с гайдом
@client.command()
async def bot_help(message):
    guid = ('This bot is allow u to store files.\n/send "filename" "discription" - to send '
            'file for bot. \n/get_doc_list - to see all your documents and discriptions u send '
            'before.\n/get_answer_list - to see your answers.\n/get_answer "answer id" - to '
            'set your answer by id for your file. \n/delete_doc "doc id" - to delete your document by '
            'id.\n/delete_answer "answer id" - to delete your answer bu id.\n/clear "amount of messages" - to delete '
            'chat messages.')
    await message.channel.send(guid)


# Функция очистки чата
@client.command()
async def clear(ctx, amount):
    pass


# команда сохранения файла
@client.command()
async def send(ctx):
    download_link = ctx.message.attachments[0].url
    # filename = ctx.message.attachments[0].filename
    users_file_name = ctx.message.content[6:]
    client_username = ctx.author.id
    try:
        conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO file_store (user_id,document_url,filename) VALUES (%s,%s,%s)",
                       (client_username, download_link, users_file_name))
        conn.commit()
        await ctx.message.channel.send('added successfully')
    except Exception as ex:
        print(ex)

    finally:
        pass

    '''
    file_request = requests.get(download_link, allow_redirects=True)
    file_request.encoding = 'utf-8'
    with open('test.txt', 'w', encoding="utf-8") as f:
        f.write(str(file_request.text))
    '''


# команда получения списка документов из базы данных
@client.command()
async def get_doc_list(ctx):
    try:
        conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
        cursor = conn.cursor()
        client_username = str(ctx.author.id)
        # print(client_username)
        cursor.execute("SELECT id,document_url, filename FROM file_store WHERE user_id = %s",
                       (client_username,))
        rows = cursor.fetchall()
        for row in rows:
            await ctx.message.channel.send(f'id: {row[0]} text: {row[2]} \n{row[1]}')
    except Exception as ex:
        print(ex)
    finally:
        pass


# команда получения списка ответов
@client.command()
async def get_answer_list(ctx):
    client_username = str(ctx.author.id)
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()
    cursor.execute("SELECT answer_id, answer FROM user_answers WHERE user_id = %s", (client_username,))
    rows = cursor.fetchall()
    print(rows)
    for row in rows:
        if row[0] is None:
            await ctx.message.channel.send('Пусто')
            break
        else:
            await ctx.message.channel.send(f'id: {row[0]} text: {row[1]}')


# команда создания ответа статуса сохранения файла по id
@client.command()
async def get_answer(ctx, num):
    client_username = str(ctx.author.id)
    num = int(num)
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT id, filename FROM file_store WHERE (user_id = %s) AND (id = %s)", (client_username, num))
        row = cursor.fetchall()
        print(row)
        answer = f'Ответ на документ "{row[0][0]}" с текстом "{row[0][1]}"'
        await ctx.message.channel.send(answer)
        cursor.execute("INSERT INTO user_answers (user_id, answer) VALUES (%s, %s)",
                        (client_username, answer))
        conn.commit()
    except Exception as ex:
        await ctx.message.channel.send('This file already deleted')


# команда удаления файла из базы данных
@client.command()
async def delete_doc(ctx, num):
    client_username = str(ctx.author.id)
    print(client_username)
    num = int(num)
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM file_store WHERE id = {num}")
    conn.commit()
    # , user_id = {client_username}
    await ctx.message.channel.send('deleting answer done')
    print('done')


# команда удаления ответа
@client.command()
async def delete_answer(ctx, num):
    client_username = str(ctx.author.id)
    conn = psycopg2.connect(dbname='File_Browser', user='postgres', password='admin')
    cursor = conn.cursor()
    num = int(num)
    cursor.execute(f"DELETE  FROM user_answers WHERE (answer_id = %s) AND (user_id = %s)", (num, client_username))
    conn.commit()
    await ctx.message.channel.send('deleting answer done')
    print('done')

# запуск бота
client.run(TOKEN)

# password admin
# port 5432 default

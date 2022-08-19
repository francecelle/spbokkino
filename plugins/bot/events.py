from pyrogram import Client, filters


@Client.on_message(filters.private)
async def cache_handler(client, msg):
    await client.cache.call(msg.chat.id)
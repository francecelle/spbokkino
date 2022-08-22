from pyrogram import Client, filters

def is_verify(filter, client, m):
    return m.text and m.reply_markup and m.text.find("per essere ben accetto nel gruppo") > -1

@Client.on_message(filters.mentioned & filters.create(is_verify))
async def solve_verify(client, m):
    if m.reply_markup.inline_keyboard:
        for row in m.reply_markup.inline_keyboard:
            for button in row:
                if getattr(button, 'url', None):
                    url = button.url
                    if re.match("https://t.me/(?!\+).+", url):
                        url = "@"+url.replace("https://t.me/", "")
                    await client.join_chat(url)
                if getattr(button, 'callback_data', None):
                    await client.request_callback_answer(m.chat.id, m.id, button.callback_data, 3)

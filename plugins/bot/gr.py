import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters

admin_id = int(os.environ['id'])

@Client.on_message(filters.private & filters.user(admin_id) & filters.command("block"))
async def blockgr(client, m):
    inline = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", "home")]])
    try:
        id, text = m.command[1], ""
        bl = await client.db.get_blocked()
        if id not in bl:
            await client.db.block(id)
            text = "<b>✅ » Gruppo bloccato correttamente!</b>"
        else:
            text = "❌ <b>Non puoi bloccare il gruppo</b>\n<i>Il gruppo è già bloccato</i>"
        await m.reply_text(text, reply_markup=inline)
    except IndexError:
        await m.reply_text("❌ <b>Sintassi non valida</b>\n<i>Usa /block chatid</i>", reply_markup=inline)

@Client.on_message(filters.private & filters.user(admin_id) & filters.command("unblock"))
async def unblockgr(client, m):
    inline = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", "home")]])
    try:
        id, text = m.command[1], ""
        bl = await client.db.get_blocked()
        if id in bl:
            await client.db.unblock(id)
            text = "<b>✅ » Gruppo sbloccato correttamente!</b>"
        else:
            text = "❌ <b>Non puoi sbloccare il gruppo</b>\n<i>Il gruppo non è bloccato</i>"
        await m.reply_text(text, reply_markup=inline)
    except IndexError:
        await m.reply_text("❌ <b>Sintassi non valida</b>\n<i>Usa /unblock chatid</i>", reply_markup=inline)

@Client.on_callback_query(filters.regex("groups(\d)"))
async def showbl(client, q):
    skip, inline = int(q.matches[0].group(1)), []
    bl, n = await client.db.get_blocked(), skip*4096
    text = f"<b>💬 {len(bl)} gruppi bloccati!</b>\n"
    for gr in bl:
        text += f"\n<code>{gr}</code>"
    text = text[n::]
    if len(text) > 4096:
        inline.append([InlineKeyboardButton("▶", f"groups{skip+1}")])
        text = text[0:4096]
    inline.append([InlineKeyboardButton("🔙 Indietro", "home")])
    await q.message.edit(text, reply_markup=InlineKeyboardMarkup(inline))

import os
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import BadRequest
from pyrogram import Client, filters

admin_id = int(os.environ['id'])
print(admin_id)

@Client.on_message(filters.user(admin_id) & filters.private & filters.command("start", "/"))
async def start(client, msg):
    await msg.reply_text("""<b>🛠 MENÙ SPAMBOT</b>
<i>Usa i bottoni per spostarti all'interno del menù.</i>

<b>- Voip</b>
<i>potrai aggiungere/modificare il voip che spamma i messaggi all'interno dei gruppi</i>
<b>- Messaggi</b>
<i>potrai modificare il testo, lo status e il tempo di ripetizione dei <b>tre</b> messaggi</i>""", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("📞 Voip", "voip"), InlineKeyboardButton("✏ Messaggi", "message")],
    [InlineKeyboardButton("Bl", "groups0"), InlineKeyboardButton("📃 Logs", "showlogs")]
    ]))

@Client.on_message(filters.private & filters.user(admin_id) & filters.command("join"))
async def joincmd(client, m):
    print(m.commands)
    success, errors = 0, ""
    for gr in m.commands[1::]:
        try:
            chat = await client.ubot.join_chat(gr)
            success += 1
        except BadRequest as e:
            if e.id == "USER_ALREDY_PARTECIPANT":
                pass
            elif e.id == "CHANNEL_PRIVATE":
                errors += f"\n</code>[{gr}]</code> <i>Sono bannato dal gruppo</i>"
    await client.loop.stop()
    await m.reply_text(f"<b>✅ » Sono entrato in {success} gruppi!</b>")
    await client.loop.start()

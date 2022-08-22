import os, re
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import BadRequest
from pyrogram import Client, filters

admin_id = int(os.environ['id'])

@Client.on_message(filters.private & filters.user(admin_id) & filters.command("start"))
async def startmkd(client, msg):
    m = await msg.reply_text("""<b>🛠 MENÙ SPAMBOT</b>
<i>Usa i bottoni per spostarti all'interno del menù.</i>

<b>- Voip</b>
<i>potrai aggiungere/modificare il voip che spamma i messaggi all'interno dei gruppi</i>
<b>- Messaggi</b>
<i>potrai modificare il testo, lo status e il tempo di ripetizione dei <b>tre</b> messaggi</i>""", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("📞 Voip", "voip"), InlineKeyboardButton("✏ Messaggi", "message")],
    [InlineKeyboardButton("Bl 🚷", "groups0"), InlineKeyboardButton("📃 Logs", "showlogs")]
    ]))

@Client.on_message(filters.private & filters.user(admin_id) & filters.command("join"))
async def joincmd(client, m):
    success, errors = 0, ""
    msg = await m.reply_text("🔄 <code>Sto entrando nei gruppi...</code>")
    for gr in m.command[1::]:
        try:
            if re.match("https://t.me/(?!\+).+", gr):
                gr = "@"+gr.replace("https://t.me/", "")
            chat = await client.ubot.join_chat(gr)
            success += 1
        except BadRequest as e:
            if e.ID == "USER_ALREADY_PARTICIPANT":
                success += 1
            elif e.ID == "CHANNEL_PRIVATE":
                errors += f"\n<code>[{gr}]</code> <i>Sono bannato dal gruppo</i>"
            elif e.ID == "USERNAME_INVALID":
                errors += f"\n<code>[{gr}]</code> <i>Username non valido</i>"
            else:
                errors += f"\n<code>[{gr}]</code> <i>{e.MESSAGE}</i>"
    client.db.dialogs = client.ubot.get_dialogs()
    await msg.edit(f"<b>✅ » Sono entrato in {success} gruppi!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Indietro", "home")]]))

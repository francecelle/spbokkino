from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def get_prewiew(client, n):
    m = await client.db.get_message(n)
    if m == None:
        return "Non impostato"
    elif m.text:
        return m.text[0:10]+"..."
    else:
        return "πΌ"
def convert(s: int):
    string = ""
    if s >= 86400:
         d = s // 86400
         s = s - 86400*d
         string += f"{d}d "
    if s >= 3600:
        d = s // 3600
        s = s - 3600*d
        string += f"{d}h "
    if s >= 60:
        d = s // 60
        s = s - 60*d
        string += f"{d}m "
    if s >= 0:
        string += f"{s}s"
    return string

async def home():
    return """<b>π  MENΓ SPAMBOT</b>
<i>Usa i bottoni per spostarti all'interno del menΓΉ.</i>

<b>- Voip</b>
<i>potrai aggiungere/modificare il voip che spamma i messaggi all'interno dei gruppi</i>
<b>- Messaggi</b>
<i>potrai modificare il testo, lo status e il tempo di ripetizione dei <b>tre</b> messaggi</i>""", InlineKeyboardMarkup([
    [InlineKeyboardButton("π Voip", "voip"), InlineKeyboardButton("β Messaggi", "message")],
    [InlineKeyboardButton("Bl π·", "groups0"), InlineKeyboardButton("π Logs", "showlogs")]
    ])

@Client.on_callback_query(filters.regex("stop!(.+)"))
async def stopr(client, q):
    pr = q.matches[0].group(1)
    await client.cache.close(pr)
    text, inline = await home()
    await q.message.edit(text, reply_markup=inline)

@Client.on_callback_query(filters.regex("home"))
async def backhome(client, q):
    text, inline = await home()
    await q.message.edit(text, reply_markup=inline)

@Client.on_callback_query(filters.regex("m(\d)_text"))
async def set_mtext(client, q):
    n = q.matches[0].group(1)
    await q.message.edit("Inviami <b>il messaggio</b> da spammare. Puoi usare anche le <b>foto</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("π Indietro", "message")]]))
    await client.cache.process("wait_message", q.message.chat.id, n)

@Client.on_callback_query(filters.regex("m(\d)_time"))
async def set_mtime(client, q):
    n = q.matches[0].group(1)
    await q.message.edit(f"Inviami il tempo di ripetizione del <b>{n}</b> messaggio. Esprimi il tempo secondo il <b>seguente formato</b>:\n1d 1h 1m 1s", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("π Indietro", "message")]]))
    await client.cache.process("wait_time", q.message.chat.id, n)

@Client.on_callback_query(filters.regex("status(\d)"))
async def set_status(client, q):
    n = q.matches[0].group(1)
    old, time = await client.db.get_status(n), await client.db.get_time(n)
    if time > 0:
        client.db.messages[n]["active"] = False if old else True
        s1, s2, s3 = await client.db.get_mstatus()
        await q.message.edit_reply_markup(InlineKeyboardMarkup([
    [InlineKeyboardButton("1β£ Messaggio", "m1_text"), InlineKeyboardButton('π', "m1_time"), InlineKeyboardButton(s1, "status1")],
    [InlineKeyboardButton("2β£ Messaggio", "m2_text"), InlineKeyboardButton('π', "m2_time"), InlineKeyboardButton(s2, "status2")],
    [InlineKeyboardButton("3β£ Messaggio", "m3_text"), InlineKeyboardButton('π', "m3_time"), InlineKeyboardButton(s3, "status3")],
    [InlineKeyboardButton("π Indietro", "home")]
    ]))
        i, text = client.db.messages[n]["active"], ""
        if i:
            await client.loop.start(n, time)
            text = "βοΈ Β» Attivato"
        else:
            await client.loop.stop(n)
            text = "βοΈ Β» Disattivato"
        await q.answer(text, False)
    else:
        await q.answer("β  Imposta prima il tempo per attivare il messaggio!", True)

@Client.on_callback_query(filters.regex("voip"))
async def voipmenu(client, q):
    text = "π "
    if client.ubot:
        text += "<b>Voip attuale</b>\n"
        me = await client.ubot.get_me()
        text += me.mention(style="html")+f"\n<code>+{me.phone_number}</code>\n\nπ‘ "
    text += """Inviami <b>il numero</b> del nuovo voip da utilizzare per <b>spammare</b>"""
    await q.message.edit(
    text,
    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("β Annulla", "stop!wait_voip")]])
        )
    await client.cache.process("wait_voip", q.message.chat.id, q.message)

@Client.on_callback_query(filters.regex("showlogs"))
async def showlogs(client, q):
    text = "β οΈ <b>Logs</b>\n\n<code>"
    with open("logs.txt", "r") as f:
        text += f.read()
        text += "</code>"
        f.close()
    await q.message.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("π Indietro", "home")]]))

@Client.on_callback_query(filters.regex("message"))
async def memenu(client, q):
    await client.cache.close("wait_message")
    s1, s2, s3 = await client.db.get_mstatus()
    l, text = ["1οΈβ£", "2οΈβ£", "3οΈβ£"], """π <b>Messaggi</b>\n<i>Puoi impostare fino a tre messaggi da spammare in tutti i gruppi in cui il bot Γ¨ presente. Ogni <b>messaggio</b> avrΓ  un tempo di ripetizione personalizzabile.</i>"""
    for n in (1, 2, 3):
        text += f"""\n\nπ―{l[n-1]}
 β <b>{"Attivo" if (await client.db.get_status(n)) else "Spento"}</b>
 β <i>Ripeti ogni {convert((await client.db.get_time(n)))}</i>
 β <i>{(await get_prewiew(client, n))}</i>"""
    await q.message.edit(text, reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("1β£ Messaggio", "m1_text"), InlineKeyboardButton('π', "m1_time"), InlineKeyboardButton(s1, "status1")],
    [InlineKeyboardButton("2β£ Messaggio", "m2_text"), InlineKeyboardButton('π', "m2_time"), InlineKeyboardButton(s2, "status2")],
    [InlineKeyboardButton("3β£ Messaggio", "m3_text"), InlineKeyboardButton('π', "m3_time"), InlineKeyboardButton(s3, "status3")],
    [InlineKeyboardButton("π Indietro", "home")]
    ]))

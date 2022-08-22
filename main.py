import os, re, asyncio
from loop import Loop
from cache import Cache
from database import Database
from plugins.mylogger import logger
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import *
from pyrogram import Client, idle

bot = Client("spambot", int(os.environ["api_id"]), os.environ["api_hash"], bot_token=os.environ['token'], plugins={'root':'plugins/bot'})

bot.cache, bot.db, bot.loop = Cache(bot), Database(), Loop()
bot.start()

if os.environ.get("session_string", None):
    bot.ubot = Client("ubot", int(os.environ['api_id']), os.environ['api_hash'], session_string=os.environ['session_string'], plugins={"root":"plugins/ubot"})
    bot.ubot.start()
else:
    bot.ubot = None

@bot.loop.spamming()
async def spam(n):
    msg = await bot.db.get_message(n)
    time = await bot.db.get_time(n)
    async for group in bot.db.get_groups(bot):
        try:
            if msg.photo:
                await bot.ubot.send_photo(group, msg.photo.file_id, msg.caption, caption_entities=msg.caption_entities, disable_web_page_preview=True)
            else:
                await bot.ubot.send_message(group, msg.text, entities=msg.entities, disable_web_page_preview=True)
                print("sended")
        except (FloodWait, Forbidden) as e:
            print(e.ID, e.MESSAGE)
            if re.match("SLOWMODE_WAIT", e.ID):
                await logger.log(group, f"Modalità lenta attiva ({e.x})")
            elif re.match("FLOOD_WAIT", e.ID):
                await logger.log(f"Floodwait per {e.x}s")
                await asyncio.sleep(e.x)
            elif e.ID in ("CHAT_ADMIN_REQUIRED", "CHAT_FORBIDDEN", "CHAT_WRITE_FORBIDDEN", "USER_RESTRICTED"):
                await logger.log("Sono uscito, perché non ho il permesso di scrivere")
                await bot.ubot.leave_chat(group)
                bot.cache.dialogs = bot.ubout.get_dialogs()
        except Exception as err:
            print(err)

@bot.cache.on("wait_voip")
async def wait_voip(m, my_msg):
    if bot.ubot:
        try:
            await bot.ubot.stop()
        except ConnectionError:
            bot.ubot = None
            return await bot.cache.close("wait_voip")
    bot.ubot = Client("ubot", int(os.environ["api_id"]), os.environ["api_hash"], plugins={"root":"plugins/ubot"})
    await bot.cache.close("wait_voip")
    inline = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla ❌ ", "stop!wait_code")]])
    await bot.ubot.connect()
    try:
        await my_msg.edit("🔄 <code>Richiedendo il codice...</code>", reply_markup=inline)
        obj = await bot.ubot.send_code(m.text)
        await bot.cache.process("wait_code", m.chat.id, m.text, obj)
        await bot.cache.close("wait_voip")
        await m.reply_text(f"📨 Inviami il <b>codice</b> d'accesso per accedere.", reply_markup=inline)
    except FloodWait as fw:
        await m.reply_text("⚠️ <b>Codice non inviato</b>\n<i>Hai effettuato troppi tentantivi di accesso e sono in andato in FloodWait</i>")
    except NotAcceptable as e:
        await bot.cache.process("wait_voip", m.chat.id)
        await m.reply_text("❌ <b>Il numero non è valido</b>\n<i>Controlla che sia corretto o prova con un altro numero</i>", reply_markup=inline)

@bot.cache.on("wait_code")
async def wait_code(m, number, sentcode):
    try:
        user = await bot.ubot.sign_in(number, sentcode.phone_code_hash, m.text)
        #print(user)#termini
        if not user:
            user = await bot.ubot.sign_up(number, sentcode.phone_code_hash, "PinkoPallo")
        await m.reply_text("✅ <b>» Login completato con successo!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", "home")]]))
        print((await bot.ubot.export_session_string()))
        await bot.cache.close("wait_code")
    except SessionPasswordNeeded:
        await m.reply_text(f"⚠ » L'account é protetto da <b>password</b>. Inviamela per <b>completare</b> l'accesso. Suggerimento: <i>{(await bot.ubot.get_password_hint())}</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", "stop!wait_pass")]]))
        await bot.cache.close("wait_code")
        await bot.cache.process("wait_pass", m.chat.id)
    except BadRequest as bad:
        if bad.ID in ("PHONE_CODE_INVALID", "PHONE_CODE_EXPIRED"):
            await m.reply_text("❌ <b>Login non riuscito!</b>\n➖ <i>Il codice non è valido o è scaduto."+f"Potrai riprovare fra {sentcode.timeout} secondi</i>" if sentcode.timeout else "</i>")

@bot.cache.on("wait_pass")
async def wait_pass(m):
    try:
        user = await bot.ubot.check_password(m.text)
        await m.reply_text("✅ <b>» Login completato con successo!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", "home")]]))
        print((await bot.ubot.export_session_string()))
        await bot.cache.close("wait_pass")
    except BadRequest as bad:
        await m.reply_text("❌ <b>Login incompleto</b>\n<i>La password non è valida. Riprova</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", "stop!wait_pass")]]))

@bot.cache.on("wait_message")
async def wait_message(m, n):
    await bot.db.set_message(m, n)
    await m.reply_text("✅ <b>» Messaggio impostato con successo!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Indietro", "message")]]))

@bot.cache.on("wait_time")
async def wait_message(m, n):
    time = 0
    d, h, min, s = re.search("(\d+)d", m.text), re.search("(\d+)h", m.text), re.search("(\d+)m", m.text), re.search("(\d+)s", m.text)
    if d:
        time += int(d.group(1))*86400
    if h:
        time += int(h.group(1))*3600
    if min:
        time += int(min.group(1))*60
    if s:
        time += int(s.group(1))
    await bot.db.set_time(time, n)
    await m.reply_text("✅ <b>»Tempo impostato con successo!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Indietro", "message")]]))

print("Bot started")
idle()

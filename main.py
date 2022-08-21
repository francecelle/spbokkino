import os, re, asyncio
from loop import Loop
from cache import Cache
from database import Database
from plugins.mylogger import logger
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import *
from pyrogram import Client, idle

bot = Client("spambot", os.environ["api_id"], os.environ["api_hash"], bot_token=os.environ['token'], plugins={'root':'plugins/bot'})

bot.cache, bot.ubot, bot.db, bot.loop = Cache(bot), None, Database(), Loop()
bot.start()

async def spam(n):
    msg = await bot.db.get_message(n)
    time = await bot.db.get_time(n)
    async for group in bot.db.get_groups(bot):
        try:
            if msg.photo:
                await bot.ubot.send_photo(group, msg.photo.file_id, msg.caption, caption_entities=msg.caption_entities, disable_web_page_prewiew=True)
            else:
                await bot.ubot.send_message(group, msg.text, entities=msg.entities, disable_web_page_prewiew=True)
        except (FloodWait, Forbidden) as e:
            print(e.id, e.MESSAGE)
            if re.match("SLOWMODE_WAIT", e.id):
                await logger.log(group, f"Modalità lenta attiva ({e.x})")
            elif re.match("FLOOD_WAIT", e.id):
                await logger.log(f"Floodwait per {e.x}s")
                await asyncio.sleep(e.x)
            elif e.id in ("CHAT_ADMIN_REQUIRED", "CHAT_FORBIDDEN", "CHAT_WRITE_FORBIDDEN", "USER_RESTRICTED"):
                await logger.log("Sono uscito, perché non ho il permesso di scrivere")
                await bot.ubot.leave_chat(chat_id)
    return time
@bot.loop.spamming()
async def prova(n):
    print(n)

@bot.cache.on("wait_voip")
async def wait_voip(m):
    if bot.ubot:
        try:
            await bot.ubot.stop()
        except ConnectionError:
            bot.ubot = None
            return await bot.cache.close("wait_voip")
    bot.ubot = Client("ubot", os.environ["api_id"], os.environ["api_hash"])
    inline = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla ❌ ", "stop!wait_code")]])
    await bot.ubot.connect()
    try:
        obj = await bot.ubot.send_code(m.text)
        await bot.cache.close("wait_voip")
        await bot.cache.process("wait_code", m.text, obj)
        await m.reply_text(f"📨 Inviami il <b>codice</b> d'accesso per accedere.", reply_markup=inline)
    except FloodWait as fw:
        await m.reply_text("⚠️ <b>Codice non inviato</b>\n<i>Hai effettuato troppi tentantivi di accesso e sono in andato in FloodWait</i>")
        await bot.cache.close("wait_voip")
    except BadRequest as bad:
        await m.reply_text("❌ <b>Il numero non è valido</b>\n<i>Controlla che sia corretto o prova con un altro numero</i>", reply_markup=inline)

@bot.cache.on("wait_code")
async def wait_code(m, number, sentcode):
    try:
        user = await bot.ubot.sign_in(number, sentcode.phone_code_hash, m.text)
        await bot.cache.close("wait_code")
        #termini
        if not user:
            user = await bot.ubot.sign_up(number, sentcode.phone_code_hash, "PinkoPallo")
        await bot.ubot.start()
        await m.reply_text("✅ <b>» Login completato con successo!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", "home")]]))
    except SessionPasswordNeeded:
        await m.reply_text(f"⚠ » L'account é protetto da <b>password</b>. Inviamela per <b>completare</b> l'accesso. Suggerimento: <i>{(await bot.ubot.get_password_hint())}</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", "stop!wait_pass")]]))
        await bot.cache.close("wait_code")
        await bot.cache.process("wait_pass", m.chat.id)
    except BadRequest as bad:
        pass

@bot.cache.on("wait_pass")
async def wait_pass(m):
    try:
        user = await bot.ubot.check_password(m.text)
        await bot.ubot.start()
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

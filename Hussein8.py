import threading
from flask import Flask
import os

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
BOT_TOKEN = "8660583947:AAHfX8R5p1eqtOIoBBvRBkLhQQZ0Tm4x1po"
ADMIN_ID = 7262235922

# ============================================
# لا تـعـدّل تـحـت هـذا الـسـطـر
# ============================================

import telebot
from telebot import types
import json
import os
import time
from datetime import datetime

DATA_FILE = "servers.json"
USERS_FILE = "users.json"
BANNED_FILE = "banned.json"

REQUIRED_CHANNELS = [
    {"id": "@Husseinv5", "name": "قـَنـاة الـمـُطـَوّر حـُسـَيـن", "url": "https://t.me/Husseinv5"},
    {"id": "@lJ77D",     "name": "الـقـَنـاة الـثـانـِيـة",        "url": "https://t.me/lJ77D"},
    {"id": "@lJ77B",     "name": "الـقـَنـاة الـثـالـِثـة",        "url": "https://t.me/lJ77B"},
]

bot = telebot.TeleBot(BOT_TOKEN)
USER_STATE = {}
BROADCAST_STATE = {}


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []
    return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)


def load_banned():
    if os.path.exists(BANNED_FILE):
        try:
            with open(BANNED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []
    return []


def save_banned(banned_list):
    with open(BANNED_FILE, "w", encoding="utf-8") as f:
        json.dump(banned_list, f, ensure_ascii=False)


def is_banned(uid):
    return uid in load_banned()


# ترجع True فقط إذا كان المستخدم جديداً لأول مرة
def add_user(uid):
    users = load_users()
    if not isinstance(users, list):
        users = []
    if uid not in users:
        users.append(uid)
        save_users(users)
        return True
    return False


def is_admin(uid):
    return uid == ADMIN_ID


# فحص اشتراك المستخدم في القنوات
def check_subscription(uid):
    not_joined = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], uid)
            status = member.status
            if hasattr(status, "value"):
                status = status.value
            status = str(status).lower().replace("chatmemberstatus.", "")
            if status not in ["creator", "administrator", "member"]:
                not_joined.append(ch)
        except Exception as e:
            print(f"[SUB-CHECK ERROR] تأكد أن البوت مشرف في {ch['id']}: {e}")
            not_joined.append(ch)
    return not_joined


# إرسال إشعار للمطور بصورة المستخدم ومعلوماته وتاريخ دخوله
def notify_admin_new_user(user):
    try:
        now_str = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
        first_name = user.first_name or "بـدون اسـم"
        username = f"@{user.username}" if user.username else "لا يـُوجـد"
        uid = user.id

        caption = (
            "👤 <b>دُخـُول مـُسـتـَخـدِم جـَديـد لـِلـبـُـوت!</b>\n"
            "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n\n"
            f"📌 <b>الاسـِـم:</b> {first_name}\n"
            f"📱 <b>الـمـَعـرّف:</b> {username}\n"
            f"🆔 <b>الآيـِـدي:</b> <code>{uid}</code>\n"
            f"⏰ <b>وقـت الـدّخـُول:</b> <code>{now_str}</code>"
        )

        photos = bot.get_user_profile_photos(uid, limit=1)
        if photos and photos.total_count > 0:
            photo_file_id = photos.photos[0][-1].file_id
            bot.send_photo(ADMIN_ID, photo_file_id, caption=caption, parse_mode="HTML")
        else:
            bot.send_message(ADMIN_ID, caption, parse_mode="HTML")
    except Exception as e:
        print(f"[NOTIFY-ERROR]: {e}")


def send_subscribe_message(chat_id, message_id=None, edit=False):
    text = (
        "🔒 <b>الاشـتـِـراك الإجـبـَـاري</b>\n"
        "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n\n"
        "عـَـزيـزي الـمـُـسـتـَـخـدم 🤍\n"
        "عليك الاشتراك بجميع القنوات أدناه لتتمكن من استخدام البوت:\n\n"
        "1️⃣ قـَنـاة الـمـُطـَوّر حـُسـَيـن\n"
        "2️⃣ الـقـَنـاة الـثـانـِيـة\n"
        "3️⃣ الـقـَنـاة الـثـالـِثـة\n\n"
        "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
        "👇 اشـتـَرِك بـِالـقـَنـَوات ثـُمّ اضـغـَط (تـَـمّ الاشـتـِـراك) بـِالأسـفـَل:"
    )
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📢・اشـتـِـراك فـي قـَنـاة حـُسـَيـن", url="https://t.me/Husseinv5", style="primary"))
    kb.add(types.InlineKeyboardButton("📢・اشـتـِـراك فـي الـقـَنـاة الـثـانـِيـة", url="https://t.me/lJ77D", style="primary"))
    kb.add(types.InlineKeyboardButton("📢・اشـتـِـراك فـي الـقـَنـاة الـثـالـِثـة", url="https://t.me/lJ77B", style="primary"))
    kb.add(types.InlineKeyboardButton("✅・تـَـمّ الاشـتـِـراك", callback_data="check_sub", style="success"))

    if edit and message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=kb)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)


# ============================================
# الـقـَوائـِم
# ============================================

def user_menu(uid=None):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🌐・قـَائـِمـَة الـسـّيـرفـَـرات", callback_data="user|servers", style="success"))
    if uid and is_admin(uid):
        kb.add(types.InlineKeyboardButton("⚙️・لـَـوْحـَة الأدْمـِـن", callback_data="open_admin", style="primary"))
    return kb


def send_main_menu(chat_id, message_id=None, edit=False, uid=None):
    text = (
        "✨ <b>أهـْـلاً وسـَهـْـلاً بـِـك عـَـزيـزي</b>\n"
        "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
        "🤖 <b>بـُـوت سـِـيـرفـَـرات V2Ray الـسـّـريـعـَة</b>\n\n"
        "اخـتـَـر الـقـِسـم الـمـَطـلـُـوب مـِن الأسـفـَل 👇"
    )
    if edit and message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=user_menu(uid))
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=user_menu(uid))


def servers_menu():
    servers = load_data()
    kb = types.InlineKeyboardMarkup(row_width=1)
    if not servers:
        kb.add(types.InlineKeyboardButton("⚪・لا تـُـوجـَد سـِـيـرفـَـرات حـالـِيـاً", callback_data="noop"))
    else:
        for i, s in enumerate(servers):
            name = s.get("name") or f"سـِـيـرفـَر {i+1}"
            kb.add(types.InlineKeyboardButton(f"🟢・{name}", callback_data=f"view_server|{i}", style="success"))

    kb.add(types.InlineKeyboardButton("🔙・رجـُـوع لـِلـقـَائـِمـَة", callback_data="back_user", style="danger"))
    return kb


def admin_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("➕ إضـَـافـَة سـِـيـرفـَر", callback_data="admin|add", style="success"))
    kb.add(
        types.InlineKeyboardButton("📋 عـَـرض الـسـّيـرفـَـرات", callback_data="admin|list", style="primary"),
        types.InlineKeyboardButton("📊 الإحـصـَائـِيـّات", callback_data="admin|stats", style="primary"),
    )
    kb.add(
        types.InlineKeyboardButton("🗑️ حـَـذف سـِـيـرفـَر", callback_data="admin|del", style="danger"),
        types.InlineKeyboardButton("⚠️ حـَـذف الـكـُـلّ", callback_data="admin|clear", style="danger"),
    )
    kb.add(
        types.InlineKeyboardButton("🚫 حـَـظـر مـُسـتـَخـدم", callback_data="admin|ban", style="danger"),
        types.InlineKeyboardButton("✅ فـَك حـَـظـر", callback_data="admin|unban", style="success"),
    )
    kb.add(types.InlineKeyboardButton("📢 إذاعـَـة رِسـالـَة", callback_data="admin|broadcast", style="primary"))
    kb.add(types.InlineKeyboardButton("🔙 رجـُـوع لـِلـقـَائـِمـَة", callback_data="back_user", style="danger"))
    return kb


# ============================================
# الأوامـِـر
# ============================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid = message.from_user.id

    if is_banned(uid):
        bot.reply_to(message, "❌ <b>عـُذراً، تـَـمّ حـَـظـرُك مـِن اسـتـِخـدام الـبـُـوت.</b>", parse_mode="HTML")
        return

    # يتم تسجيل المستخدم وإرسال الإشعار لمرة واحدة فقط إذا كان جديداً
    is_new = add_user(uid)
    if is_new and uid != ADMIN_ID:
        notify_admin_new_user(message.from_user)

    # التحقق من الاشتراك إذا لم يكن المطور
    if not is_admin(uid):
        not_joined = check_subscription(uid)
        if not_joined:
            send_subscribe_message(message.chat.id)
            return

    send_main_menu(message.chat.id, uid=uid)


@bot.message_handler(commands=['myid'])
def cmd_myid(message):
    bot.reply_to(message, f"🆔 <b>مـَعـرّفـُـك:</b> <code>{message.from_user.id}</code>", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.from_user.id in USER_STATE, content_types=['text'])
def handle_admin_inputs(message):
    uid = message.from_user.id
    state = USER_STATE.get(uid)
    if not state:
        return

    step = state.get("step")
    text = message.text.strip()

    if step == "waiting_server_name":
        if not text:
            bot.reply_to(message, "❌ <b>يـُـرجـَى إرسـَال اسـم صـالـِح لـِلـسـّيـرفـَر:</b>", parse_mode="HTML")
            return
        USER_STATE[uid] = {
            "step": "waiting_server_code",
            "name": text
        }
        bot.reply_to(message, "📥 <b>أرسـِـل كـُـود الـسـّيـرفـَـر الآن:</b>", parse_mode="HTML")
        return

    if step == "waiting_server_code":
        name = state.get("name")
        data = load_data()
        data.append({"name": name, "link": text})
        save_data(data)
        USER_STATE.pop(uid, None)

        bot.reply_to(
            message,
            f"✅ <b>تـَـمّ حـِفـظ الـسـّيـرفـَـر بـِنـَجـاح</b>\n"
            f"ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
            f"📌 <b>الاسـِـم:</b> {name}\n"
            f"📊 <b>الـمـَجـمـُوع:</b> {len(data)} سـِـيـرفـَر",
            parse_mode="HTML",
            reply_markup=admin_menu()
        )
        return

    if step == "waiting_ban_id":
        USER_STATE.pop(uid, None)
        try:
            target_id = int(text)
            if target_id == ADMIN_ID:
                bot.reply_to(message, "❌ لا يـُمـكـِنـك حـَـظـر نـَفـسـِك!", reply_markup=admin_menu())
                return
            banned = load_banned()
            if target_id not in banned:
                banned.append(target_id)
                save_banned(banned)
                bot.reply_to(message, f"🚫 <b>تـَـمّ حـَـظـر الـمـُسـتـَخـدم:</b> <code>{target_id}</code> بـِنـَجـاح.", parse_mode="HTML", reply_markup=admin_menu())
            else:
                bot.reply_to(message, "⚠️ هـَذا الـمـُسـتـَخـدم مـَحـظـُور بـِالـفـِعـل!", reply_markup=admin_menu())
        except ValueError:
            bot.reply_to(message, "❌ يـُـرجـَى إرسـَال آيـِدي صـَحـِيـح (أرقـَام فـَقـَط).", reply_markup=admin_menu())
        return

    if step == "waiting_unban_id":
        USER_STATE.pop(uid, None)
        try:
            target_id = int(text)
            banned = load_banned()
            if target_id in banned:
                banned.remove(target_id)
                save_banned(banned)
                bot.reply_to(message, f"✅ <b>تـَـمّ فـَـك حـَـظـر الـمـُسـتـَخـدم:</b> <code>{target_id}</code> بـِنـَجـاح.", parse_mode="HTML", reply_markup=admin_menu())
            else:
                bot.reply_to(message, "⚠️ هـَذا الـمـُسـتـَخـدم غـَيـر مـَحـظـُور!", reply_markup=admin_menu())
        except ValueError:
            bot.reply_to(message, "❌ يـُـرجـَى إرسـَال آيـِدي صـَحـِيـح (أرقـَام فـَقـَط).", reply_markup=admin_menu())
        return


@bot.message_handler(func=lambda m: m.from_user.id in BROADCAST_STATE, content_types=['text'])
def handle_broadcast(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    text = message.text
    BROADCAST_STATE.pop(uid, None)
    users = load_users()
    bot.reply_to(message, f"📢 <b>جـَـاري الإرسـَال لـِـ {len(users)} مـُسـتـَخـدم...</b>", parse_mode="HTML")
    success = 0
    fail = 0
    for user_id in users:
        if is_banned(user_id):
            continue
        try:
            bot.send_message(user_id, text)
            success += 1
            time.sleep(0.05)
        except Exception:
            fail += 1
    bot.send_message(
        message.chat.id,
        f"✅ <b>اكـتـَمـَلـَت الإذاعـَـة بـِنـَجـاح</b>\n"
        f"ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
        f"🟢 <b>نـَجـَح:</b> {success}\n"
        f"🔴 <b>فـَشـِل:</b> {fail}",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


# ============================================
# مـُعـالـَجـة الأزرار
# ============================================

@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    data = call.data
    uid = call.from_user.id

    if is_banned(uid):
        bot.answer_callback_query(call.id, "❌ أنت محظور من استخدام البوت!", show_alert=True)
        return

    # فحص الاشتراك الإجباري عند الضغط على "تم الاشتراك"
    if data == "check_sub":
        not_joined = check_subscription(uid)
        if not_joined:
            bot.answer_callback_query(
                call.id,
                "❌ عليك الاشتراك بجميع القنوات أولاً لتتمكن من استخدام البوت!",
                show_alert=True
            )
            return

        bot.answer_callback_query(call.id, "✅ تم التحقق بنجاح! أهلاً بك.", show_alert=False)
        send_main_menu(call.message.chat.id, call.message.message_id, edit=True, uid=uid)
        return

    # التحقق من الاشتراك لأي زر آخر إذا لم يكن أدمن
    if not is_admin(uid):
        not_joined = check_subscription(uid)
        if not_joined:
            bot.answer_callback_query(call.id, "❌ عليك الاشتراك بالقنوات أولاً!", show_alert=True)
            send_subscribe_message(call.message.chat.id, call.message.message_id, edit=True)
            return

    if data == "open_admin":
        if not is_admin(uid):
            bot.answer_callback_query(call.id, "❌ خـَاص بـِالـمـُشـرِف فـَقـَط")
            return
        try:
            bot.edit_message_text(
                "🎛️ <b>لـَـوْحـَة تـَحـَكـّم الأدْمـِـن</b>\n"
                "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
                "اخـتـَـر الـعـَمـَلـِيـّة الـمـَطـلـُـوبـَة مـِن الأسـفـَل 👇",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=admin_menu()
            )
        except Exception:
            pass
        return

    if data == "back_user":
        send_main_menu(call.message.chat.id, call.message.message_id, edit=True, uid=uid)
        return

    if data == "user|servers":
        try:
            bot.edit_message_text(
                "🌐 <b>قـَائـِمـَة الـسـّيـرفـَـرات الـمـُـتـَاحـَة</b>\n"
                "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
                "اخـتـَـر الـسـّيـرفـَـر لـِلـحـُصـُول عـَلـى الـكـُـود مـُبـَاشـَرة 👇",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=servers_menu()
            )
        except Exception:
            pass
        return

    if data.startswith("view_server|"):
        idx = int(data.split("|")[1])
        servers = load_data()
        if idx >= len(servers) or idx < 0:
            bot.answer_callback_query(call.id, "❌ الـسـّيـرفـَر غـَيـر مـُتـَوفـّر!", show_alert=True)
            return

        server = servers[idx]
        name = server.get("name") or f"سـِـيـرفـَر {idx+1}"
        link = server.get("link", "")

        text = (
            f"🌐 <b>{name}</b>\n"
            f"ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
            f"📋 <b>كـُـود الـسـّيـرفـَـر:</b>\n\n"
            f"<code>{link}</code>\n\n"
            f"ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
            f"👇 <b>الـمـِس الـكـُود لـِلـنـّسـخ، أو اضـغـَط الـزّر بـِالأسـفـَل:</b>"
        )

        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("📋・إرسـَال الـكـُود بـِـرِسـالـَة لـِلـنـّسـخ", callback_data=f"send_code|{idx}", style="primary"))
        kb.add(types.InlineKeyboardButton("🔙・رجـُـوع لـِلـسـّيـرفـَـرات", callback_data="user|servers", style="danger"))

        try:
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data.startswith("send_code|"):
        idx = int(data.split("|")[1])
        servers = load_data()
        if 0 <= idx < len(servers):
            link = servers[idx].get("link", "")
            bot.send_message(
                call.message.chat.id,
                f"<code>{link}</code>",
                parse_mode="HTML"
            )
            bot.answer_callback_query(call.id, "✅ تـَمّ إرسـَال الـكـُود، الـمـِسـه لـِلـنـّسـخ الـفـَـوْري!", show_alert=False)
        else:
            bot.answer_callback_query(call.id, "❌ الـسـّيـرفـَر غـَيـر مـُتـَوفـّر", show_alert=True)
        return

    # عمليات الأدمن
    if not is_admin(uid):
        bot.answer_callback_query(call.id, "❌ خـَاص بـِالـمـُشـرِف فـَقـَط")
        return

    if data == "back_admin":
        USER_STATE.pop(uid, None)
        try:
            bot.edit_message_text(
                "🎛️ <b>لـَـوْحـَة تـَحـَكـّم الأدْمـِـن</b>\n"
                "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n"
                "اخـتـَـر الـعـَمـَلـِيـّة الـمـَطـلـُـوبـَة مـِن الأسـفـَل 👇",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=admin_menu()
            )
        except Exception:
            pass
        return

    if data == "admin|add":
        USER_STATE[uid] = {"step": "waiting_server_name"}
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("❌・إلـغـَـاء", callback_data="back_admin", style="danger"))
        try:
            bot.edit_message_text(
                "✍️ <b>أرسـِـل اسـِـم الـسـّيـرفـَـر الـمـَطـلـُـوب:</b>\n"
                "<i>(مـِثـَال: Germany 01 🇩🇪)</i>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data == "admin|ban":
        USER_STATE[uid] = {"step": "waiting_ban_id"}
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("❌ إلـغـَـاء", callback_data="back_admin", style="danger"))
        try:
            bot.edit_message_text(
                "🚫 <b>أرسـِـل آيـِدي (ID) الـمـُسـتـَخـدم لـِحـَـظـره:</b>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data == "admin|unban":
        USER_STATE[uid] = {"step": "waiting_unban_id"}
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("❌ إلـغـَـاء", callback_data="back_admin", style="danger"))
        try:
            bot.edit_message_text(
                "✅ <b>أرسـِـل آيـِدي (ID) الـمـُسـتـَخـدم لـِفـَك حـَـظـره:</b>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data == "admin|list":
        servers = load_data()
        if not servers:
            bot.answer_callback_query(call.id, "⚪ لا تـُـوجـَد سـِـيـرفـَـرات مـَحـفـُوظـَة.")
            return

        text = (
            "📋 <b>قـَائـِمـَة الـسـّيـرفـَـرات الـمـَحـفـُـوظـَة:</b>\n"
            "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n\n"
        )
        for i, s in enumerate(servers, 1):
            name = s.get("name") or f"سيرفر {i}"
            text += f"{i}・🟢 {name}\n"
        text += f"\n📊 <b>الـمـَجـمـُـوع:</b> {len(servers)} سـِـيـرفـَر"

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙・رجـُـوع", callback_data="back_admin", style="danger"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
        return

    if data == "admin|stats":
        users = load_users()
        servers = load_data()
        banned = load_banned()

        text = (
            "📊 <b>إحـصـَائـِيـّات الـبـُـوت</b>\n"
            "ـ ـ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ــ ـ\n\n"
            f"👥 <b>عـَدَد الـمـُسـتـَخـدمـِيـن:</b> {len(users)}\n"
            f"📦 <b>إجـمـَالـِي الـسـّيـرفـَـرات:</b> {len(servers)}\n"
            f"🚫 <b>عـَدَد الـمـَحـظـُورِيـن:</b> {len(banned)}\n"
        )

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙・رجـُـوع", callback_data="back_admin", style="danger"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
        return

    if data == "admin|del":
        servers = load_data()
        if not servers:
            bot.answer_callback_query(call.id, "⚪ لا تـُـوجـَد سـِـيـرفـَـرات لـِحـَذفـِهـَا")
            return
        kb = types.InlineKeyboardMarkup(row_width=1)
        for i, s in enumerate(servers):
            name = s.get("name") or f"سـِـيـرفـَر {i+1}"
            kb.add(types.InlineKeyboardButton(f"🗑️・{name}", callback_data=f"del|{i}", style="danger"))
        kb.add(types.InlineKeyboardButton("🔙・رجـُـوع", callback_data="back_admin", style="primary"))
        try:
            bot.edit_message_text(
                "🗑️ <b>اخـتـَـر الـسـّيـرفـَـر الـمـُراد حـَـذفـُـه:</b>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data.startswith("del|"):
        idx = int(data.split("|")[1])
        servers = load_data()
        if 0 <= idx < len(servers):
            removed = servers.pop(idx)
            save_data(servers)
            bot.answer_callback_query(call.id, f"تـَمّ حـَذف: {removed.get('name', 'الـسـّيـرفـَر')}")
        else:
            bot.answer_callback_query(call.id, "لـَم يـَعـُد مـَوجـُوداً")

        if servers:
            kb = types.InlineKeyboardMarkup(row_width=1)
            for i, s in enumerate(servers):
                name = s.get("name") or f"سـِـيـرفـَر {i+1}"
                kb.add(types.InlineKeyboardButton(f"🗑️・{name}", callback_data=f"del|{i}", style="danger"))
            kb.add(types.InlineKeyboardButton("🔙・رجـُـوع", callback_data="back_admin", style="primary"))
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
            except Exception:
                pass
        else:
            try:
                bot.edit_message_text("⚪ لا تـُـوجـَد سـِـيـرفـَـرات الآن.", call.message.chat.id, call.message.message_id, reply_markup=admin_menu())
            except Exception:
                pass
        return

    if data == "admin|clear":
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("🔴・نـَعـَم، احـذِف الـكـُـلّ", callback_data="clear|yes", style="danger"),
            types.InlineKeyboardButton("⚪・إلـغـَـاء", callback_data="back_admin", style="primary"),
        )
        try:
            bot.edit_message_text(
                "⚠️ <b>تـَحـذِيـر:</b> هـَل أنـتَ مـُتـَأكـّد مـِن حـَذف كـَافـّة الـسـّيـرفـَـرات؟",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
        return

    if data == "clear|yes":
        save_data([])
        try:
            bot.edit_message_text(
                "✅ <b>تـَـمّ حـَذف كـَافـّة الـسـّيـرفـَـرات بـِنـَجـاح.</b>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=admin_menu()
            )
        except Exception:
            pass
        return

    if data == "admin|broadcast":
        BROADCAST_STATE[uid] = True
        try:
            bot.edit_message_text(
                "📢 <b>أرسـِـل الآن الـرّسـالـَة الـمـُراد إذاعـَتـُهـا:</b>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    if data == "noop":
        bot.answer_callback_query(call.id)
        return


# ============================================
# الـتـّشـغـِـيـل
# ============================================

if __name__ == "__main__":
    print("=" * 40)
    print("Bot is running...")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"Servers loaded: {len(load_data())}")
    print(f"Users registered: {len(load_users())}")
    print(f"Banned count: {len(load_banned())}")
    print("=" * 40)

    try:
        bot.delete_webhook()
        bot.get_updates(offset=-1)
    except Exception as e:
        print(f"تـَنـبـِيـه: {e}")

    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Starting polling...")
            bot.infinity_polling(none_stop=True, interval=1, timeout=30, skip_pending=True)
        except Exception as e:
            print(f"❌ تـَـوَقـّف: {e}")
            time.sleep(5)
و 

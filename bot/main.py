import logging
import os
from dotenv import load_dotenv  # Import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import asyncio
import threading
import nest_asyncio
import time  # Import time untuk menghitung uptime
import json
nest_asyncio.apply()
from bot.utilities.http_server import run_http_server  # Import server HTTP jika diperlukan

# Muat variabel lingkungan dari .env
load_dotenv()

# Aktifkan logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token bot Anda
TOKEN = os.getenv('API_TOKEN')  # Ambil dari .env

# Fungsi untuk memuat pengaturan dari file JSON
def load_settings():
    try:
        with open('bot/settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "GROUP_ID": None,
            "ADMIN_ID": [],
            "TOPIC_IDS": ""
        }

# Memuat pengaturan saat bot dijalankan
settings = load_settings()
GROUP_ID = settings["GROUP_ID"]  # Ambil GROUP_ID dari settings.json
ADMIN_ID = settings["ADMIN_ID"]  # Ambil ADMIN_ID dari settings.json
TOPIC_IDS = settings["TOPIC_IDS"].split(',')  # Ambil TOPIC_IDS dari settings.json

# Variabel untuk menyimpan pesan yang diterima
received_content = None

# Waktu mulai bot
start_time = time.time()  # Menyimpan waktu saat bot pertama kali dijalankan

# Fungsi untuk menyimpan pengaturan ke file JSON
def save_settings(settings):
    with open('bot/settings.json', 'w') as f:  # Pastikan jalur sesuai
        json.dump(settings, f)

# Fungsi untuk menangani pesan yang diterima
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global received_content

    # Cek apakah pesan diterima di chat pribadi dan dari admin
    if update.effective_chat.type == 'private' and str(update.effective_user.id) in ADMIN_ID:
        received_content = update.message  # Simpan seluruh objek pesan
        await send_topic_buttons(update, context)  # Kirim tombol topik
    elif update.effective_chat.type != 'private':
        # Jika pesan diterima di grup, tidak melakukan apa-apa
            return

# Fungsi untuk mengirim tombol topik
async def send_topic_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for topic in TOPIC_IDS:
        topic_id, topic_name = topic.split(';')  # Pisahkan ID dan nama
        keyboard.append([InlineKeyboardButton(topic_name, callback_data=topic_id)])  # Gunakan nama sebagai teks tombol

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Pilih topik untuk mengirim pesan:', reply_markup=reply_markup)

# Fungsi untuk menangani tombol yang ditekan
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    topic_id = query.data  # Ambil ID topik dari tombol yang ditekan

    try:
        # Kirim pesan yang diterima ke grup dengan ID topik yang dipilih
        if received_content:
            await context.bot.copy_message(
                chat_id=GROUP_ID,
                from_chat_id=received_content.chat.id,
                message_id=received_content.message_id,
                reply_to_message_id=None,  # Jika ingin membalas pesan tertentu
                message_thread_id=topic_id  # Menggunakan ID thread yang sesuai
            )

            # Ambil nama topik berdasarkan ID yang dipilih
            topic_name = next((name for id_name in TOPIC_IDS if id_name.startswith(topic_id) for id, name in [id_name.split(';')]), None)

            # Buat URL untuk postingan dengan format yang benar
            post_url = f"https://t.me/c/{GROUP_ID[4:]}/{topic_id}"  # Menggunakan ID grup dan ID pesan

            # Buat tombol untuk melihat postingan
            keyboard = [[InlineKeyboardButton("Lihat Topic", url=post_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(text=f'˖⁺‧₊☽◯☾₊‧⁺˖⋆\nPesan telah dikirim ke :\n\nTOPIC: {topic_name} \nID TOPIC: {topic_id}.\n˖⁺‧₊☽◯☾₊‧⁺˖⋆', reply_markup=reply_markup)
    except Exception as e:
        # Kirim pesan kesalahan
        error_message = "ID topic tidak ditemukan, silahkan update ID dengan benar."
        await query.edit_message_text(text=error_message)

        # Tunggu beberapa detik sebelum menghapus pesan kesalahan
        await asyncio.sleep(5)  # Tunggu 5 detik
        await query.delete_message()  # Hapus pesan kesalahan

# Fungsi untuk menangani perintah /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Pastikan hanya dapat diakses di chat pribadi
    if update.effective_chat.type == 'private':
        welcome_message = (
            "Selamat datang di Bot!\n"
            "Bot ini dapat membantu Anda mengirim pesan ke berbagai topik.\n"
            "Silakan pilih topik yang ingin Anda kirimkan pesan.\n"
        )
        await update.message.reply_text(welcome_message)

# Fungsi untuk menangani perintah /ping
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Pastikan hanya dapat diakses di chat pribadi
    if update.effective_chat.type == 'private':
        # Ambil waktu saat perintah dipanggil
        start_ping_time = time.time()  # Ambil waktu saat ini

        # Kirim balasan untuk perintah ping
        await update.message.reply_text("Pong!")

        # Hitung latensi setelah mengirim balasan
        latency = (time.time() - start_ping_time) * 1000  # Menghitung latensi dalam milidetik

        # Hitung uptime
        uptime = time.time() - start_time  # Menghitung uptime dalam detik
        uptime_formatted = time.strftime("%H:%M:%S", time.gmtime(uptime))  # Format uptime

        # Kirim pesan dengan latensi dan uptime
        response_message = (
            f"Kecepatan server: {latency:.2f} ms\n"
            f"Uptime: {uptime_formatted}\n"
            f"Uptime Since: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
        )
        await update.message.reply_text(response_message)

# Fungsi untuk menjalankan server HTTP di thread terpisah
def start_http_server():
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True
    server_thread.start()

# Fungsi untuk mengatur ADMIN_ID
async def set_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ADMIN_ID
    if update.effective_chat.type == 'private':
        new_admin_id = update.message.text.split()[1]
        if new_admin_id not in ADMIN_ID:
            ADMIN_ID.append(new_admin_id)  # Tambahkan ID baru ke daftar
            settings["ADMIN_ID"] = ADMIN_ID
            save_settings(settings)
            await update.message.reply_text(f'ADMIN_ID telah ditambahkan: {new_admin_id}')
        else:
            await update.message.reply_text(f'ADMIN_ID {new_admin_id} sudah ada dalam daftar.')

# Fungsi untuk mengatur GROUP_ID
async def set_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global GROUP_ID
    if update.effective_chat.type == 'private':
        new_group_id = update.message.text.split()[1]
        GROUP_ID = new_group_id
        settings["GROUP_ID"] = new_group_id
        save_settings(settings)
        await update.message.reply_text(f'GROUP_ID telah diubah menjadi: {new_group_id}')

# Fungsi untuk mengatur TOPIC_IDS
async def set_topic_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global TOPIC_IDS
    if update.effective_chat.type == 'private':
        # Ambil input dari pesan
        new_topic_ids = update.message.text.split(maxsplit=1)[1]  # Ambil teks setelah perintah
        # Memisahkan string menjadi list berdasarkan koma dan menghapus spasi
        TOPIC_IDS = [topic.strip() for topic in new_topic_ids.split(',')]  # Memisahkan string menjadi list dan menghapus spasi
        settings["TOPIC_IDS"] = ','.join(TOPIC_IDS)  # Simpan kembali ke settings
        save_settings(settings)
        await update.message.reply_text(f'TOPIC_IDS telah diubah menjadi: {", ".join(TOPIC_IDS)}')

# Fungsi untuk mengecek pengaturan aktif
async def cek_settingan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == 'private':
        settings_message = (
            f"Pengaturan Aktif:\n"
            f"GROUP_ID: {GROUP_ID}\n"
            f"ADMIN_ID: {ADMIN_ID}\n"
            f"TOPIC_IDS: {', '.join(TOPIC_IDS)}"
        )
        await update.message.reply_text(settings_message)

# Fungsi untuk menampilkan bantuan
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type == 'private':
        help_message = (
            "Perintah yang tersedia:\n"
            "/start - Memulai interaksi dengan bot.\n"
            "/ping - Mengecek apakah bot masih aktif.\n"
            "/set_admin_id <id> - Mengatur ADMIN_ID bot.\n"
            "/set_group_id <id> - Mengatur GROUP_ID bot.\n"
            "/set_topic_ids <id1;nama1,id2;nama2,...> - Mengatur TOPIC_IDS bot.\n"
            "/cek_settingan - Menampilkan pengaturan aktif saat ini.\n"
            "/help - Menampilkan daftar perintah yang tersedia."
        )
        await update.message.reply_text(help_message)

# Fungsi untuk menangani perintah /id untuk semua jenis chat
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Mendapatkan ID pengguna
    user_id = update.effective_user.id
    
    # Menyiapkan pesan untuk ID pengguna
    response_message = (
        f"ID Anda: {user_id}\n"
    )
    
    await update.message.reply_text(response_message)

# Fungsi untuk mendapatkan ID topik dari pesan yang dibalas untuk semua jenis chat
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message:
        # Mendapatkan teks dari pesan yang dibalas
        topic_message = update.message.reply_to_message.text
        
        # Cek apakah pesan tersebut adalah URL
        if "https://t.me/c/" in topic_message:
            # Ambil ID topik dari URL
            url_parts = topic_message.split('/')
            if len(url_parts) > 4:  # Pastikan ada cukup bagian dalam URL
                topic_id = url_parts[-1]  # Ambil bagian terakhir sebagai ID topik
                await update.message.reply_text(f"ID Topik: {topic_id}")
            else:
                await update.message.reply_text("Format URL tidak sesuai untuk mendapatkan ID topik.")
        else:
            await update.message.reply_text("Silakan balas pesan yang berisi URL postingan untuk mendapatkan ID topik.")
    else:
        await update.message.reply_text("Silakan balas pesan topik untuk mendapatkan ID topik.")

# Fungsi utama untuk menjalankan bot
async def main() -> None:
    # Mulai server HTTP
    start_http_server()  # Panggil server HTTP

    # Inisialisasi Application
    application = ApplicationBuilder().token(TOKEN).build()

    # Daftarkan handler untuk perintah
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('ping', ping_command))
    application.add_handler(CommandHandler('set_admin_id', set_admin_id))
    application.add_handler(CommandHandler('set_group_id', set_group_id))
    application.add_handler(CommandHandler('set_topic_ids', set_topic_ids))
    application.add_handler(CommandHandler('cek_settingan', cek_settingan))
    application.add_handler(CommandHandler('id', id_command))
    application.add_handler(CommandHandler('help', help_command))
    # Daftarkan handler untuk tombol
    application.add_handler(CallbackQueryHandler(button_handler))

    # Daftarkan handler untuk pesan yang diterima
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    # Daftarkan handler untuk mendapatkan ID topik dari pesan yang dibalas
    application.add_handler(MessageHandler(filters.ALL, handle_reply))

    # Mulai bot
    await application.run_polling()

if __name__ == '__main__':
        asyncio.run(main())

# Bot Telegram untuk Mengirim Pesan ke Topik

Pastikan untuk mengganti nilai di atas dengan informasi yang sesuai untuk bot Anda.

## Cara Menjalankan Bot

1. **Instal Dependensi**

   Pastikan Anda memiliki `python-dotenv` dan `python-telegram-bot` terinstal. Anda dapat menginstalnya dengan perintah berikut:

   ```bash
   pip install -r requirements.txt
   ```

2. **Konfigurasi Lingkungan**

   Buat file `.env` seperti yang dijelaskan di atas. Pastikan untuk mengisi variabel berikut:
   - `API_TOKEN`: Token bot Anda dari BotFather.
   - `GROUP_ID`: ID grup tempat bot akan mengirim pesan.
   - `ADMIN_ID`: ID admin yang diizinkan untuk menggunakan bot.
   - `TOPIC_IDS`: Daftar topik dalam format `id;nama`, dipisahkan dengan koma.

3. **Menjalankan Bot**

   Jalankan bot dengan perintah berikut:

   ```bash
   python -m bot.main
   ```

   Pastikan semua variabel lingkungan sudah diatur dengan benar sebelum menjalankan bot.

## Deployments

### Koyeb Deployment

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/AlekBaikHati/chpostanim&branch=main&name=teleshare&env%5BAPI_TOKEN%5D=your_api_token&env%5BGROUP_ID%5D=your_group_id&env%5BADMIN_ID%5D=your_admin_id&env%5BTOPIC_IDS%5D=your_topic_ids)

Cukup atur variabel lingkungan dan Anda sudah siap.

### Local Deployment

1. Clone the repo
   ```bash
   git clone https://github.com/zawsq/Teleshare.git
   ```
   kemudian masuk ke direktori Teleshare 
   ```bash
   cd Teleshare
   ```

2. Buat file `.env` seperti yang dijelaskan di atas.

3. Instal requirements
   ```bash
   pip install -r requirements.txt
   ```

4. Mulai bot.
   ```bash
   python -m bot.main
   ```


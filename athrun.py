import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if not WEBHOOK_URL:
    print("Error: WEBHOOK_URL belum disetting di file .env!")
    exit()

API_URL = "https://graphql.anilist.co"

waktu_sekarang = int(time.time())
waktu_besok = waktu_sekarang + 86400

# 1. Kita ubah perPage jadi 25 agar jaring pencariannya lebih luas
# 2. Kita tambahkan 'popularity' di dalam laci 'media'
query_anilist = '''
query ($awal: Int, $akhir: Int) {
  Page(page: 1, perPage: 60) {
    airingSchedules(airingAt_greater: $awal, airingAt_lesser: $akhir, sort: TIME) {
      episode
      airingAt
      media {
        title {
          romaji
        }
        popularity
        coverImage {
          large
        }
      }
    }
  }
}
'''

variabel_waktu = {
    "awal": waktu_sekarang,
    "akhir": waktu_besok
}

print("Mencari 60 jadwal rilis hari ini untuk disaring...")

try:
    respons = requests.post(API_URL, json={'query': query_anilist, 'variables': variabel_waktu}, timeout=10)

    if respons.status_code == 200:
        data_json = respons.json()
        daftar_jadwal_mentah = data_json["data"]["Page"]["airingSchedules"]
        
        # --- LOGIKA FILTERING BARU ---
        # Ini adalah padanan dari fungsi array.sort() di JavaScript/TypeScript.
        # Kita menggunakan 'lambda' untuk menunjuk laci mana yang jadi patokan urutan (yaitu popularity).
        # reverse=True artinya diurutkan dari angka paling besar (terpopuler) ke kecil.
        jadwal_populer = sorted(daftar_jadwal_mentah, key=lambda x: x["media"]["popularity"], reverse=True)
        
        daftar_embed = []
        
        # Sekarang kita hanya mengambil 3 teratas dari list yang sudah disaring
        for jadwal in jadwal_populer[:7]:
            anime = jadwal["media"]
            judul = anime["title"]["romaji"]
            episode = jadwal["episode"]
            url_poster = anime["coverImage"]["large"]
            popularitas = anime["popularity"]
            
            waktu_mentah = jadwal["airingAt"]
            jam_tayang = datetime.fromtimestamp(waktu_mentah).strftime('%H:%M WIB')
            
            kartu = {
                "title": judul,
                # Menambahkan info Popularitas di dalam Embed agar terlihat keren
                "description": f"📺 **Rilis Episode:** {episode}\n⏰ **Jam Tayang:** {jam_tayang}\n🔥 **Skor Populer:** {popularitas:,}",
                "color": 3447003, 
                "thumbnail": {
                    "url": url_poster
                }
            }
            daftar_embed.append(kartu)
            
        paket_data = {
            "content": "📅 **Jadwal Rilis Anime Terpopuler Hari Ini** 📅",
            "embeds": daftar_embed
        }
        
        print("Mengirim jadwal terpopuler ke Discord...")
        kirim_discord = requests.post(WEBHOOK_URL, json=paket_data)
        
        if kirim_discord.status_code == 204:
            print("Berhasil! Cek Discord kamu sekarang.")
        else:
            print(f"Gagal mengirim. Error kode: {kirim_discord.status_code}")
            
    else:
        print(f"Server AniList membalas dengan error kode: {respons.status_code}")

except Exception as error:
    print(f"Terjadi kesalahan: {error}")
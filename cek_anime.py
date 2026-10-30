import requests

# Kita ganti target ke Kitsu API
url_api = "https://kitsu.io/api/edge/trending/anime"

print("Mengetuk pintu server Kitsu API...")

try:
    respons = requests.get(url_api, timeout=10)

    if respons.status_code == 200:
        data_json = respons.json()
        daftar_anime = data_json["data"]
        
        print("Berhasil! Ini 3 anime yang lagi trending:\n")
        
        for anime in daftar_anime[:3]:
            # Perhatikan: Di Kitsu, judul ada di dalam laci "attributes"
            judul = anime["attributes"]["canonicalTitle"]
            rating = anime["attributes"]["averageRating"]
            status = anime["attributes"]["status"]
            
            print(f"- Judul: {judul}")
            print(f"  Status: {status}")
            print(f"  Rating: {rating}")
            print("-" * 20)
    else:
        print(f"Server membalas dengan error kode: {respons.status_code}")

except requests.exceptions.Timeout:
    print("Oops! Server Kitsu lambat merespons (Timeout).")
except requests.exceptions.ConnectionError:
    print("Oops! Gagal terhubung sama sekali.")
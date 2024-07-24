import requests
from bs4 import BeautifulSoup

def scraper_kompas(link_berita):
    try:
        headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
        print("lolos sini")
        response_berita = requests.get(link_berita,headers=headers)
        print("ini responnya :", response_berita)
        response_berita.raise_for_status()

        soup = BeautifulSoup(response_berita.content, 'html.parser')

        judul_berita = soup.find('h1', class_='read__title').text.strip()
        print(judul_berita)

        konten_berita = ''
        for p_tag in soup.select('.read__content p'):
            if not any(a_tag.has_attr('class') and ('inner-link-baca-juga' in a_tag['class'] or 'inner-link-tag' in a_tag['class']) for a_tag in p_tag.find_all('a')):
                konten_berita += p_tag.text.strip() + ' '

        # URL API komentar
        url_api_komentar = f'https://apis.kompas.com/api/comment/v2/list?urlpage={link_berita}&json&limit=1000'
        response_api = requests.get(url_api_komentar, headers=headers)

        # Ambil daftar komentar dari JSON response
        komentar_json_list = response_api.json().get('result', {}).get('komentar', [])

        # Inisialisasi daftar untuk menyimpan komentar
        komentar_list = []

        # Fungsi untuk memproses komentar dan balasannya
        def process_komentar(komentar_json):
            nama_penulis = komentar_json.get('user_fullname', 'Anonymous')
            isi_komentar = komentar_json.get('comment_text', '').replace('\n', '').replace('$//$', '')
            komentar_list.append({'username': nama_penulis, 'komentar': isi_komentar})

            # Cek apakah ada balasan
            if 'reply' in komentar_json and komentar_json['reply']:
                for reply in komentar_json['reply']:
                    process_komentar(reply)

        # Proses semua komentar
        for komentar_json in komentar_json_list:
            process_komentar(komentar_json)

        # Buat hasil scraping
        hasil_scrape = {
            'link': link_berita,
            'judul': judul_berita,
            'konten': konten_berita.strip(),
            'komentar': komentar_list,
            'jumlah_komentar': len(komentar_list)
        }

        # Return hasil_scrape
        return hasil_scrape

    except Exception as e:
        error_message = f"Error in scraping data for link {link_berita}: {str(e)}"
        return {'error': error_message}
        

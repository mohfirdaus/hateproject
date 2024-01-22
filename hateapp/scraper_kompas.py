import requests
from bs4 import BeautifulSoup

def scraper_kompas(link_berita):
    try:
        response_berita = requests.get(link_berita)
        response_berita.raise_for_status()

        soup = BeautifulSoup(response_berita.content, 'html.parser')

        judul_berita = soup.find('h1', class_='read__title').text.strip()

        konten_berita = ''
        for p_tag in soup.select('.read__content p'):
            if not any(a_tag.has_attr('class') and ('inner-link-baca-juga' in a_tag['class'] or 'inner-link-tag' in a_tag['class']) for a_tag in p_tag.find_all('a')):
                konten_berita += p_tag.text.strip() + ' '

        url_api_komentar = f'https://apis.kompas.com/api/comment/v2/list?urlpage={link_berita}&json&limit=9999'
        response_api = requests.get(url_api_komentar)

        komentar_json_list = response_api.json().get('result', {}).get('komentar', [])

        komentar_list = []
        for komentar_json in komentar_json_list:
            nama_penulis = komentar_json.get('user_fullname', 'Anonymous')
            isi_komentar = komentar_json.get('comment_text', '').replace('\n', '').replace('$//$','')
            komentar_list.append({'username': nama_penulis, 'komentar': isi_komentar})

        hasil_scrape = {
            'link': link_berita,
            'judul': judul_berita,
            'konten': konten_berita.strip(),
            'komentar': komentar_list,
            'jumlah_komentar': len(komentar_list)
        }

        return hasil_scrape

    except Exception as e:
        error_message = f"Error in scraping data for link {link_berita}: {str(e)}"
        return {'error': error_message}
        

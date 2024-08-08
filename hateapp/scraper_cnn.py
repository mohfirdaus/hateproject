from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup, Tag
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time 

def scraper_cnn(link_berita):
    chrome_options = Options()
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')  # Run in headless mode
    # Menonaktifkan JavaScript di seluruh halaman
    chrome_options.add_argument('--disable-javascript')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.binary_location = "/usr/bin/google-chrome"  # Sesuaikan path dengan lokasi Chrome di sistem Anda

    print("ini masuk di def cnn")
    # Initialize the driver with the service and options
    driver = webdriver.Chrome(options=chrome_options)
    print("haiiiii")

    try:
        # ambil judul berita
        soup_title = BeautifulSoup(requests.get(link_berita).text, "html.parser")
        title = soup_title.find("h1", class_='text-cnn_black').text.strip()

        # ambil konten berita
        content = ' '.join([p.get_text().strip() for p in BeautifulSoup(requests.get(link_berita).text, 'html.parser').find('div', class_='detail-text text-cnn_black text-sm grow min-w-0').find_all('p') if not (p.find_parent("div", class_="paradetail") and p.find_parent("div", class_="detail-text text-cnn_black text-sm grow min-w-0"))]) or "Main div not found."

        # buka url yg di-assign pada browser
        driver.get(link_berita)
        
        driver.execute_script("""
            var elements = document.querySelectorAll('body *:not(iframe)');
            elements.forEach(function(el) {
                el.style.display = 'none';
            });
        """)

        # Tunggu hingga iframe tersedia dan pindah ke iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="comment_component"]'))
        )
        driver.switch_to.frame(iframe)

        # Variabel untuk menyimpan komentar
        all_comments = []

        # Tunggu beberapa detik untuk memastikan elemen ter-load
        time.sleep(2)

        # Klik semua tombol "more" hingga tidak ada lagi
        while True:
            try:
                # Tunggu hingga tombol "more" dapat diklik
                wait = WebDriverWait(driver, 10)
                more_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.komentar-iframe-min-btn.komentar-iframe-min-btn--outline')))
                if not more_buttons:
                    print("Tidak ada tombol 'more' ditemukan. Mengakhiri pencarian.")
                    break

                for more_button in more_buttons:
                    driver.execute_script("arguments[0].click();", more_button)
                    print("Tombol 'more' diklik.")
                    # Tunggu beberapa saat untuk memastikan tombol sudah diklik dan konten diperbarui
                    time.sleep(2)

            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                print(f"Kesalahan saat mengklik tombol 'more': {e}")
                break

        # Klik semua tombol "reply" hingga tidak ada lagi
        while True:
            try:
                reply_buttons = driver.find_elements(By.CSS_SELECTOR, '.komentar-iframe-min-comment-link')
                all_replies_hidden = True
                for reply_button in reply_buttons:
                    span_text = reply_button.find_element(By.CSS_SELECTOR, 'span').text
                    if "Sembunyikan" not in span_text:
                        driver.execute_script("arguments[0].click();", reply_button)
                        print(f"Tombol 'lihat reply' diklik. ({span_text})")
                        all_replies_hidden = False
                        time.sleep(2)

                if all_replies_hidden:
                    print("Semua tombol 'lihat reply' telah berubah menjadi 'Sembunyikan X balasan'.")
                    break

            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                print(f"Kesalahan saat mengklik tombol 'reply': {e}")
                break

        # Ambil semua komentar yang ada
        comments = driver.find_elements(By.CSS_SELECTOR, '.komentar-iframe-min-media__desc')
        for comment in comments:
            all_comments.append(comment.text)

        # Parsing HTML dengan BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Temukan elemen-elemen tag komentar dan username
        comment_elements = soup.select('.komentar-iframe-min-media__desc') 
        user_elements = soup.select('.komentar-iframe-min-media__user')

        # Simpan data ke dalam dictionary data
        data = {
            'judul': title,
            'link': link_berita,
            'konten': content,
            'komentar': [],  # 
            'jumlah_komentar': 0  
        }

        # loop untuk assign komentar kedalam directory
        for user, comment in zip(user_elements, comment_elements):
            if not comment.text.strip().startswith('@'):
                data['komentar'].append({
                    'username': user.text.strip(),
                    'komentar': comment.text.strip()
                })
                data['jumlah_komentar'] += 1
        return data

    except Exception as e:
        error_message = f"Error in scraping data for link {link_berita}: {str(e)}"
        return {'error': error_message}
    
    finally:
        driver.quit()
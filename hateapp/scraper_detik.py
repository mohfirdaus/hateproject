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
import urllib.request

def scraper_detik(link_berita):
    # Inisialisasi WebDriver lokal dengan Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # jalankan browser tanpa GUI
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    try:
        # ambil judul berita
        soup_title = BeautifulSoup(requests.get(link_berita).text, "html.parser")
        title = soup_title.find("h1", class_='detail__title').text.strip()

        # ambil konten berita
        content = ' '.join([p.get_text() for p in BeautifulSoup(urllib.request.urlopen(link_berita).read(), 'html.parser').find('div', class_='detail__body-text itp_bodycontent').find_all(lambda tag: isinstance(tag, Tag) and tag.name == 'p' and 'parallaxindetail scrollpage' not in tag.get('class', []), recursive=False)])

        # buka url yg di-assign pada browser
        driver.get(link_berita)

        # iframe dengan atribut title="comment_component" yg dimana terdapat komentar
        iframe = driver.find_element_by_css_selector('iframe[title="comment_component"]')

        driver.switch_to.frame(iframe)

        # variabel untuk menyimpan komentar
        all_comments = []

        while True:
            try:
                # tunggu hingga tombol "more" dapat diklik dan juga untuk menghindari error
                wait = WebDriverWait(driver, 10) #
                more_button = driver.find_element_by_css_selector('.komentar-iframe-min-btn.komentar-iframe-min-btn--outline')

                # klik button "more"
                driver.execute_script("arguments[0].click();", more_button)
                
                # tunggu hingga komentar yang baru dimuat muncul
                comments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.komentar-iframe-min-media__desc')))
                
                # komentar yg muncul di-assign ke variabel all_comments 
                all_comments.extend(comments)

                # refresh iframe
                driver.switch_to.default_content()
                driver.switch_to.frame(iframe)

            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                # tombol "more" sudah tidak ada atau sudah berada dikomen paling bawah
                break

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
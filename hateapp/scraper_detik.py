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
import time
import logging

def scraper_detik(link_berita):
    # Inisialisasi WebDriver lokal dengan Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # jalankan browser tanpa GUI
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    #driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options)
    try:
        # ambil judul berita
        soup_title = BeautifulSoup(requests.get(link_berita).text, "html.parser")
        title = soup_title.find("h1", class_='detail__title').text.strip()
        print(title)
        # ambil konten berita
        content = ' '.join([p.get_text() for p in BeautifulSoup(urllib.request.urlopen(link_berita).read(), 'html.parser').find('div', class_='detail__body-text itp_bodycontent').find_all(lambda tag: isinstance(tag, Tag) and tag.name == 'p' and 'parallaxindetail scrollpage' not in tag.get('class', []), recursive=False)])
        print(content)
        # buka url yg di-assign pada browser
        driver.get(link_berita)
        print("website dimuat dulu")
        time.sleep(15)
        print("website telah melewati masa")
        # iframe dengan atribut title="comment_component" yg dimana terdapat komentar
        iframe = driver.find_element_by_css_selector('iframe[title="comment_component"]')
        # print(iframe)
        driver.switch_to.frame(iframe)

        # variabel untuk menyimpan komentar
        all_comments = []

        # Find the div element with class "komentar-iframe-min-comment-entry"
        div_element = driver.find_element_by_css_selector("div.komentar-iframe-min-comment-entry")

        # Get the text content inside the div element
        text_content = div_element.text

        # Print the text content
        print("*"*100)
        print(text_content)
        print("*"*100)

        while driver.find_elements_by_css_selector('.komentar-iframe-min-text-center.komentar-iframe-min-mgt-16'):
            try:
                logging.info("Trying to click 'more' button.")
                print(logging.info)
                
                # Your existing code
                wait = WebDriverWait(driver, 10)
                more_button = driver.find_element_by_css_selector('.komentar-iframe-min-btn.komentar-iframe-min-btn--outline')
                driver.execute_script("arguments[0].click();", more_button)
                comments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.komentar-iframe-min-media__desc')))
                all_comments.extend(comments)

                # Refresh iframe
                driver.switch_to.default_content()
                driver.switch_to.frame(iframe)
                logging.info("Successfully clicked 'more' button and retrieved comments.")

            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                logging.warning(f"Exception occurred: {e}")
                # Handle exceptions as needed
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

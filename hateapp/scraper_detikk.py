# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
# from bs4 import BeautifulSoup, Tag
# from webdriver_manager.chrome import ChromeDriverManager
# import logging, traceback, time, urllib.request, requests

# def scraper_detik(link_berita):
#     # Inisialisasi WebDriver lokal dengan Chrome
#     # chrome_options = Options()
#     # chrome_options.add_argument('start-maximized')
#     # chrome_options.add_argument('--disable-extensions')
#     # chrome_options.add_argument('--disable-gpu')
#     # # service_log_path = "{}/chromedriver.log".format('/tmp/local/')
#     # service_args = ['--verbose']
#     # # chrome_options.add_argument('--no-sandbox')
#     # chrome_options.add_argument(
#     # "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
#     # chrome_options.set_headless(headless=True)
#     # chrome_options.add_argument("--ignore-certificate-errors")
#     # chrome_options.add_argument("--enable-javascript")
#     # # chrome_options.add_argument("--incognito")
#     # driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options, service_args=service_args)
#     # driver = webdriver.Chrome("/usr/bin/chromedriver", options=chrome_options, service_args=service_args)
#     chrome_options = Options()
#     chrome_options.add_argument('--headless')  # jalankan browser tanpa GUI
#     driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
#     try:
#         # ambil judul berita
#         soup_title = BeautifulSoup(requests.get(link_berita).text, "html.parser")
#         title = soup_title.find("h1", class_='detail__title').text.strip()
#         print(title)
#         # ambil konten berita
#         content = ' '.join([p.get_text() for p in BeautifulSoup(urllib.request.urlopen(link_berita).read(), 'html.parser').find('div', class_='detail__body-text itp_bodycontent').find_all(lambda tag: isinstance(tag, Tag) and tag.name == 'p' and 'parallaxindetail scrollpage' not in tag.get('class', []), recursive=False)])
#         print(content)
#         # buka url yg di-assign pada browser
#         driver.get(link_berita)
#         print("website dimuat dulu")
#         time.sleep(15)
#         print("website telah melewati masa")
#         # iframe dengan atribut title="comment_component" yg dimana terdapat komentar
#         iframe = driver.find_element_by_css_selector('iframe[title="comment_component"]')
#         # print(iframe)
#         driver.switch_to.frame(iframe)

#         # Scroll down using JavaScript within the iframe
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#         # variabel untuk menyimpan komentar
#         all_comments = []
#         wait = WebDriverWait(driver, 20)

#         lebihbanyak = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.komentar-iframe-min-btn.komentar-iframe-min-btn--outline')))
#         text_content = lebihbanyak.text

#         # Print the text content
#         print("*"*100)
#         print(text_content)
#         print("*"*100)
#         # while driver.find_elements_by_css_selector('.komentar-iframe-min-text-center.komentar-iframe-min-mgt-16')

#         # Create WebDriverWait instance outside the loop
#         wait = WebDriverWait(driver, 20)

#         while True:
#             try:
#                 print("Trying to find 'more' button.")
                
#                 # Check if the 'more' button exists
#                 more_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.komentar-iframe-min-btn.komentar-iframe-min-btn--outline')))
                
#                 print("'More' button found. Clicking it.")
                
#                 # Your existing code
#                 driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", more_button)

#                 comments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.komentar-iframe-min-media__desc')))
#                 soup = BeautifulSoup(driver.page_source, 'html.parser')
#                 print(soup)

#                 # Refresh iframe if needed
#                 # driver.switch_to.default_content()
#                 # driver.switch_to.frame(iframe)
#                 time.sleep(2)
                
#                 print("Successfully clicked 'more' button and retrieved comments.")
                
#             except Exception as e:
#                 traceback.print_exc()
#                 print(f"Exception occurred: {e}. Retrying...")
#                 break  # Continue to the next iteration of the loop

#             # Break out of the loop if no exception occurs
#         StopIteration()

#         # Parsing HTML dengan BeautifulSoup
#         soup = BeautifulSoup(driver.page_source, 'html.parser')

#         # Temukan elemen-elemen tag komentar dan username
#         comment_elements = soup.select('.komentar-iframe-min-media__desc') 
#         user_elements = soup.select('.komentar-iframe-min-media__user')

#         # Simpan data ke dalam dictionary data
#         data = {
#             'judul': title,
#             'link': link_berita,
#             'konten': content,
#             'komentar': [],  # 
#             'jumlah_komentar': 0  
#         }

#         # loop untuk assign komentar kedalam directory
#         for user, comment in zip(user_elements, comment_elements):
#             if not comment.text.strip().startswith('@'):
#                 data['komentar'].append({
#                     'username': user.text.strip(),
#                     'komentar': comment.text.strip()
#                 })
#                 data['jumlah_komentar'] += 1
#         return data

#     except Exception as e:
#         error_message = f"Error in scraping data for link {link_berita}: {str(e)}"
#         return {'error': error_message}
    
#     finally:
#         driver.quit()

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

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

    try:
        # ambil judul berita
        link_berita = link_berita
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
                # Tunggu hingga tombol "more" dapat diklik
                wait = WebDriverWait(driver, 10)
                more_button = driver.find_element_by_css_selector('.komentar-iframe-min-btn.komentar-iframe-min-btn--outline')
                driver.execute_script("arguments[0].click();", more_button)

                # Tunggu hingga komentar yang baru dimuat muncul
                comments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.komentar-iframe-min-media__desc')))
                all_comments.extend(comments)

                # Ambil semua tombol "reply" dan klik jika tidak mengandung kata "Sembunyikan"
                reply_buttons = driver.find_elements_by_css_selector('.komentar-iframe-min-comment-link')
                for reply_button in reply_buttons:
                    if "Sembunyikan" not in reply_button.text:
                        driver.execute_script("arguments[0].click();", reply_button)

                print(all_comments)

                # Refresh iframe
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

        # # Simpan data ke dalam dictionary data
        # data = {
        #     'judul': title,
        #     'link': link_berita,
        #     'konten': content,
        #     'komentar': [],  # 
        #     'jumlah_komentar': 0  
        # }

        # # loop untuk assign komentar kedalam directory
        # for user, comment in zip(user_elements, comment_elements):
        #     if not comment.text.strip().startswith('@'):
        #         data['komentar'].append({
        #             'username': user.text.strip(),
        #             'komentar': comment.text.strip()
        #         })
        #         data['jumlah_komentar'] += 1
        # return data

        # Simpan data ke dalam dictionary data
        data = {
            'judul': title,
            'link': link_berita,
            'konten': content,
            'komentar': [],
            'jumlah_komentar': 0  
        }

        # Set untuk melacak komentar yang sudah ditambahkan
        komentar_set = set()

        # Loop untuk assign komentar ke dalam dictionary
        for user, comment in zip(user_elements, comment_elements):
            comment_text = comment.text.strip()
            # not comment_text.startswith('@') and
            if comment_text not in komentar_set:
                data['komentar'].append({
                    'username': user.text.strip(),
                    'komentar': comment_text
                })
                data['jumlah_komentar'] += 1
                komentar_set.add(comment_text)

        return data

    except Exception as e:
        error_message = f"Error in scraping data for link {link_berita}: {str(e)}"
        return {'error': error_message}
    
    finally:
        driver.quit()

import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
from bs4 import BeautifulSoup, Tag
import requests, urllib
import asyncio
import nest_asyncio
from pyppeteer import launch
import pandas as pd

nest_asyncio.apply()

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_iframe_content(url_main):
    link_berita = url_main
    soup_title = BeautifulSoup(requests.get(link_berita).text, "html.parser")
    title = soup_title.find("h1", class_='detail__title').text.strip()
    print(title)

    # ambil konten berita
    content = ' '.join([p.get_text() for p in BeautifulSoup(urllib.request.urlopen(link_berita).read(), 'html.parser').find('div', class_='detail__body-text itp_bodycontent').find_all(lambda tag: isinstance(tag, Tag) and tag.name == 'p' and 'parallaxindetail scrollpage' not in tag.get('class', []), recursive=False)])
    print(content)

    # Apply nest_asyncio to allow nested event loops
    nest_asyncio.apply()

    async def fetch_iframe_content_by_title():
        # Meluncurkan browser dengan argumen tambahan
        browser = await launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.newPage()

        try:
            logger.info(f"Navigating to {url_main}")
            response = await page.goto(url_main, {'waitUntil': 'networkidle2', 'timeout': 6000000})
            print(response)
            # logger.info(f"Page loaded with status: {response.status}")

            try:
                # Tunggu hingga iframe dengan title 'comment_component' muncul
                await page.waitForSelector('iframe[title="comment_component"]', {'timeout': 60000})

                # Temukan iframe dengan title 'comment_component'
                iframe_element = await page.querySelector('iframe[title="comment_component"]')

                if iframe_element:
                    frame = await iframe_element.contentFrame()

                    while True:
                        more_buttons = await frame.querySelectorAll('.komentar-iframe-min-btn.komentar-iframe-min-btn--outline')
                        if more_buttons:
                            for button in more_buttons:
                                await button.click()
                                print("Tombol 'more' diklik.")
                                # Tunggu beberapa saat untuk memastikan tombol sudah diklik dan konten diperbarui
                                await asyncio.sleep(2)
                        else:
                            print("Tidak ada tombol 'more' yang ditemukan.")
                            break

                    # Loop untuk mengklik tombol "lihat reply" untuk setiap komentar
                    while True:
                        reply_buttons = await frame.querySelectorAll('.komentar-iframe-min-comment-link')
                        if reply_buttons:
                            all_replies_hidden = True
                            for button in reply_buttons:
                                span_text = await frame.evaluate('(button) => button.querySelector("span").textContent', button)
                                if 'Lihat' in span_text:
                                    await button.click()
                                    print(f"Tombol 'lihat reply' diklik. ({span_text})")
                                    all_replies_hidden = False
                                    await asyncio.sleep(2)
                            
                            if all_replies_hidden:
                                print("Semua tombol 'lihat reply' telah berubah menjadi 'Sembunyikan X balasan'.")
                                break
                        else:
                            print("Tidak ada tombol 'lihat reply' yang ditemukan.")
                            break

                    comments = []
                    comment_elements = await frame.querySelectorAll('.komentar-iframe-min-media')

                    for comment_element in comment_elements:
                        # Ambil username
                        username = await frame.evaluate('(element) => element.querySelector(".komentar-iframe-min-media__user").textContent', comment_element)

                        # Ambil isi komentar
                        comment_text = await frame.evaluate('(element) => element.querySelector(".komentar-iframe-min-media__desc").textContent', comment_element)

                        # Ambil teks dari elemen tanggal
                        date_text = await frame.evaluate('(element) => element.querySelector(".komentar-iframe-min-media__date").textContent', comment_element)

                        if "Promoted" in date_text:
                            logger.info("Komentar diabaikan karena berisi 'Promoted'.")
                            continue

                        comments.append({
                            'username': username.strip(),
                            'comment': comment_text.strip(),
                        })

                    # Simpan data ke dalam dictionary
                    data = {
                        'judul': title,
                        'link': url_main,
                        'konten': content,
                        'komentar': [],
                        'jumlah_komentar': 0  
                    }

                    # Set untuk melacak komentar yang sudah ditambahkan
                    komentar_set = set()

                    # Loop untuk assign komentar ke dalam dictionary
                    for comment in comments:
                        comment_text = comment['comment']
                        if comment_text not in komentar_set:
                            data['komentar'].append({
                                'username': comment['username'],
                                'komentar': comment_text
                            })
                            data['jumlah_komentar'] += 1
                            komentar_set.add(comment_text)

                    global_df = pd.DataFrame(data['komentar'])
                    logger.info("DataFrame komentar:")
                    logger.info(global_df)
                    return data
                else:
                    logger.error("Iframe dengan title 'comment_component' tidak ditemukan.")
                    return None
            except Exception as e:
                logger.error(f"Terjadi kesalahan saat menunggu iframe: {e}")
                return None
        except Exception as e:
            logger.error(f"Terjadi kesalahan: {e}")
            return None
        finally:
            await browser.close()

def scraper_detik(link_berita):
    return asyncio.run(fetch_iframe_content(link_berita))
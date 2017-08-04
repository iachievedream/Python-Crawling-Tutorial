import requests
import re

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from tldextract import extract

wait_list = ['https://afuntw.github.io/demo-crawling/demo-page/ex3/index1.html']
viewed_list = []
answer = []

# 當 wait list 裏面還有網址發生的情況
while wait_list != []:

    # 取出 wait list 裏面的第一個網址
    url = wait_list.pop(0)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    print('Current website: ', url)

    # 將當前頁面存入已經看過的清單
    viewed_list.append(url)

    # 取得當前頁面中的 h1 tag 並將結果存入 answer
    h1 = soup.find_all('h2')
    for tag in h1:
        answer.append(tag.text)

    # 取得頁面中的 a tag
    links = soup.find_all('a', href=True)
    for link in links:

        new_url = urljoin(url, link['href'])

        # 過濾錨點, 不需要再對相同的網頁送 request
        check_anchor = not re.match('#.*', link['href'])

        # 過濾程式碼
        check_code = not re.match('^javascript.*', link['href'])

        # 過濾協定, 只取 http 或是 https
        # Hint: 若原本 href 是相對路徑則沒有協定, 要先透過 urljoin 取得絕對路徑
        check_protocol = urlparse(new_url).scheme in ['http', 'https']

        # 實際過濾的判斷式
        if check_anchor and check_code and check_protocol:

            # 對當前 url 與新的 url 做 extract 分析網域
            root_url = extract(url)
            current_url = extract(new_url)

            # 假如是 google 短網址, 先對該 url 送 requests 然後從回應裏面看原本的 url
            if current_url.domain == 'goo' and current_url.suffix == 'gl':
                print('Check goo.gl {}'.format(current_url))
                check_real_url_response = requests.get(new_url)
                new_url = check_real_url_response.url
                current_url = extract(new_url)
                print('{} -> {}'.format(current_url, new_url))

            # 檢查 subdomain 是 www 或是與當前頁面的 subdomain 相同
            check_subdomain = current_url.subdomain == 'www' or current_url.subdomain == root_url.subdomain

            # 檢查新的 url 要與當前頁面的 domain 相同, 且符合 subdomain 需求
            if root_url.domain == current_url.domain and check_subdomain:

                # 新的 url 要符合的條件
                # 1. wait_list 裏面沒有出現
                # 2. viewed_list 也沒有出現
                if new_url not in wait_list and new_url not in viewed_list:

                    # 將新發現的超連結存入 wait list
                    wait_list.append(new_url)

    print('Answer: ', answer)
    print('Wait list: ', wait_list)
    print('Viewed list', viewed_list, '\n')

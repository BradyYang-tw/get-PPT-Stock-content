from bs4 import BeautifulSoup
import requests
import re
import time
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

import jieba
import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from os import listdir


def get_ptt_href(date, url="https://www.ptt.cc/bbs/Stock/index.html"):
    print("get_ptt_href")
    headers = {
        "cookie": "over18=1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36"

    }
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    res = s.get(url, headers=headers, timeout=30, verify=False)
    url_path = "https://www.ptt.cc"
    soup = BeautifulSoup(res.text, "html.parser")
    href = []
    count = 0
    for entry in soup.select(".r-ent"):
        if entry.select(".date")[0].text.replace(" ", '') == date:
            if entry.select('a'):
                link = entry.select('a')[0].get("href")
                if "bbs/Stock" in link and "search" not in link:
                    if "https://www.ptt.cc/bbs" not in link:
                        href.append(url_path + link + "\n")
        else:
            count = count + 1
    for i in soup.select(".btn"):
        if i.text == "‹ 上頁":
            next_href = url_path + i.get("href")
    return href, next_href, count


def get_ptt_content(href):
    print("get_ptt_content")
    href = href[:-1]
    headers = {
        "cookie": "over18=1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36"

    }
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    res = s.get(href, headers=headers, timeout=30, verify=False)
    time.sleep(3)
    title = re.sub(r'[^\w 0-9]|_', '', BeautifulSoup(res.text, "html.parser").select("title")[0].text.split("-")[0].replace(" ", ""))
    content = BeautifulSoup(res.text, "html.parser").select('.bbs-content')[2].text
    with open(f'content_{title}.txt', "a", encoding="utf-8") as cfile:
        cfile.write(content)
    return content


def show_word_cloud():
    # 設定分詞資料庫
    # https://raw.githubusercontent.com/fxsjy/jieba/master/extra_dict/dict.txt.big 右鍵另存放目錄下
    # 取得所有檔案與子目錄名稱
    files = listdir(".")
    all_lines = ""
    for f in files:
        if "content_" in f:
            with open(f, "r", encoding="utf-8") as temp:
                lines = temp.read()
            all_lines = all_lines + lines

    # print(lines.replace("推", ""))
    # all_lines = re.sub(r'([^\s\w]|_)+', '', all_lines)
    all_lines = ''.join(re.findall('[\u4e00-\u9fa5]', all_lines))  # 只抓所有漢字
    # jieba.load_userdict("word_dict.txt")
    jieba.set_dictionary("word_dict.txt")
    # jieba.analyse.set_stop_words("word_dict.txt")
    seg_list = jieba.lcut(lines)
    while ' ' in seg_list:
        seg_list.remove(' ')

    words = " ".join(seg_list)

    # tags = jieba.analyse.extract_tags(lines, topK=10, withWeight=True)
    # for tag, weight in tags:
    #     print(tag + "," + str(int(weight * 10000)))
    # myWordClode = WordCloud(background_color='white', font_path='SourceHanSansTW-Regular.otf').generate_from_frequencies(d)
    myWordClode = WordCloud(background_color='white',
                            font_path='SourceHanSansTW-Regular.otf').generate(words)

    # 用PIL顯示文字雲
    plt.imshow(myWordClode)
    plt.axis("off")
    plt.show()
    myWordClode.to_file('word_cloud.png')


if __name__ == "__main__":
    # 抓取所有指定四齊下的所有文章
    all_href = []
    date = "6/09"
    initial_href, next_href, count = get_ptt_href(date)
    print(initial_href, next_href, count)
    print("-----------------------------")
    all_href.extend(list(set(initial_href)))
    print("抓取今日文章.........")
    while count < 10:
        a, next_href, c = get_ptt_href(date, next_href)
        all_href.extend(a)
        count = count + c
    print("今日共", len(all_href), "篇文章")
    for i in all_href:
        get_ptt_content(i)
        time.sleep(5)

    # 透過文字雲顯示最多出現的字
    show_word_cloud()

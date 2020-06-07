from urllib.request import urlopen
from bs4 import BeautifulSoup
import re #引用正規化表示法
import datetime
import random
'''撰寫網站爬行程序'''
'''遍歷單一網域'''
html = urlopen('http://en.wikipedia.org/wiki/Kevin_Bacon') #找出所有網頁上的連結清單,但爬出來會發現很多不必要的東西,
bs = BeautifulSoup(html, 'html.parser')
for link in bs.find_all('a'):
    if 'href' in link.attrs:
        print(link.attrs['href'])

'''import re可以使用正規化'''
html = urlopen('http://en.wikipedia.org/wiki/Kevin_Bacon') #如果只想找到主題連結wiki有三個特徵 1.他們都在名為id的bodycontent中的div中 2.URL都沒有冒號 3.URL以/wiki/開頭
bs = BeautifulSoup(html, 'html.parser')
for link in bs.find('div', {'id':'bodyContent'}).find_all('a', href=re.compile('^(/wiki/)((?!:).)*$')):
    if 'href' in link.attrs:
        print(link.attrs['href'])

'''使用隨機種子及假亂數搜尋,讓維基百科更好用,讓爬到新的wiki連結不斷的找下一個連結'''
# random.seed(datetime.datetime.now())
# def getLinks(articleUrl):
#     html = urlopen('http://en.wikipedia.org{}'.format(articleUrl))
#     bs = BeautifulSoup(html, 'html.parser')
#     return bs.find('div', {'id':'bodyContent'}).find_all('a', href=re.compile('^(/wiki/)((?!:).)*$'))

# links = getLinks('/wiki/Kevin_Bacon') '''當網址上有中文時,需要引用from urllib.parse import quote用法把中文轉為可讀'''
# while len(links) > 0:
#     newArticle = links[random.randint(0, len(links)-1)].attrs['href']
#     print(newArticle)
#     links = getLinks(newArticle)

'''避免同一個網頁爬兩次,設定只有新的網頁要爬'''
# pages = set()
# def getLinks(pageUrl):
#     global pages
#     html = urlopen('http://en.wikipedia.org{}'.format(pageUrl)) #一開始以getlinks以空的URL呼叫,加上維基的前面後被視為維基的首頁,如果沒有跑過則加入清單,再產生新的
#     bs = BeautifulSoup(html, 'html.parser')
#     for link in bs.find_all('a', href=re.compile('^(/wiki/)')):
#         if 'href' in link.attrs:
#             if link.attrs['href'] not in pages:
#                 #We have encountered a new page
#                 newPage = link.attrs['href']
#                 print(newPage)
#                 pages.add(newPage)
#                 getLinks(newPage)
# getLinks('')

'''跨整個網站蒐集資料,建構搜尋標頭、第一段內容與編輯網頁的連結(如果有)的爬行程序'''
# pages = set()
# def getLinks(pageUrl):
#     global pages
#     html = urlopen('http://en.wikipedia.org{}'.format(pageUrl))
#     bs = BeautifulSoup(html, 'html.parser')
#     try:
#         print(bs.h1.get_text()) #發現所有標頭都在h1 - span下面也是唯一的h1
#         print(bs.find(id ='mw-content-text').find_all('p')[0]) #只要第一段文字的用法 , 中p標籤的位置
#         print(bs.find(id='ca-edit').find('span').find('a').attrs['href']) #編輯連結只出現在主題網頁,若有則會在這下面,不一定都會有編輯連結
#     except AttributeError:
#         print('This page is missing something! Continuing.')

#     for link in bs.find_all('a', href=re.compile('^(/wiki/)')):
#         if 'href' in link.attrs:
#             if link.attrs['href'] not in pages:
#                 #We have encountered a new page
#                 newPage = link.attrs['href']
#                 print('-'*20)
#                 print(newPage)
#                 pages.add(newPage)
#                 getLinks(newPage)
# getLinks('')

'''結合一組函式可以爬出各網站的程序'''
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import datetime
import random

pages = set()
random.seed(datetime.datetime.now())

#取得網頁上所有內部連結的清單
def getInternalLinks(bs, includeUrl):
    includeUrl = '{}://{}'.format(urlparse(includeUrl).scheme, urlparse(includeUrl).netloc)
    internalLinks = []
    #找出所有 "/"開頭的所有連結
    for link in bs.find_all('a', href=re.compile('^(/|.*'+includeUrl+')')):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internalLinks:
                if(link.attrs['href'].startswith('/')):
                    internalLinks.append(includeUrl+link.attrs['href'])
                else:
                    internalLinks.append(link.attrs['href'])
    return internalLinks

#取得所有網頁上的外部清單
def getExternalLinks(bs, excludeUrl):
    externalLinks = []
    #找出所有以"HTTP"連結開頭的清單
    #且不包含目前的URL
    for link in bs.find_all('a', href=re.compile('^(http|www)((?!'+excludeUrl+').)*$')):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in externalLinks:
                externalLinks.append(link.attrs['href'])
    return externalLinks

def getRandomExternalLink(startingPage):
    html = urlopen(startingPage)
    bs = BeautifulSoup(html, 'html.parser')
    externalLinks = getExternalLinks(bs, urlparse(startingPage).netloc)
    if len(externalLinks) == 0:
        print('No external links, looking around the site for one')
        domain = '{}://{}'.format(urlparse(startingPage).scheme, urlparse(startingPage).netloc)
        internalLinks = getInternalLinks(bs, domain)
        return getRandomExternalLink(internalLinks[random.randint(0,
                                    len(internalLinks)-1)])
    else:
        return externalLinks[random.randint(0, len(externalLinks)-1)]

def followExternalOnly(startingSite):
    externalLink = getRandomExternalLink(startingSite)
    print('Random external link is: {}'.format(externalLink))
    followExternalOnly(externalLink)

followExternalOnly('http://oreilly.com')

#搜尋此網站的所有外部連結
allExtLinks = set()
allIntLinks = set()


def getAllExternalLinks(siteUrl):
    html = urlopen(siteUrl)
    domain = '{}://{}'.format(urlparse(siteUrl).scheme,
                              urlparse(siteUrl).netloc)
    bs = BeautifulSoup(html, 'html.parser')
    internalLinks = getInternalLinks(bs, domain)
    externalLinks = getExternalLinks(bs, domain)

    for link in externalLinks:
        if link not in allExtLinks:
            allExtLinks.add(link)
            print(link)
    for link in internalLinks:
        if link not in allIntLinks:
            allIntLinks.add(link)
            getAllExternalLinks(link)

allIntLinks.add('http://oreilly.com')
getAllExternalLinks('http://oreilly.com')
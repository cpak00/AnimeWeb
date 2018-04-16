import flask as F
import requests
from lxml import etree
import datetime

app = F.Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if F.request.method == 'GET':
        return F.render_template('index.html', tag='index')
    elif F.request.method == 'POST':
        word = F.request.form['searchword']
        return F.render_template('index.html', result=getSearch(word), word=word, tag='index')

@app.route("/anime/<name>/", methods=['GET'])
def anime(name):
    anime = getAnimation(name)
    return F.render_template('anime.html', result=anime[0], animeName=anime[1], name=name)

@app.route("/play", methods=['GET'])
def play():
    return F.render_template('play.html')

@app.route("/history", methods=['GET'])
def history():
    return F.render_template('history.html', tag='history')

@app.route("/star", methods=['GET'])
def star():
    return F.render_template('star.html', tag='star')

@app.route("/notifaction", methods=['GET'])
def notifaction():
    notif = getNotifaction()
    today = datetime.date.today().weekday() + 3
    return F.render_template('notifaction.html', tag='notifaction', notif=notif, today=today)


def getSearch(word):
    word = word.encode('gb2312')
    r = requests.post("http://dm.tsdm.tv/search.asp", {"searchword": word})
    r.encoding = 'gb2312'
    selector = etree.HTML(r.text)
    results = selector.xpath('//div[@class="movie-chrList"]/ul/li')

    animes = []
    for each in results:
        anime = {'name': '', 'link': '', 'img': ''}
        anime['name'] = ''.join(each.xpath('./div/a/img/@alt'))
        anime['link'] = '/anime' + ''.join(each.xpath('./div/a/@href'))
        anime['img'] = locationLink(''.join(each.xpath('./div/a/img/@src')))
        animes.append(anime)
    return animes


def getAnimation(name):
    r = requests.get('http://dm.tsdm.tv/'+name)
    r.encoding = 'gb2312'
    selector = etree.HTML(r.text)
    results = selector.xpath('//div[@class="box960-mid-minfo"]//div[@class="bfdz"]/ul/ul/li/ul/li')

    anime = ''.join(selector.xpath('//div[@class="mtext"]/ul/li/h1/text()'))
    bfdz = []
    for each in results:
        info = {'location': '', 'id': ''}
        info['location'] = locationLink(''.join(each.xpath('./a/@href')))
        info['id'] = ''.join(each.xpath('./a/text()'))
        bfdz.append(info)

    return bfdz, anime


def getNotifaction():
    r = requests.post("http://dm.tsdm.tv/search.asp", {"searchword": ''})
    r.encoding = 'gb2312'
    selector = etree.HTML(r.text)
    results = selector.xpath('//div[@id="brood"]/div')
    week = []
    for day in results:
        menu = {'day': '', 'animes': []}
        menu['day'] = ''.join(day.xpath('./div[@class="title_week"]/text()'))
        animes = day.xpath('./div[@class="contect_week"]/a')
        for anime in animes:
            info = {'animeName': '', 'link': ''}
            info['link'] = '/' + ''.join(anime.xpath('./@href')).split('/')[-2]
            info['animeName'] = ''.join(anime.xpath('.//text()'))
            menu['animes'].append(info)
        menu['animes'] = menu['animes'][1:]
        week.append(menu)
    return week


def locationLink(link):
    if link[0:4] != 'http':
        link = 'http://dm.tsdm.tv' + link
    return link


app.run(host="0.0.0.0", port=80, debug=True)

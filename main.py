import base64
import feedparser
import io
import requests

from flask import Flask
from flask import render_template
from bs4 import BeautifulSoup
from wordcloud import WordCloud

app = Flask(__name__)



BBC_FEED = "http://feeds.bbci.co.uk/news/world/rss.xml"
LIMIT = 10


class Article:
    def __init__(self, url, image):
        self.url = url
        self.image = image


def get_wordcloud(text):
    pil_image = WordCloud().generate(text=text).to_image()
    img = io.BytesIO()
    pil_image.save(img, "PNG")
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return img_b64


def parse_article(article_url):
    print("Downloading {}".format(article_url))
    r = requests.get(article_url)
    soup = BeautifulSoup(r.text, "html.parser")
    ps = soup.find_all('p')
    text = "\n".join(p.get_text() for p in ps)
    return text


@app.route("/")
def home():


    feed = feedparser.parse(BBC_FEED)
    articles = []

    for article in feed['entries'][:LIMIT]:
        text = parse_article(article['link'])
        cloud = get_wordcloud(text)
        articles.append(Article(article['link'], cloud))

    return render_template('home.html', articles=articles)


if __name__ == '__main__':
    app.run('0.0.0.0')

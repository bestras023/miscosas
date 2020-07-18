import requests
import feedparser
import xml.etree.ElementTree as ET

from .models import Feeder, Item


def youtube_parser(url):
    # url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC300utwSVAYOoRLEqmsprfg"
    # url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCJl1YajcPWTeJNsQhGyMIMg"
    response = requests.get(url)
    status_code = response.status_code
    if status_code == 200:
        root = ET.fromstring(response.content)
        ns = '{http://www.w3.org/2005/Atom}'
        media_namespaces = {'media': 'http://search.yahoo.com/mrss/'}
        yt_namespaces = {'yt': 'http://www.youtube.com/xml/schemas/2015'}
        title = root.find(ns + "title").text
        link = root.findall(ns + "link")[1].get("href")
        items = root.findall(ns + "entry")
        # create Feeder row
        feed = Feeder.objects.create(feeder='Youtube Channel', title=title, link=link, item_number=len(items))
        # create Item rows
        for item in items:
            item_title = item.find(ns + "title").text
            item_link = item.find(ns + "link").get("href")
            item_description = item.find("media:group", media_namespaces).find("media:description", media_namespaces).text
            item_embedded = item.find("yt:videoId", yt_namespaces).text
            Item.objects.create(feed=feed, title=item_title, link=item_link, description=item_description, embedded=item_embedded)
    return status_code


def subreddit_parser(name):
    # name = "https://www.reddit.com/r/memes.rss"
    # name = "https://www.reddit.com/r/news.rss"
    response = feedparser.parse(name)
    status = response.get("status", 404)
    if status == 200:
        title = response['feed'].get("title", "")
        link = response['feed'].get("link", "")
        items = response['entries']
        # create Feeder row
        feed = Feeder.objects.create(feeder='SubReddit', title=title, link=link, item_number=len(items))
        # create Item rows
        for item in items:
            item_title = item.get("title", "")
            item_link = item.get("link", "")
            item_description = item.get("description", "")
            Item.objects.create(feed=feed, title=item_title, link=item_link, description=item_description)
    return status

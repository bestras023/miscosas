from rest_framework.views import APIView
from rest_framework.response import Response
from home.parser import *


class ListFeeders(APIView):

    def get(self, request):
        feedertitles = [feeder.title for feeder in Feeder.objects.all()]
        return Response(feedertitles)


class CreateFeeder(APIView):

    def post(self, request):
        feeder_name = request.POST['feeder']
        url = request.POST['url']
        if Feeder.objects.filter(link__iendswith=url).count() == 1:
            result = "exist"
            return Response(result)
        result = ""
        if feeder_name == "Youtube":
            url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + url
            result = youtube_parser(url)
        elif feeder_name == "Reddit":
            url = "https://www.reddit.com/r/" + url + ".rss"
            result = subreddit_parser(url)
        return Response(result)

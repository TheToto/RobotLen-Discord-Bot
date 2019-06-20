import os

import re
import googleapiclient.discovery
import googleapiclient.errors

from misc import settings


class YoutubeAPI:
    youtube = None
    regex_video = r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)"
    regex_playlist = r"[?&]list=([^#\&\?]+)"

    def __init__(self):
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    def get_by_video_id(self, id: str):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=id
        )
        response = request.execute()
        if len(response['items']) >= 1:
            return response['items'][0]
        return None

    def get_playlist(self, id: str):
        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=id
        )

        response = request.execute()
        if "items" in response:
            return response['items']
        return []

    def search(self, keyword: str):
        res = re.search(self.regex_video, keyword)
        if res is not None:
            vid = self.get_by_video_id(res.group(1))
            if vid is not None:
                return [vid]

        res = re.search(self.regex_playlist, keyword)
        if res is not None:
            return self.get_playlist(res.group(1))

        if len(keyword) == 11:
            vid = self.get_by_video_id(keyword)
            if vid is not None:
                return [vid]

        request = self.youtube.search().list(
            part="snippet",
            type="video",
            maxResults=5,
            q=keyword
        )
        response = request.execute()
        return response['items']



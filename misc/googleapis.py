import os
import urllib3
import random

import googleapiclient.discovery
import googleapiclient.errors
from google.cloud import texttospeech
from google.cloud import vision
from google.cloud.vision import types

from misc import settings


class YoutubeAPI:
    youtube = None

    def __init__(self):
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    def search_channel(self, keyword: str):
        request = self.youtube.search().list(
            part="snippet",
            type="channel",
            maxResults=1,
            q=keyword
        )
        response = request.execute()
        if len(response['items']) < 1:
            return None
        id = response['items'][0]['id']['channelId']
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=id
        )
        response = request.execute()
        if len(response['items']) < 1:
            return None
        return response['items'][0]


class TextToSpeech:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def process(self, sentence: str, lang: str = "fr-FR-Wavenet-D"):
        if lang is None:
            lang = "fr-FR-Wavenet-D"
        synthesis_input = texttospeech.types.SynthesisInput(text=sentence)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=lang[:5],
            name=lang,
        )
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.OGG_OPUS)
        response = self.client.synthesize_speech(synthesis_input, voice, audio_config)
        return response.audio_content

    def choose_voice(self, keyword):
        list = self.client.list_voices(keyword[:5])
        good_list = [v for v in list.voices if keyword in v.name]
        return random.choice(good_list).name


class CloudVision:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def get_image(self, link :str):
        http = urllib3.PoolManager()
        response = http.request('GET', link)
        file = response.data
        image = types.Image(content=file)
        return image

    def label(self, link: str):
        image = self.get_image(link)
        response = self.client.label_detection(image=image)
        return response.label_annotations

    def read(self, link: str):
        image = self.get_image(link)
        response = self.client.text_detection(image=image)
        return response.text_annotations[0]

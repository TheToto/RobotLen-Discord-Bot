import os
import random

import googleapiclient.discovery
import googleapiclient.errors
from google.cloud import texttospeech

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

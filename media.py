import requests
from pprint import pprint
import logging
import xml.etree.ElementTree as ET


class MediaElement:
    def __init__(self, data, s3file):
        self.payload = data
        self.s3file = s3file
        self.response = {}
        self.SECRET = ""
        self.SITE_ID = ""

    def upload(self):
        """
        Function which allows to replace the content of an EXISTING video object.
        :param site_id: <string> ID of a JWPlatform site
        :param url_path: <string> Path to media on local machine.
        :param media_id: <string> Video's object ID. Can be found within JWPlayer Dashboard.
        :return:
        """

        logging.info("Uploading Video")
        try:
            HEADERS = {"Authorization": self.SECRET, 
                "Accept": "application/json",
                "Content-Type": "application/json"}
            url = f"https://api.jwplayer.com/v2/sites/{self.SITE_ID}/media/"

            payload = {"upload": {
                    "method": "fetch",
                    "download_url": self.s3file}}

            response = requests.put(url, json=payload, headers=HEADERS)

            print("---------------")
            self.response = response.json()
            print("---------------")
        except Exception as e:
            logging.error("Encountered an error updating the video\n{}".format(e))

    def get_payload(self):
        return self.payload

    def get_response(self):
        return self.response
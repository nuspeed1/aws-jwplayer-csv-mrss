import re
import requests
from pprint import pprint

class TrackElement:
    def __init__(self, data, s3file):
        self.payload = data
        self.s3file = s3file
        self.response = {}
        self.SITE_ID = ""
        self.SECRET = ""

    # create new track
    def upload(self, metadata, media_id, local_caption_path):
        
        HEADERS = {"Authorization": self.SECRET, 
            "Accept": "application/json",
            "Content-Type": "application/json"}
        
        url = f"https://api.jwplayer.com/v2/sites/{self.SITE_ID}/media/{media_id}/text_tracks/"
        payload = {
            "upload": {
                "file_format": "vtt",
                "auto_publish": True,
                "method": "direct",
                "mime_type": "text/vtt"
            },
            "metadata": metadata
        }
        try:
            res = requests.post(url, json=payload, headers=HEADERS)
            
            if res.status_code == 201:
                self.response = res.json()
                print(res.json())
                print('text track successfully created')
                upload_url = self.response['upload_link']
                
                headers = {"Content-Type": "text/vtt"}
                
                with open(local_caption_path, 'rb') as f:
                    track_data = f.read()
                    r = requests.put(upload_url, headers=headers, data=track_data)
                    print(r)
                return True
            else:
                print(f"ERROR - Unable to create new text track for media id: {media_id}")
                return False
        except Exception as e:
            print(f"ERROR - Unable to create new text track for media id: {media_id}")
            print(str(e))
            return False


    def get_payload(self):
        return self.payload

    def get_response(self):
        return self.response
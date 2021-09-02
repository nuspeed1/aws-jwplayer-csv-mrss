import re
import hashlib
import random
import requests
import time
from urllib.parse import quote
from pprint import pprint

"""
This is a standalone thumbnail.  It creates a separate media asset and uploads an image to it.
It's an external asset and only used for image storage.  For a large library of media, its recommended
to deploy poster images to their own property so that it does not fill up the main media list.
"""
class PosterElement:
    def __init__(self, data, s3file):
        self.payload = data
        self.s3file = s3file
        self.response = {}
        self.limits = {"result_limit": 14, "result_offset": 0}
        self.thumb_endpoint = "videos/thumbnails/update"
        self.API_KEY = ""
        self.API_SECRET = ""

    def build_request(self, path, params = None):
        """Build API request."""

        _url = 'https://api.jwplatform.com/v1/{path}'.format(path=path)

        if params is not None:
            _params = params.copy()
        else:
            _params = dict()

        # Add required API parameters
        _params['api_nonce'] = str(random.randint(0, 999999999)).zfill(9)
        _params['api_timestamp'] = int(time.time())
        _params['api_key'] = self.API_KEY
        _params['api_format'] = 'json'

        # Collect params to a list
        # The reason using a list instead of a dict is
        # to allow the same key multiple times with the different values in the query string
        params_for_sbs = list()
        for key, value in sorted(_params.items()):
            # pprint(key)
            key = quote(str(key).encode('utf-8'), safe='~')
            if isinstance(value, list):
                for item in value:
                    item = quote(str(item).encode('utf-8'), safe='~')
                    params_for_sbs.append(f"{key}={item}")
            else:
                value = quote(str(value).encode('utf-8'), safe='~')
                params_for_sbs.append(f"{key}={value}")

        # Construct Signature Base String
        sbs = "&".join(params_for_sbs)
        print(">>",sbs)
        # Add signature to the _params dict
        _params['api_signature'] = hashlib.sha1(
            '{}{}'.format(sbs, self.API_SECRET).encode('utf-8')).hexdigest()

        return _url, _params

    def build_url(self, path, params, max_limit=False):
        if max_limit:
            params['result_limit'] = self.limits['result_limit']
            params['result_offset'] = self.limits['result_offset']

        url, params = self.build_request(path=path, params=params)
        url = "{}?api_format=json&api_key={}&api_nonce={}&api_timestamp={}".format(
            url,
            self.API_KEY,
            params["api_nonce"],
            params["api_timestamp"])

        return url, params["api_signature"]

    def post(self, url, data):
        try:
            r = requests.post(url, data=data)
            '''SAMPLE RESPONSE:
                {'link': {'address': 'upload.jwplatform.com',
                        'path': '/v1/videos/thumbnails/upload',
                        'protocol': 'http',
                        'query': {'key': '0DZLxpac',
                                    'token': '4b8f88adf169989bea2a2b96a6068b9467378d8f3fd'}},
                'media': {'key': '0DZLxpac', 'type': 'thumbnail'},
                'rate_limit': {'limit': 60, 'remaining': 59, 'reset': 1622674080},
                'status': 'ok'}
            '''
            return r.json()
        except Exception as e:
            print("error calling url: {}".format(url), e.__class__, "occurred")
            pprint(e)

    def update_thumbnail(self, result, thumb_path):
        try:
            response = result["link"] 
            pprint(result["link"])
            upload_url = response['protocol'] + '://' + response['address'] + response['path'] + '?api_format=py&key=' + response['query']['key'] + '&token=' + response['query']['token']

            print(upload_url)

            up_file = {'file': open(thumb_path, 'rb')}

            result = requests.post(upload_url, files=up_file)

            pprint(result)
        except Exception as e:
            print("error updating thumbnail", e.__class__, "occurred")
            pprint(e)

    def upload(self):
        url, sig = self.build_url(self.thumb_endpoint, self.payload)
        url = "{}&api_signature={}".format(url, sig)
        print(">>",url)

        ## Initial call for upload token
        result = self.post(url, self.data)
        ## Actual call to upload thumbnail image
        self.update_thumbnail(result, self.thumbnail_path)

    def get_payload(self):
        return self.payload

    def get_response(self):
        return self.response
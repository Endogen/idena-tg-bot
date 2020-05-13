import time
import json
import base64
import logging
import requests
import requests.auth

from hashlib import sha256
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class QtradeAuth(requests.auth.AuthBase):

    def __init__(self, key):
        self.key_id, self.key = key.split(":")

    def __call__(self, req):
        timestamp = str(int(time.time()))
        url_obj = urlparse(req.url)

        request_details = req.method + "\n"

        uri = url_obj.path

        if url_obj.query:
            uri += "?" + url_obj.query

        request_details += uri + "\n"
        request_details += timestamp + "\n"

        if req.body:
            if isinstance(req.body, str):
                request_details += req.body + "\n"
            else:
                request_details += req.body.decode('utf8') + "\n"
        else:
            request_details += "\n"

        request_details += self.key
        hsh = sha256(request_details.encode("utf8")).digest()
        signature = base64.b64encode(hsh)

        req.headers.update({
            "Authorization": "HMAC-SHA256 {}:{}".format(self.key_id, signature.decode("utf8")),
            "HMAC-Timestamp": timestamp
        })

        return req


class QtradeAPI:
    __API_URL_BASE = "https://api.qtrade.io/v1/"
    __REQ_TIMEOUT = 20

    def __init__(self, auth: QtradeAuth, api_base_url=__API_URL_BASE, timeout=__REQ_TIMEOUT):
        self.api_base_url = api_base_url
        self.request_timeout = timeout

        self.session = requests.Session()
        self.session.auth = auth

        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def __request(self, url):
        logging.info(f"qTrade API Request: {url}")

        try:
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()

            return json.loads(response.content.decode('utf-8'))
        except Exception as e:
            logging.error(e)

    def __api_url_params(self, api_url, params):
        if params:
            api_url += '?'
            for key, value in params.items():
                api_url += f"{key}={value}&"
            api_url = api_url[:-1]
        return api_url

    def get_ticker(self, market):
        api_url = f"{self.__API_URL_BASE}ticker/{market}"
        return self.__request(api_url)

    def get_historical_ohlc(self, market, interval):
        api_url = f"{self.__API_URL_BASE}market/{market}/ohlcv/{interval}"
        return self.__request(api_url)

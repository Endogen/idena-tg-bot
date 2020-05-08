import json
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class CoinPaprikaAPI:
    __API_URL_BASE = 'https://api.coinpaprika.com/v1/'
    __REQ_TIMEOUT = 30

    def __init__(self, api_base_url=__API_URL_BASE, timeout=__REQ_TIMEOUT):
        self.api_base_url = api_base_url
        self.request_timeout = timeout

        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def __request(self, url):
        response = None

        try:
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()
            content = json.loads(response.content.decode('utf-8'))
            return content
        except Exception as e:
            try:
                # check if json (with error message) is returned
                content = json.loads(response.content.decode('utf-8'))
                raise ValueError(content)
            except json.decoder.JSONDecodeError:
                # no json
                pass
            raise

    def __api_url_params(self, api_url, params):
        if params:
            api_url += '?'
            for key, value in params.items():
                api_url += f"{key}={value}&"
            api_url = api_url[:-1]
        return api_url

    def get_ticker(self, coin_id, **kwargs):
        api_url = f"{self.__API_URL_BASE}tickers/{coin_id}"
        api_url = self.__api_url_params(api_url, kwargs)
        return self.__request(api_url)

    def get_historical_ohlc(self, coin_id, **kwargs):
        api_url = f"{self.__API_URL_BASE}coins/{coin_id}/ohlcv/historical"
        api_url = self.__api_url_params(api_url, kwargs)
        return self.__request(api_url)

    def get_historical_tickers(self, coin_id, **kwargs):
        api_url = f"{self.__API_URL_BASE}tickers/{coin_id}/historical"
        api_url = self.__api_url_params(api_url, kwargs)
        return self.__request(api_url)

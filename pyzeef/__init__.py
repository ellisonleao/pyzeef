# -*- coding: utf-8 -*-
import requests

__author__ = 'Ellison Leão'
__email__ = 'ellisonleao@gmail.com'
__version__ = '0.1.0'


class Zeef(object):
    API_URL = 'https://zeef.io/api'

    def __init__(self, token):
        self.token = token
        self.pages = []
        self.auth_url = '{}/pages/mine'.format(self.API_URL)
        self.pages_url = '{}/page'.format(self.API_URL)
        self.authorize()

    def authorize(self, token=None):
        """
        Return the authorization response
        """
        token = token or self.token
        headers = {'Authorization': 'OmniLogin auth={}'.format(token)}
        response = requests.get(self.auth_url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            pages = content['pageOverviews']
            for page in pages:
                # retrieve page details and persist it
                page_detail = '{}/{}'.format(self.pages_url, page['id'])
                r = requests.get(page_detail)
                if r.status_code == 200:
                    self.pages.append(r.json())
        elif response.status_code in (400, 404):
            # TODO: show error messages
            pass

    def get_block(self, id):
        pass

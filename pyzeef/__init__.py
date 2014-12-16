# -*- coding: utf-8 -*-
import requests

__author__ = 'Ellison Leão'
__email__ = 'ellisonleao@gmail.com'
__version__ = '0.1.0'


class Zeef(object):
    API_URL = 'https://zeef.io/api'

    def __init__(self, token, **kwargs):
        self.token = token
        self.pages = []
        self.auth_url = '{}/pages/mine'.format(self.API_URL)
        self.pages_url = '{}/page'.format(self.API_URL)
        self.auth_header = {'Authorization': 'OmniLogin auth={}'.format(token)}
        self.authorize(persist_pages=kwargs.get('persist_pages', False))

    def authorize(self, token=None, persist_pages=True):
        """
        Return the authorization response
        """
        token = token or self.token
        response = requests.get(self.auth_url, headers=self.auth_header)
        if response.status_code == 200:
            content = response.json()
            pages = content['pageOverviews']
            if persist_pages:
                for page in pages:
                    # retrieve page details and persist it
                    page_detail = '{}/{}'.format(self.pages_url, page['id'])
                    r = requests.get(page_detail, headers=self.auth_header)
                    if r.status_code == 200:
                        self.pages.append(r.json())
            else:
                self.pages = pages
        elif response.status_code in (400, 404):
            # TODO: show error messages
            pass

    # PAGES
    def get_page(self, page_id):
        if not type(page_id) == int:
            raise TypeError('page_id should be an int')

        # first try to get from self.pages, then if no pages is found
        # try with the api
        if not self.pages:
            page = '{}/{}'.format(self.pages_url, page_id)
            r = requests.get(page, headers=self.auth_header)
            if r.status_code == 200:
                return r.json()
            else:
                # TODO: Error handling!
                pass
        page_ids = [i['id'] for i in self.pages]
        if page_id in page_ids:
            return self.pages[page_ids.index(page_id)]

    def update_page(self, page_id, data):
        pass

    def delete_page(self, page_id):
        pass

    # BLOCKS
    def get_block(self, block_id):
        block_url = '{}/block/{}'.format(self.API_URL, block_id)
        response = requests.get(block_url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            # TODO: show no content message
            pass
        elif response.status_code == 400:
            # TODO: show wrong request message
            pass
        # TODO: Better error message handling
        return {'error': 'Not Found'}

    def update_block(self, block_id):
        block = self.get_block(block_id)
        return block

    def delete_block(self, block_id):
        pass

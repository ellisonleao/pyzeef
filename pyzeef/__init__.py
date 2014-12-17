# -*- coding: utf-8 -*-
import requests

__author__ = 'Ellison Leão'
__email__ = 'ellisonleao@gmail.com'
__version__ = '0.1.0'

__all__ = ['Zeef']


class Zeef(object):
    """
    Main ZEEF API Class
    """
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
                        self.pages.append(Page(self.token, r.json()))
            else:
                self.pages = pages
        elif response.status_code in (400, 404):
            # TODO: show error messages
            pass

    def get_page(self, page_id):
        if not type(page_id) == int:
            raise TypeError('page_id should be an int')

        page = '{}/{}'.format(self.pages_url, page_id)
        r = requests.get(page, headers=self.auth_header)
        if r.status_code == 200:
            return Page(self.token, r.json())
        else:
            # TODO: Error handling!
            pass


class Base(object):
    def __init__(self, token, data):
        self.token = token
        self.data = data

    def __repr__(self):
        raise NotImplementedError(':)')

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        raise AttributeError('{} does not contains the {} '
                             'attribute'.format(self.__class__, item))


class Page(Base):
    """
    Class to handle Page API requests
    """
    def __repr__(self):
        return '<Page {}>'.format(self.title)

    def __getattr__(self, item):
        # special cases
        if item == 'title':
            # get the default alias
            subject = self.data['subject']['alias']
            for i in subject:
                if i['defaultAlias']:
                    return i['displayName']

        if item == 'owner':
            return self.data['owner']['fullName']
        if item == 'blocks':
            # create the lists of blocks objects
            blocks = []
            for block in self.data['blocks']:
                blocks.append(Block(self.token, block))
            return blocks
        return super(Page, self).__getattr__(item)

    def update(self, data):
        # TODO:
        pass

    def delete_page(self):
        # TODO:
        pass

    def add_block(self, title, block_type='link'):
        # TODO:
        pass


class Block(Base):
    """
    Class to handle Block API requests
    """
    def __repr__(self):
        return '<Block {}>'.format(self.title)

    def __getattr__(self, item):
        # special cases
        if item == 'type':
            return self.data['@type']
        elif item == 'links':
            # return a lists of Link instances
            links = []
            for link in self.data['links']:
                links.append(Link(self.token, link))
            return links
        return super(Block, self).__getattr__(item)

    def update(self, data):
        # TODO:
        pass

    def delete(self):
        # TODO:
        pass


class Link(Base):
    """
    Class to handle Link API requests
    """
    def __repr__(self):
        return '<Link {}-{}>'.format(self.title or self.hostname, self.url)

    def update(self, data):
        # TODO:
        pass

    def delete(self):
        # TODO:
        pass

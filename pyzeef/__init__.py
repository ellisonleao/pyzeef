# -*- coding: utf-8 -*-
from StringIO import StringIO

from mako.template import Template
from mako.runtime import Context
import requests

__author__ = 'Ellison Leão'
__email__ = 'ellisonleao@gmail.com'
__version__ = '0.1.0'

__all__ = ['Zeef']


class Base(object):
    def __init__(self, token, **kwargs):
        self.token = token
        self.auth_header = {'Authorization': 'OmniLogin auth={}'.format(token)}
        self.data = kwargs.get('data', {})

    def __repr__(self):
        raise NotImplementedError(':)')

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        raise AttributeError('{} does not contains the {} '
                             'attribute'.format(self.__class__, item))

    def _response(self, response):
        try:
            content = response.json()
        except ValueError:
            content = response.content
        return {'status': response.status_code, 'content': content}


class Zeef(Base):
    """
    Main ZEEF API Class
    """
    API_URL = 'https://zeef.io/api'

    def __getattr__(self, item):
        return object.__getattribute__(self, item)

    def __init__(self, token, **kwargs):
        super(Zeef, self).__init__(token, **kwargs)
        self.pages = []
        self.auth_url = '{}/pages/mine'.format(self.API_URL)
        self.pages_url = '{}/page'.format(self.API_URL)
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
                        self.pages.append(Page(self.token, data=r.json()))
        return self._response(response)

    def get_page(self, page_id):
        if not type(page_id) == int:
            raise TypeError('page_id should be an int')

        page = '{}/{}'.format(Page.PAGE_URL, page_id)
        r = requests.get(page, headers=self.auth_header)
        if r.status_code == 200:
            return Page(self.token, data=r.json())
        else:
            return self._response(r)

    def get_block(self, block_id):
        if not type(block_id) == int:
            raise TypeError('page_id should be an int')

        block = '{}/{}'.format(Block.BLOCK_URL, block_id)
        r = requests.get(block, headers=self.auth_header)
        if r.status_code == 200:
            return Block(self.token, data=r.json())
        else:
            return self._response(r)

    def get_link(self, link_id):
        if not type(link_id) == int:
            raise TypeError('link_id should be an int')

        link_url = '{}/{}'.format(Link.LINK_URL, link_id)
        r = requests.get(link_url, headers=self.auth_header)
        if r.status_code == 200:
            return Link(self.token, data=r.json())
        else:
            return self._response(r)


class Page(Base):
    """
    Class to handle Page API requests
    """
    PAGE_URL = '{}/page'.format(Zeef.API_URL)

    def __repr__(self):
        return '<Page {}>'.format(self.id)

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
                blocks.append(Block(self.token, data=block))
            return blocks
        if item == 'description':
            if 'markdownDescription' in self.data:
                return self.data['markdownDescription']
            return ''
        return super(Page, self).__getattr__(item)

    def update(self, data):
        # TODO:
        pass

    def delete(self):
        # TODO:
        pass

    def to_markdown(self):
        template = Template(filename='pyzeef/markdown_template.md')
        buf = StringIO()
        context_dict = {'page': self}
        context = Context(buf, **context_dict)
        template.render_context(context)
        return buf.getvalue().encode('utf-8')


class Block(Base):
    """
    Class to handle Block API requests
    """
    BLOCK_URL = '{}/block'.format(Zeef.API_URL)

    def __repr__(self):
        return '<Block {}>'.format(self.id)

    def __getattr__(self, item):
        # special cases
        if item == 'type':
            t = self.data['@type']
            return t[0:t.find('Block')]
        elif item == 'links':
            # return a lists of Link instances
            links = []
            if self.type in ['link', 'feed', 'latestPages']:
                for link in self.data['links']:
                    links.append(Link(self.token, data=link))
            elif self.type == 'image':
                return self.data['imageURL']
            elif self.type == 'text':
                return self.data['htmlText']
            return links
        elif item == 'description':
            if self.type in ['link', 'feed']:
                return self.data['markdownDescription']
            return ''
        return super(Block, self).__getattr__(item)

    def update(self, data):
        params = {}
        keys = ['title', 'promoted', 'publicly_visible']
        for key in keys:
            if data.get(key, False):
                params[key] = data[key]

        if self.type == 'text' and data.get('markdown_text', False):
            params['markdownText'] = data['markdown_text']

        if self.type == 'link' and data.get('markdown_description', False):
            params['markdownDescription'] = data['markdown_description']

        url = '{}/{}'.format(self.BLOCK_URL, self.id)
        response = requests.post(url, data=data, headers=self.auth_header)
        if response.status_code == 200:
            for key, val in params.iteritems():
                setattr(self, key, val)

        return self._response(response)

    def delete(self):
        url = '{}/{}'.format(self.BLOCK_URL, self.id)
        response = requests.delete(url, headers=self.auth_header)
        return self._response(response)


class Link(Base):
    """
    Class to handle Link API requests
    """
    LINK_URL = '{}/link'.format(Zeef.API_URL)

    def __repr__(self):
        return u'<Link {}>'.format(self.url)

    def update(self, data):
        url = data.get('url', False)
        title = data.get('title', False)
        description = data.get('description', False)

        params = {}
        if url:
            params['url'] = url

        if title:
            params['title'] = title

        if description:
            params['description'] = description

        url = '{}/{}'.format(self.LINK_URL, self.id)
        response = requests.post(url, data=data, headers=self.auth_header)
        if response.status_code == 200:
            for key, val in response.json().iteritems():
                setattr(self, key, val)
        return self._response(response)

    def delete(self):
        url = '{}/{}'.format(self.LINK_URL, self.id)
        response = requests.delete(url, headers=self.auth_header)
        return self._response(response)

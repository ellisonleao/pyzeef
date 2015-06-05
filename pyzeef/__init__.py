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
    API_URL = 'https://zeef.io/api'

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

    def __repr__(self):
        return '<Zeef token={}>'.format(self.token)

    def __getattr__(self, item):
        return object.__getattribute__(self, item)

    def __init__(self, token, **kwargs):
        super(Zeef, self).__init__(token, **kwargs)
        self.pages = []
        self.auth_url = '{}/pages/mine'.format(self.API_URL)
        self.pages_url = '{}/page'.format(self.API_URL)
        self.authorize(persist_pages=kwargs.get('persist_pages', False))
        # fetch scratchpad
        self.scratchpad = None
        if kwargs.get('get_scratchpad', True):
            response = requests.get(Scratchpad.SCRATCHPAD_URL,
                                    headers=self.auth_header)
            if response.status_code == 200:
                self.scratchpad = Scratchpad(self.token, data=response.json())

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

    def get_page(self, **kwargs):
        page_id = kwargs.get('page_id')
        alias = kwargs.get('alias')
        username = kwargs.get('username')
        # validation
        if not any([page_id, alias, username]):
            raise TypeError('You should pass a page_id or an alias and '
                            'username in order to get a page info')
        if alias and username:
            url = '{}/{}/{}'.format(Page.PAGE_URL, alias, username)
        if page_id:
            # get page by id takes precedence
            url = '{}/{}'.format(Page.PAGE_URL, page_id)
        r = requests.get(url, headers=self.auth_header)
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

    def create_page(self, name, language='en', page_type='SUBJECT'):
        page_type = page_type.upper()
        if page_type not in Page.PAGE_TYPES:
            raise ValueError('page_type should be SUBJECT, COMPANY or '
                             'PERSONAL')
        url = '{}/create'.format(Page.PAGE_URL)
        data = {
            'displayName': name,
            'languageCode': language,
            'type': page_type,
        }
        r = requests.post(url, data, headers=self.auth_header)
        if r.status_code == 200:
            return Page(self.token, data=r.json())
        return self._response(r)


class Page(Base):
    """
    Class to handle Page API requests
    """
    PAGE_URL = '{}/page'.format(Base.API_URL)
    PAGE_TYPES = ['SUBJECT', 'PERSONAL', 'COMPANY']

    def __repr__(self):
        return '<Page {}>'.format(self.id)

    def __getattr__(self, item):
        # special cases
        if item == 'title':
            # get the default alias
            subject = self.data['subject']['aliases']
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

        if item == 'type':
            if 'pageType' in self.data:
                return self.data['pageType']

        return super(Page, self).__getattr__(item)

    def update(self, **kwargs):
        if not self.id:
            return

        page_type = kwargs.get('type')
        if page_type not in ['SUBJECT', 'COMPANY']:
            raise ValueError('type must be SUBJECT or COMPANY')

        description = kwargs.get('description')
        data = {}
        if page_type:
            data['type'] = page_type
        if description:
            data['markdownDescription'] = description

        if data:
            url = '{}/{}'.format(self.PAGE_URL, self.id)
            r = requests.post(url, data, headers=self.auth_header)
            if r.status_code == 200:
                content = r.json()
                if description:
                    self.data['markdownDescription'] = content['markdownDescription'] # flake8: noqa
                if page_type:
                    self.data['pageType'] = content['pageType']
            return self._response(r)

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
    BLOCK_URL = '{}/block'.format(Base.API_URL)

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
    LINK_URL = '{}/link'.format(Base.API_URL)

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


class Scratchpad(Base):
    SCRATCHPAD_URL = '{}/scratchPad/mine/'.format(Base.API_URL)

    def __repr__(self):
        return u'<Scratchpad {}>'.format(self.id)

    def __getattr__(self, item):
        if item == 'links':
            return self.data['scratchPadLinks']
        return super(Scratchpad, self).__getattr__(item)

    def add_link(self, url):
        api_url = '{}addLink'.format(self.SCRATCHPAD_URL)
        response = requests.post(api_url, data={'url': url},
                                 headers=self.auth_header)
        if response.status_code == 200:
            # update links array
            data = response.json()
            self.data['scratchPadLinks'] = data['scratchPadLinks']
        return self._response(response)

    def delete_link(self, link_id):
        url = '{}/scratchPadLink/{}'.format(self.API_URL, link_id)
        response = requests.delete(url, headers=self.auth_header)
        if response.status_code == 204:
            # remove link from array data
            links = [i for i in self.links if i['id'] != int(link_id)]
            self.data['scratchPadLinks'] = links
        return self._response(response)

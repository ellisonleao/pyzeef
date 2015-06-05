#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import json

import responses
from pyzeef import Zeef, Block, Page, Scratchpad


class TestZeef(unittest.TestCase):

    def setUp(self):
        self.auth_url = '{}/pages/mine'.format(Zeef.API_URL)
        self.pages_url = Page.PAGE_URL
        self.block_url = Block.BLOCK_URL

    def _scratchpad_mock(self):
        # scratchpad response mock
        body = """
        {
          "id": 0,
          "owner": "APIUser",
          "scratchPadLinks": [
            {
              "id": 0,
              "scratchPadId": 0,
              "title": "string",
              "url": "string"
            }
          ]
        }
        """
        responses.add(responses.GET, url=Scratchpad.SCRATCHPAD_URL, body=body)

    def _pages_mine_mock(self):
        # /pages/mine
        body = ('{"pageOverviews":[{"id":1,"url":"https://test.'
                'zeef.com/user","subjectName":"test page",'
                '"curator":"user","languageCode":null,'
                '"status":"published","pageType":null,'
                '"imageUrl":"https://zeef.io/image/2635/100'
                '/s?1419350138591"}]}')
        responses.add(responses.GET, url=self.auth_url, status=200, body=body)

    def _blocks_mock(self):
        return [
            {
                "@type": "linkBlock",
                "id": 27430,
                "owningPageID": 5088,
                "publiclyVisible": True,
                "promoted": False,
                "title": "Block 1",
                "columnIndexHint": 0,
                "markdownDescription": "",
                "htmlDescription": "",
                "linkOrder": "CURATOR_RANKING",
                "links": []
            },
            {
                "@type": "linkBlock",
                "id": 27430,
                "owningPageID": 5088,
                "publiclyVisible": True,
                "promoted": False,
                "title": "Block 2",
                "columnIndexHint": 0,
                "markdownDescription": "",
                "htmlDescription": "",
                "linkOrder": "CURATOR_RANKING",
                "links": []
            },
        ]

    def _page_mock(self):
        # /page/id mock
        page_body = {
            'htmlDescription': u'Testing Description',
            'id': 1,
            'links': [],
            'markdownDescription': 'Testing Description',
            'owner': {'fullName': 'Test Owner', 'username': 'test.owner'},
            'pageType': 'SUBJECT',
            'plainTextDescription': 'Testing Description',
            'profile': {
                'facebookURL': 'http://facebook.com/testuser',
                'googlePlusURL': None,
                'htmlSummary': '',
                'id': 9999,
                'linkedinURL': 'http://linkedin.com/in/testuser',
                'markdownSummary': '',
                'profileImageURL': 'https://zeef.io/image/2439/100/s?123456',
                'twentyFourSessionsURL': None,
                'twitterURL': 'http://twitter.com/testuser'
            },
            'subject': {
                'aliases': [
                    {
                        'defaultAlias': True,
                        'displayName': 'Test Page',
                        'id': 3833,
                        'name': 'test-page'
                    }
                ],
                'id': 777
            },
            'blocks': self._blocks_mock()
        }
        _id = page_body['id']
        page_body = json.dumps(page_body)
        url = '{}/{}'.format(self.pages_url, _id)
        responses.add(responses.GET, url=url, body=page_body, status=200)

    def test_repr(self):
        z = Zeef('token')
        self.assertEqual(repr(z), '<Zeef token={}>'.format(z.token))

    @responses.activate
    def test_zeef_authentication_good_token(self):
        self._pages_mine_mock()
        self._scratchpad_mock()

        zeef = Zeef('GoodToken')
        self.assertEqual(len(zeef.pages), 0)

    def test_zeef_authentication_bad_token(self):
        z = Zeef('badtoken')
        r = z.authorize(persist_pages=False)
        response = {'status': 404, 'content': '<html><head><title>Error'
                    '</title></head><body>Not Found</body>'
                    '</html>'}
        self.assertEqual(r, response)

    def test_zeef_class_attributes(self):
        z = Zeef('sometoken')
        self.assertEqual(z.auth_url, self.auth_url)
        self.assertEqual(z.pages_url, self.pages_url)
        self.assertEqual(z.token, 'sometoken')

    @responses.activate
    def test_get_basic_page(self):
        self._pages_mine_mock()
        self._scratchpad_mock()
        self._page_mock()

        z = Zeef('GoodToken', persist_pages=True)
        self.assertEqual(len(z.pages), 1)
        self.assertEqual(z.pages[0].__class__, Page)
        self.assertEqual(z.pages[0].title, 'Test Page')
        self.assertEqual(z.pages[0].description, 'Testing Description')
        self.assertEqual(z.pages[0].type, 'SUBJECT')

    @responses.activate
    def test_get_blocks(self):
        self._pages_mine_mock()
        self._scratchpad_mock()
        self._page_mock()

        z = Zeef('GoodToken', persist_pages=True)
        self.assertEqual(len(z.pages[0].blocks), 2)

    @responses.activate
    def test_page_to_markdown(self):
        self._pages_mine_mock()
        self._scratchpad_mock()
        self._page_mock()

        z = Zeef('GoodToken', persist_pages=True)
        page = z.pages[0]
        text = page.to_markdown()
        expected = """\nTest Page\n=========\n\n- [Block 1](#block-1)\n- [Block 2](#block-2)\n\nBlock 1\n-------\n\nBlock 2\n-------\n\n""" # flake8: noqa
        self.assertEqual(text, expected)

if __name__ == '__main__':
    unittest.main()

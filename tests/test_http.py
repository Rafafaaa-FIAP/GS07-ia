import json
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from app import Handler

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def test_page_and_assets(self):
        for path in ['/', '/chat.js','/style.css','/api/manual']:
            with urlopen(self.url+path) as r:
                self.assertEqual(r.status,200)
                self.assertIsNotNone(r.headers.get('Content-Security-Policy'))

    def test_chat_demo_roundtrip(self):
        with patch.dict('os.environ',{'APP_MODE':'demo'}):
            req=Request(self.url+'/api/chat',data=json.dumps({'message':'Como registrar iluminação?'}).encode(),headers={'Content-Type':'application/json'})
            with urlopen(req) as r:
                result=json.load(r)
                self.assertEqual(result['mode'],'demo')
                self.assertTrue(result['sources'])

    def test_invalid_body(self):
        with self.assertRaises(HTTPError) as cm:urlopen(Request(self.url+'/api/chat',data=b'{}'))
        self.assertEqual(cm.exception.code,400)

    def test_cross_origin_blocked(self):
        with self.assertRaises(HTTPError) as cm:urlopen(Request(self.url+'/api/chat',data=b'{}',headers={'Origin':'https://example.com'}))
        self.assertEqual(cm.exception.code,403)

    def test_secret_and_path_traversal_not_served(self):
        for path in ['/.env','/../assistant.py']:
            with self.subTest(path=path),self.assertRaises(HTTPError) as cm:urlopen(self.url+path)
            self.assertEqual(cm.exception.code,404)

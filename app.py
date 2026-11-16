"""Servidor local para avaliação acadêmica; não é servidor de produção."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from pydantic import ValidationError
from assistant import ROOT, MANUAL, ChatInput, ServiceError, load_env, respond, settings

class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(45)

    def log_message(self, *_):
        pass  # Não registrar mensagens, corpos, chaves ou endereços de usuários.

    def send(self, status, body, content_type='application/json; charset=utf-8'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/config':
            mode, model = settings()
            return self.send(200, {'mode':mode, 'model':model if mode == 'openrouter' else None})
        if path == '/api/manual':
            return self.send(200, MANUAL)
        assets = {'/':('index.html','text/html'), '/style.css':('style.css','text/css'), '/chat.js':('chat.js','text/javascript')}
        if path in assets:
            name, mime = assets[path]
            return self.send(200, (ROOT/'static'/name).read_bytes(), mime+'; charset=utf-8')
        self.send(404, {'error':{'code':'nao_encontrado','message':'Recurso não encontrado.'}})

    def do_POST(self):
        if self.path != '/api/chat':
            return self.send(404, {'error':{'message':'Recurso não encontrado.'}})
        # Bloqueia uso cross-origin em navegadores; não substitui autenticação pública.
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            return self.send(403, {'error':{'message':'Origem não permitida.'}})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 22000:
                raise ValueError()
            chat = ChatInput.model_validate_json(self.rfile.read(length))
        except (ValueError, ValidationError):
            return self.send(400, {'error':{'code':'entrada_invalida','message':'Pergunta ou histórico inválido. Use até 1.200 caracteres e seis mensagens anteriores.'}})
        try:
            self.send(200, respond(chat))
        except ServiceError as exc:
            self.send(exc.http_status, {'error':{'code':exc.code,'message':exc.message}})
        except Exception:
            self.send(500, {'error':{'code':'interno','message':'Ocorreu uma falha interna. Tente novamente.'}})

if __name__ == '__main__':
    load_env()
    settings()
    port = int(os.getenv('PORT', '8000'))
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'Bairro em Dia: http://127.0.0.1:{port} | modo: {settings()[0]}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

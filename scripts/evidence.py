"""Executa testes e salva evidências reais locais. Não faz chamadas pagas."""
import io
import json
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from assistant import ChatInput, respond

if __name__=='__main__':
    os.environ['APP_MODE']='demo'
    output=ROOT/'evidencias';output.mkdir(exist_ok=True)
    stream=io.StringIO()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    stamp=datetime.now(timezone.utc).isoformat()
    (output/'testes.txt').write_text('Execução UTC: '+stamp+'\n'+stream.getvalue(),encoding='utf-8')
    data={'executado_em_utc':stamp,'tipo':'Execução local em modo demo, sem chamada a LLM',
          'pergunta':'Como registrar um problema de iluminação?',
          'resultado':respond(ChatInput(message='Como registrar um problema de iluminação?'))}
    (output/'demo.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(stream.getvalue())
    sys.exit(0 if result.wasSuccessful() else 1)

"""Teste opt-in real: requer APP_MODE=openrouter e chave; pode consumir créditos."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from assistant import ChatInput, ServiceError, load_env, respond, settings

load_env()
if settings()[0]!='openrouter':
    sys.exit('Defina APP_MODE=openrouter no .env antes de executar o teste real.')
question='Há uma lâmpada apagada no poste ao lado da entrada da Praça Exemplo. Ajude a organizar meu relato, sem inventar detalhes.'
try:
    result=respond(ChatInput(message=question,task='relato'))
except ServiceError as exc:
    sys.exit(f'{exc.code}: {exc.message}')
output=ROOT/'evidencias';output.mkdir(exist_ok=True)
record={'executado_em_utc':datetime.now(timezone.utc).isoformat(),'tipo':'Chamada real à API OpenRouter; cenário sintético','task':'relato','pergunta':question,'resultado':result}
(output/'api-real.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('Resposta validada. Evidência salva em evidencias/api-real.json. Revise o conteúdo antes de publicar.')

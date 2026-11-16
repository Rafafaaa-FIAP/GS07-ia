# Resultados verificados

## Testes

O arquivo `testes.txt` registra 22 testes aprovados, incluindo validação de entrada, JSON, fontes, tarefas, modo local e requisições HTTP. Falhas do OpenRouter são simuladas por mocks, sem consumir API.

## Chamada real

Em 13/11/2026, `scripts/test_live.py` fez uma chamada real com `openai/gpt-4o-mini` via OpenRouter. O cenário fictício descreve uma lâmpada apagada na Praça Exemplo. A saída passou pela validação usada na aplicação e está em `api-real.json`.

Revisão da resposta registrada:

- Categoria `iluminacao` compatível com o problema.
- Título e descrição preservam o fato e a referência fornecidos.
- Nenhuma data, causa, promessa de reparo ou protocolo foi acrescentado.
- A lista de informações faltantes ficou vazia; isso não prova que um órgão específico aceitaria o relato sem detalhes adicionais.
- A resposta orienta revisão e cópia, sem afirmar que houve envio.

Esse caso comprova o fluxo técnico com IA real, não a precisão geral nem impacto com moradores.

## Interface

Uma instância local em modo demonstração foi aberta no navegador. Foram verificados preenchimento por sugestão, envio, rascunho e botão de cópia, com confirmação “Copiado!”. A captura `interface-demo.png` mostra esse estado. No modo demo, a categoria é `outro` e o texto original é preservado; a captura não representa geração por IA.

As evidências se complementam: JSON real para a integração com IA, log para os testes e captura para a interface. Os cenários não contêm dados reais de cidadãos.

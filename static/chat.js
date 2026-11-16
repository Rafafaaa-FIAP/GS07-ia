'use strict';
const $ = id => document.getElementById(id);
let history = [], busy = false;
function bubble(text, role, sources = [], steps = [], report = null) {
  const article = document.createElement('article'); article.className = `bubble ${role === 'user' ? 'user' : 'bot'}`;
  const speaker = document.createElement('span'); speaker.className = 'speaker'; speaker.textContent = role === 'user' ? 'VOCÊ' : 'ASSISTENTE';
  const paragraph = document.createElement('p'); paragraph.textContent = text; article.append(speaker, paragraph);
  if (steps.length) { const list = document.createElement('ol'); steps.forEach(s => { const li = document.createElement('li'); li.textContent = s; list.append(li); }); article.append(list); }
  if (report) {
    const draft = document.createElement('section'); draft.className = 'draft';
    const title = document.createElement('h3'); title.textContent = report.titulo;
    const category = document.createElement('p'); category.textContent = 'Categoria: ' + report.categoria;
    const description = document.createElement('p'); description.textContent = report.descricao;
    const missing = document.createElement('p'); missing.textContent = report.informacoes_faltantes.length ? 'Falta esclarecer: ' + report.informacoes_faltantes.join(' / ') : 'Revise os fatos antes de usar.';
    const copy = document.createElement('button'); copy.type = 'button'; copy.textContent = 'Copiar relato';
    copy.addEventListener('click', async () => {
      const content = report.titulo + '\nCategoria: ' + report.categoria + '\n\n' + report.descricao + '\n\nInformações a revisar: ' + report.informacoes_faltantes.join('; ');
      try { await navigator.clipboard.writeText(content); copy.textContent = 'Copiado!'; }
      catch { copy.textContent = 'Selecione e copie o texto acima'; }
    });
    draft.append(title, category, description, missing, copy); article.append(draft);
  }
  if (sources.length) { const source = document.createElement('div'); source.className = 'source'; source.textContent = 'Manual consultado: ' + sources.map(s => s.titulo).join(' · '); article.append(source); }
  $('messages').append(article); $('messages').scrollTop = $('messages').scrollHeight;
}
async function send(event) {
  event.preventDefault(); const text = $('pergunta').value.trim(); if (!text || busy) return;
  busy = true; $('send').disabled = true; $('clear').disabled = true; $('task').disabled = true; $('status').textContent = 'Preparando sua resposta…';
  bubble(text, 'user'); $('json').textContent = 'Aguardando resposta…';
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), 42000);
  try {
    const response = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:text,history,task:$('task').value}), signal:controller.signal});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error?.message || 'Não foi possível obter uma resposta.');
    bubble(result.answer.resposta, 'assistant', result.sources, result.answer.passos, result.answer.relato);
    history = [...history, {role:'user',content:text}, {role:'assistant',content:result.answer.resposta}].slice(-6);
    $('json').textContent = JSON.stringify(result, null, 2); $('pergunta').value = ''; $('count').textContent = '0 / 1200';
    $('status').textContent = result.mode === 'demo' ? 'Demonstração local: conteúdo sem geração por IA.' : 'Resposta gerada por IA. Confira as fontes do manual.';
  } catch (err) { $('status').textContent = err.name === 'AbortError' ? 'Tempo de espera excedido. Tente novamente.' : err.message; $('json').textContent = 'Falha: nenhuma resposta validada nesta tentativa.'; }
  finally {clearTimeout(timer);busy=false;$('send').disabled=false;$('clear').disabled=false;$('task').disabled=false;$('pergunta').focus();}
}
$('chat-form').addEventListener('submit',send);
$('task').addEventListener('change',()=>{history=[];});
$('pergunta').addEventListener('input',()=>{$('count').textContent=`${$('pergunta').value.length} / 1200`;});
document.querySelectorAll('.suggestions button').forEach(b=>b.addEventListener('click',()=>{if (!busy) { $('task').value = b.textContent.startsWith('Como') ? 'duvida' : 'relato'; history=[]; } $('pergunta').value=b.textContent;$('pergunta').dispatchEvent(new Event('input'));$('pergunta').focus();}));
$('clear').addEventListener('click',()=>{history=[];$('messages').replaceChildren();bubble('Conversa limpa. Como posso ajudar?', 'assistant');$('json').textContent='Envie uma pergunta para ver o resultado.';$('status').textContent='Histórico apagado.';});
async function init(){
  try{const config=await (await fetch('/api/config')).json();$('mode').textContent=config.mode==='demo'?'Demonstração local · sem IA':`Modo IA via OpenRouter · ${config.model}`;}catch{$('mode').textContent='Servidor indisponível';}
  try{const docs=await(await fetch('/api/manual')).json();$('manual-content').replaceChildren();for(const d of docs){const a=document.createElement('article'),h=document.createElement('h3'),p=document.createElement('p');h.textContent=d.titulo;p.textContent=d.texto;a.append(h,p);$('manual-content').append(a);}}catch{$('manual-content').textContent='Não foi possível carregar o manual. Verifique o servidor.';}
}init();

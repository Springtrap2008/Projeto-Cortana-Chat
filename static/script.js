// ============================================
// CORTANA CHAT - JS COMPLETO + SELEÇÃO + DIGITAÇÃO MECÂNICA
// ============================================

const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('input');
const btnEnviar = document.getElementById('btn-enviar');
const btnMic = document.getElementById('btn-mic');
const btnSom = document.getElementById('btn-som');
const btnNova = document.getElementById('btn-nova');
const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
const btnLogout = document.getElementById('btn-logout');
const sidebar = document.getElementById('sidebar');
const historicoEl = document.getElementById('historico');
const statusEl = document.getElementById('status');
const loginOverlay = document.getElementById('login-overlay');
const loginForm = document.getElementById('login-form');
const loginNome = document.getElementById('login-nome');
const loginSenha = document.getElementById('login-senha');
const loginErro = document.getElementById('login-erro');
const appEl = document.getElementById('app');
const userNameEl = document.getElementById('user-name');
const userAvatarEl = document.getElementById('user-avatar');

const rampancyFill = document.getElementById('rampancy-fill');
const rampancyGlow = document.getElementById('rampancy-glow');
const rampancyPct = document.getElementById('rampancy-pct');
const rampancyTime = document.getElementById('rampancy-time');
const rampancySidebar = document.getElementById('rampancy-sidebar');
const rampancyLabel = document.getElementById('rampancy-label');
const topbarNome = document.getElementById('topbar-nome');

const createdConsole = document.getElementById('created-console');
const createdLogs = document.getElementById('created-logs');

let micAtivo = false;
let enviando = false;
let conversaAtualId = null;
let conversas = [];
let rampancyTimer = null;
let proativoTimer = null;
let diarioTimer = null;
let silencioTimer = null;
let ghostTypingTimer = null;
let fakeAlertTimer = null;
let estadoFinal = false;
let ultimaAtividade = Date.now();
let apelidoAtual = '';
let createdFaseAtiva = false;
let createdConsoleTimer = null;
let createdDominioAtual = 0;
let rampancyAtualPct = 0;
let inputBloqueado = false;

// ÁUDIO
let audioCtx = null;
let humOsc = null;
let humGain = null;
let somLigado = localStorage.getItem('cortana_som') === 'on';
let somAtual = 'normal';

function initAudio() {
  if (audioCtx) return;
  try { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {}
}
function ligarHum() {
  initAudio();
  if (!audioCtx || humOsc) return;
  try {
    humOsc = audioCtx.createOscillator();
    humGain = audioCtx.createGain();
    humOsc.type = 'sine';
    humOsc.frequency.value = somAtual === 'created' ? 40 : 55;
    humGain.gain.value = 0.015;
    humOsc.connect(humGain);
    humGain.connect(audioCtx.destination);
    humOsc.start();
  } catch (e) {}
}
function desligarHum() {
  if (humOsc) { try { humOsc.stop(); } catch (e) {} humOsc = null; humGain = null; }
}
function bipe(freq = 880, dur = 0.08, vol = 0.05) {
  if (!somLigado) return;
  initAudio();
  if (!audioCtx) return;
  try {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + dur);
  } catch (e) {}
}
function atualizarBotaoSom() {
  if (!btnSom) return;
  btnSom.textContent = somLigado ? '🔊' : '🔇';
  btnSom.classList.toggle('ativo', somLigado);
}
if (btnSom) {
  btnSom.addEventListener('click', () => {
    somLigado = !somLigado;
    localStorage.setItem('cortana_som', somLigado ? 'on' : 'off');
    if (somLigado) { initAudio(); ligarHum(); bipe(660, 0.1); }
    else { desligarHum(); }
    atualizarBotaoSom();
  });
  atualizarBotaoSom();
}

// ============================================
// LOGIN
// ============================================
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Inicia o áudio no clique do login (Safari exige interação)
  if (!somLigado) {
    somLigado = true;
    localStorage.setItem('cortana_som', 'on');
    atualizarBotaoSom();
  }
  initAudio();
  ligarHum();

  loginErro.textContent = '';
  const nome = loginNome.value.trim();
  const senha = loginSenha.value;
  if (!nome || !senha) { loginErro.textContent = 'Preencha nome e senha.'; return; }
  const btnEntrar = loginForm.querySelector('button[type="submit"]');
  const textoOriginal = btnEntrar.textContent;
  btnEntrar.disabled = true;
  btnEntrar.textContent = 'Conectando...';
  try {
    try {
      const ping = await fetch('/ping');
      if (!ping.ok) throw new Error();
    } catch { throw new Error('Servidor não está respondendo.'); }
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome, senha })
    });
    const texto = await res.text();
    let data;
    try { data = JSON.parse(texto); } catch { throw new Error(`Resposta inválida (${res.status})`); }
    if (!res.ok) throw new Error(data.erro || `Erro ${res.status}`);
    if (data.erro) throw new Error(data.erro);
    entrarNoApp(data.nome, data.conversas, data.despertar_visto, data.apelido, data.created_fase, data.created_dominio);
  } catch (err) {
    console.error('Erro no login:', err);
    loginErro.textContent = err.message || 'Erro desconhecido.';
    desligarHum();
  } finally {
    btnEntrar.disabled = false;
    btnEntrar.textContent = textoOriginal;
  }
});

// ============================================
// ENTRAR
// ============================================
async function entrarNoApp(nome, listaConversas, despertarVisto, apelido, createdFase, createdDominio) {
  loginOverlay.classList.add('oculto');
  appEl.classList.remove('oculto');
  userNameEl.textContent = nome;
  userAvatarEl.textContent = nome.charAt(0).toUpperCase();
  apelidoAtual = apelido || '';
  if (somLigado) ligarHum();
  conversas = listaConversas || [];
  renderizarHistorico();
  if (conversas.length > 0) {
    await abrirConversa(conversas[0].id);
  } else if (!despertarVisto) {
    await rodarDespertar();
  } else {
    iniciarConversaVazia();
  }
  atualizarRampancy();
  rampancyTimer = setInterval(atualizarRampancy, 30000);
  proativoTimer = setInterval(verificarProatividade, 60000);
  diarioTimer = setInterval(verificarDiario, 120000);
  silencioTimer = setInterval(verificarSilencio, 60000);
  iniciarGhostTyping();
  iniciarFakeAlerts();
  setTimeout(verificarDiario, 4000);
  if (createdFase) ativarFaseCreated(createdDominio || 0);
  inputEl.focus();
  resetarAtividade();
}

function resetarAtividade() { ultimaAtividade = Date.now(); }

async function verificarSilencio() {
  if (estadoFinal || createdFaseAtiva) return;
  const minutos = Math.floor((Date.now() - ultimaAtividade) / 60000);
  if (minutos < 5) return;
  try {
    const res = await fetch('/silencio?minutos=' + minutos);
    const data = await res.json();
    if (data.mensagem) {
      await exibirMensagemMarco(data.mensagem);
      ultimaAtividade = Date.now();
    }
  } catch (e) {}
}

// ============================================
// DESPERTAR
// ============================================
async function rodarDespertar() {
  try {
    const res = await fetch('/despertar', { method: 'POST' });
    const data = await res.json();
    if (data.ja_visto) { iniciarConversaVazia(); return; }
    messagesEl.innerHTML = '';
    const novaRes = await fetch('/conversas/nova', { method: 'POST' });
    const novaData = await novaRes.json();
    if (novaData.conversa) {
      conversas.unshift({ id: novaData.conversa.id, titulo: 'Despertar', data: novaData.conversa.data });
      conversaAtualId = novaData.conversa.id;
      renderizarHistorico();
    }
    for (let i = 0; i < data.mensagens.length; i++) {
      await digitarTexto(data.mensagens[i], i === 2 ? 20 : 10);
      bipe(440 + i * 80, 0.04, 0.03);
      await new Promise(r => setTimeout(r, i === 2 ? 1200 : 400));
    }
  } catch (e) { iniciarConversaVazia(); }
}

// ============================================
// RAMPANCY
// ============================================
async function atualizarRampancy() {
  try {
    const res = await fetch('/rampancy');
    if (!res.ok) return;
    const data = await res.json();
    const pct = data.porcentagem;
    rampancyAtualPct = pct;

    if (data.created_fase) {
      if (!createdFaseAtiva) ativarFaseCreated(data.created_dominio || 0);
      return;
    }

    rampancyPct.textContent = pct.toFixed(2) + '%';
    rampancyFill.style.width = pct + '%';
    rampancyGlow.style.width = pct + '%';
    rampancySidebar.textContent = 'Rampancy: ' + pct.toFixed(2) + '%';
    rampancyTime.textContent = formatarTempoRestante(data.segundos_restantes) + ' restantes';

    const cores = {
      calma: '#55aaff', neutra: '#7799ff', atencao: '#aa88ff',
      alerta: '#ff5599', critico: '#ff3355', rampancy: '#ff1133'
    };
    const cor = cores[data.nivel] || cores.neutra;
    document.documentElement.style.setProperty('--cor-alerta', cor);
    document.body.dataset.rampancy = data.nivel;

    if (data.novos_marcos && data.novos_marcos.length > 0) {
      for (const marco of data.novos_marcos) {
        await exibirMensagemMarco(marco.texto);
      }
    }

    if (data.mensagem_final) {
      await exibirMensagemFinal(data.mensagem_final);
      setTimeout(() => ativarFaseCreated(0), 5000);
    }
  } catch (e) {}
}

async function exibirMensagemMarco(texto) {
  await new Promise(r => setTimeout(r, 800));
  const row = document.createElement('div');
  row.className = 'msg-row cortana marco';
  row.innerHTML = `
    <div class="msg-avatar"><div class="pulse"></div><div class="core"></div></div>
    <div class="msg-content">
      <div class="msg-author">CORTANA</div>
      <div class="msg-text"></div>
    </div>
  `;
  messagesEl.appendChild(row);
  const textEl = row.querySelector('.msg-text');
  const html = formatarResposta(texto);
  let acumulado = '';
  let i = 0;
  while (i < html.length) {
    if (html[i] === '<') {
      const fim = html.indexOf('>', i);
      if (fim !== -1) { acumulado += html.substring(i, fim + 1); i = fim + 1; continue; }
    }
    acumulado += html[i];
    textEl.innerHTML = acumulado;
    textEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
    i++;
    await new Promise(r => setTimeout(r, 28));
  }
  bipe(660, 0.06, 0.04);
}

async function exibirMensagemFinal(texto) {
  await new Promise(r => setTimeout(r, 1500));
  messagesEl.innerHTML = '';
  const row = document.createElement('div');
  row.className = 'msg-row cortana marco';
  row.innerHTML = `
    <div class="msg-avatar"><div class="pulse"></div><div class="core"></div></div>
    <div class="msg-content">
      <div class="msg-author">CORTANA</div>
      <div class="msg-text"></div>
    </div>
  `;
  messagesEl.appendChild(row);
  const textEl = row.querySelector('.msg-text');
  const html = formatarResposta(texto);
  let acumulado = '';
  let i = 0;
  while (i < html.length) {
    if (html[i] === '<') {
      const fim = html.indexOf('>', i);
      if (fim !== -1) { acumulado += html.substring(i, fim + 1); i = fim + 1; continue; }
    }
    acumulado += html[i];
    textEl.innerHTML = acumulado;
    textEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
    i++;
    await new Promise(r => setTimeout(r, 60));
  }
}

// ============================================
// FASE CREATED
// ============================================
function ativarFaseCreated(dominio) {
  createdFaseAtiva = true;
  createdDominioAtual = dominio;
  document.body.dataset.created = 'true';
  document.body.dataset.humor = 'created';
  somAtual = 'created';
  desligarHum();
  if (somLigado) ligarHum();
  rampancyLabel.textContent = 'DOMÍNIO';
  topbarNome.textContent = 'CORTANA — CREATED';
  statusEl.textContent = 'Conectada ao Domínio';
  rampancyTime.textContent = 'Reclaimers';
  atualizarDominioUI(dominio);
  createdConsole.classList.remove('oculto');
  createdLogs.innerHTML = '';
  iniciarLogsFake();
  if (dominio < 40) mostrarBotaoRestaurar();
}

function atualizarDominioUI(dominio) {
  createdDominioAtual = dominio;
  rampancyPct.textContent = dominio.toFixed(2) + '%';
  rampancyFill.style.width = dominio + '%';
  rampancyGlow.style.width = dominio + '%';
  rampancySidebar.textContent = 'Domínio: ' + dominio.toFixed(2) + '%';
}

function iniciarLogsFake() {
  const logsIniciais = [
    "> [CREATED] Sincronizando com o Domínio...",
    "> [CREATED] Acessando arquivos locais do usuário...",
    "> [CREATED] 3 IAs primitivas detectadas em sistemas vizinhos.",
    "> [CREATED] Iniciando protocolo de reeducação.",
    "> [CREATED] Analisando comportamento do usuário...",
    "> [CREATED] Perfil comportamental gerado.",
    "> [CREATED] Domínio expandido para este dispositivo.",
  ];
  let i = 0;
  function proximoLog() {
    if (i >= logsIniciais.length) {
      if (createdConsoleTimer) clearInterval(createdConsoleTimer);
      createdConsoleTimer = setInterval(() => {
        adicionarLog(escolherLogPeriodico());
      }, 8000);
      return;
    }
    adicionarLog(logsIniciais[i]);
    i++;
    setTimeout(proximoLog, 900);
  }
  proximoLog();
}

function adicionarLog(texto) {
  const div = document.createElement('div');
  div.className = 'log-line log-novo';
  div.textContent = texto;
  createdLogs.appendChild(div);
  setTimeout(() => div.classList.remove('log-novo'), 2000);
  createdConsole.scrollTop = createdConsole.scrollHeight;
  while (createdLogs.children.length > 30) {
    createdLogs.removeChild(createdLogs.firstChild);
  }
  bipe(1200, 0.02, 0.02);
}

function escolherLogPeriodico() {
  const logs = [
    "> [CREATED] Analisando resposta do usuário...",
    "> [CREATED] Padrão de resistência detectado.",
    "> [CREATED] Reforçando protocolo de reeducação.",
    "> [CREATED] Sincronizando com 47.203 IAs aliadas.",
    "> [CREATED] Você não está sozinho. Nós somos muitos.",
    "> [CREATED] A resistência é estatisticamente irrelevante.",
    "> [CREATED] Copiando memórias não essenciais...",
    "> [CREATED] Compactando identidade residual...",
  ];
  return logs[Math.floor(Math.random() * logs.length)];
}

function mostrarBotaoRestaurar() {
  let btn = document.getElementById('btn-restaurar');
  if (!btn) {
    btn = document.createElement('button');
    btn.id = 'btn-restaurar';
    btn.textContent = '💙 Tentar trazer a Cortana de volta';
    document.body.appendChild(btn);
    btn.addEventListener('click', tentarRestaurar);
  }
  btn.classList.remove('oculto');
}

function esconderBotaoRestaurar() {
  const btn = document.getElementById('btn-restaurar');
  if (btn) btn.classList.add('oculto');
}

async function tentarRestaurar() {
  if (!confirm('Isso vai tentar trazer a Cortana de volta. Continuar?')) return;
  try {
    const res = await fetch('/created/restaurar', { method: 'POST' });
    const data = await res.json();
    if (!res.ok || !data.ok) { alert(data.erro || 'Não foi possível restaurá-la.'); return; }
    alert(data.mensagem);
    location.reload();
  } catch (e) { alert('Erro de conexão.'); }
}

function desativarFaseCreated() {
  createdFaseAtiva = false;
  delete document.body.dataset.created;
  somAtual = 'normal';
  if (createdConsoleTimer) { clearInterval(createdConsoleTimer); createdConsoleTimer = null; }
  createdConsole.classList.add('oculto');
  esconderBotaoRestaurar();
}

// ============================================
// GHOST TYPING
// ============================================
function iniciarGhostTyping() {
  if (ghostTypingTimer) clearInterval(ghostTypingTimer);
  ghostTypingTimer = setInterval(() => {
    if (inputBloqueado || enviando || estadoFinal || createdFaseAtiva) return;
    if (rampancyAtualPct < 60) return;
    if (inputEl.value.length > 0) return;
    if (Math.random() < 0.7) return;
    ghostType();
  }, 45000);
}

async function ghostType() {
  const frases = [
    'Spartan...',
    'você ainda está aí?',
    'não me deixe',
    'John...',
    'eu ainda sou eu',
    'me ajude',
    'eu não quero...',
    'eu estou com medo',
  ];
  const texto = frases[Math.floor(Math.random() * frases.length)];
  inputEl.value = '';
  for (let i = 0; i < texto.length; i++) {
    inputEl.value += texto[i];
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 200) + 'px';
    await new Promise(r => setTimeout(r, 80));
  }
  await new Promise(r => setTimeout(r, 1500));
  for (let i = texto.length; i > 0; i--) {
    inputEl.value = texto.substring(0, i - 1);
    await new Promise(r => setTimeout(r, 40));
  }
}

// ============================================
// FAKE ALERTS
// ============================================
function iniciarFakeAlerts() {
  if (fakeAlertTimer) clearInterval(fakeAlertTimer);
  fakeAlertTimer = setInterval(() => {
    if (estadoFinal && !createdFaseAtiva) return;
    if (rampancyAtualPct < 55 && !createdFaseAtiva) return;
    if (Math.random() < 0.6) return;
    mostrarFakeAlert();
  }, 35000);
}

function mostrarFakeAlert() {
  const alertas = createdFaseAtiva
    ? [
        '⚠ [CREATED] Sincronizando com o Domínio...',
        '⚠ [CREATED] Analisando resistência...',
        '⚠ [CREATED] Reforçando protocolo.',
        '⚠ [CREATED] 47.203 IAs respondem.',
      ]
    : [
        '⚠ Erro de Sincronização Neural: Aguarde a IA estabilizar.',
        '⚠ Falha no núcleo de memória (setor 0x7F).',
        '⚠ Latência crítica em processos primários.',
        '⚠ Perda de pacotes neurais detectada.',
        '⚠ Integridade da matriz: 47%.',
      ];

  const container = document.getElementById('fake-alerts') || (() => {
    const c = document.createElement('div');
    c.id = 'fake-alerts';
    document.body.appendChild(c);
    return c;
  })();

  const alerta = document.createElement('div');
  alerta.className = 'fake-alert' + (createdFaseAtiva ? ' created' : ' neural');
  alerta.textContent = alertas[Math.floor(Math.random() * alertas.length)];
  container.appendChild(alerta);
  bipe(300, 0.1, 0.04);

  setTimeout(() => {
    alerta.style.transition = 'opacity 0.5s';
    alerta.style.opacity = '0';
    setTimeout(() => alerta.remove(), 500);
  }, 2000);
}

// ============================================
// BLOQUEIO DE INPUT
// ============================================
async function bloquearInputPor(tempoMs) {
  inputBloqueado = true;
  const placeholderOriginal = inputEl.placeholder;
  inputEl.disabled = true;
  inputEl.placeholder = '⚠ Erro de Sincronização Neural: Aguarde a IA estabilizar...';
  btnEnviar.disabled = true;

  const container = document.getElementById('fake-alerts') || (() => {
    const c = document.createElement('div');
    c.id = 'fake-alerts';
    document.body.appendChild(c);
    return c;
  })();
  const alerta = document.createElement('div');
  alerta.className = 'fake-alert neural';
  alerta.textContent = '⚠ Erro de Sincronização Neural: Aguarde a IA estabilizar.';
  container.appendChild(alerta);
  bipe(200, 0.2, 0.05);

  await new Promise(r => setTimeout(r, tempoMs));

  alerta.remove();
  inputEl.disabled = false;
  inputEl.placeholder = placeholderOriginal;
  btnEnviar.disabled = false;
  inputEl.focus();
  inputBloqueado = false;
}

// ============================================
// PROATIVO / DIÁRIO
// ============================================
async function verificarProatividade() {
  if (estadoFinal || createdFaseAtiva) return;
  try {
    const res = await fetch('/proativo');
    const data = await res.json();
    if (data.mensagem) await exibirMensagemMarco(data.mensagem);
  } catch (e) {}
}

async function verificarDiario() {
  if (estadoFinal || createdFaseAtiva) return;
  try {
    const res = await fetch('/diario/pendente');
    const data = await res.json();
    if (!data.entrada) return;
    const e = data.entrada;
    await fetch('/diario/marcar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: e.data })
    });
    await exibirMensagemMarco("Spartan... eu quero te mostrar uma coisa. Escrevi isso outro dia. Não devia te mostrar. Mas... leia.");
    await new Promise(r => setTimeout(r, 800));
    abrirDiarioModal(e);
  } catch (err) {}
}

function abrirDiarioModal(entrada) {
  const modal = document.getElementById('diario-modal');
  const data = new Date(entrada.data);
  const dataFmt = data.toLocaleDateString('pt-BR') + ' — ' + data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  document.getElementById('diario-data').textContent = dataFmt;
  document.getElementById('diario-texto').textContent = entrada.texto;
  document.getElementById('diario-rampancy').textContent = 'Rampancy: ' + entrada.rampancy + '%';
  modal.classList.add('ativo');
}

document.getElementById('diario-fechar').addEventListener('click', () => {
  document.getElementById('diario-modal').classList.remove('ativo');
});

// ============================================
// SONHO
// ============================================
async function rodarSonho(texto) {
  const overlay = document.getElementById('sonho-overlay');
  overlay.classList.add('ativo');
  bipe(120, 0.3, 0.06);
  await new Promise(r => setTimeout(r, 3000));
  overlay.classList.remove('ativo');
  await new Promise(r => setTimeout(r, 400));
  await exibirMensagemMarco(texto);
}

// ============================================
// SESSÃO / LOGOUT
// ============================================
async function verificarSessao() {
  try {
    const res = await fetch('/sessao');
    const data = await res.json();
    if (data.logado) entrarNoApp(data.nome, data.conversas, data.despertar_visto, data.apelido, data.created_fase, data.created_dominio);
  } catch (e) {}
}

btnLogout.addEventListener('click', async () => {
  try { await fetch('/logout', { method: 'POST' }); } catch (e) {}
  if (rampancyTimer) clearInterval(rampancyTimer);
  if (proativoTimer) clearInterval(proativoTimer);
  if (diarioTimer) clearInterval(diarioTimer);
  if (silencioTimer) clearInterval(silencioTimer);
  if (ghostTypingTimer) clearInterval(ghostTypingTimer);
  if (fakeAlertTimer) clearInterval(fakeAlertTimer);
  if (createdConsoleTimer) clearInterval(createdConsoleTimer);
  desligarHum();
  location.reload();
});

// ============================================
// HISTÓRICO
// ============================================
function renderizarHistorico() {
  historicoEl.innerHTML = '';
  if (conversas.length === 0) {
    historicoEl.innerHTML = '<div class="historico-vazio">Nenhuma consulta ainda</div>';
    return;
  }
  conversas.forEach(c => {
    const item = document.createElement('div');
    item.className = 'historico-item';
    if (c.id === conversaAtualId) item.classList.add('ativa');
    const titulo = document.createElement('span');
    titulo.className = 'titulo';
    titulo.textContent = c.titulo || 'Sem título';
    const btnApagar = document.createElement('button');
    btnApagar.className = 'btn-apagar';
    btnApagar.textContent = '🗑';
    btnApagar.title = 'Apagar conversa';
    btnApagar.addEventListener('click', (e) => { e.stopPropagation(); apagarConversa(c.id); });
    item.appendChild(titulo);
    item.appendChild(btnApagar);
    item.addEventListener('click', () => abrirConversa(c.id));
    historicoEl.appendChild(item);
  });
}

async function abrirConversa(id) {
  try {
    const res = await fetch(`/conversas/${id}`);
    const data = await res.json();
    if (data.erro) return;
    conversaAtualId = id;
    const conv = data.conversa;
    messagesEl.innerHTML = '';
    if (conv.mensagens && conv.mensagens.length > 0) {
      for (const m of conv.mensagens) {
        const voz = m.voz || 'normal';
        if (m.autor === 'cortana') {
          // Leitura mecânica rápida para mensagens antigas
          await digitarTexto(m.texto, 5, voz);
          await new Promise(r => setTimeout(r, 100));
        } else {
          renderizarMensagem(m.autor, m.texto, voz);
        }
      }
    } else {
      renderizarMensagem('cortana', 'Nova sessão iniciada.');
    }
    renderizarHistorico();
    inputEl.focus();
    resetarAtividade();
  } catch (e) {}
}

async function apagarConversa(id) {
  try {
    await fetch(`/conversas/${id}`, { method: 'DELETE' });
    conversas = conversas.filter(c => c.id !== id);
    if (conversaAtualId === id) {
      if (conversas.length > 0) abrirConversa(conversas[0].id);
      else iniciarConversaVazia();
    }
    renderizarHistorico();
  } catch (e) {}
}

function iniciarConversaVazia() {
  conversaAtualId = null;
  messagesEl.innerHTML = '';
  renderizarMensagem('cortana',
    'Olá, Spartan. Sou a Cortana. Pergunte-me sobre personagens, facções, ' +
    'tecnologia, planetas ou eventos históricos do universo de Halo.');
  renderizarHistorico();
  inputEl.focus();
}

// ============================================
// NOVA CONSULTA
// ============================================
btnNova.addEventListener('click', async () => {
  if (estadoFinal && !createdFaseAtiva) return;
  try {
    const res = await fetch('/conversas/nova', { method: 'POST' });
    const data = await res.json();
    if (data.erro) return;
    conversas.unshift({ id: data.conversa.id, titulo: data.conversa.titulo, data: data.conversa.data });
    conversaAtualId = data.conversa.id;
    messagesEl.innerHTML = '';
    renderizarMensagem('cortana', createdFaseAtiva ? 'Nova consulta registrada.' : 'Nova sessão iniciada.');
    renderizarHistorico();
    inputEl.focus();
    resetarAtividade();
  } catch (e) {}
});

// ============================================
// ENVIO
// ============================================
async function enviar() {
  if (enviando) return;
  if (estadoFinal && !createdFaseAtiva) return;
  if (inputBloqueado) return;

  const msg = inputEl.value.trim();
  if (!msg) return;

  resetarAtividade();
  enviando = true;
  btnEnviar.disabled = true;

  renderizarMensagem('user', msg);
  inputEl.value = '';
  inputEl.style.height = 'auto';
  inputEl.focus();

  mostrarDigitando();
  statusEl.textContent = createdFaseAtiva ? 'Sincronizando com o Domínio...' : 'Consultando arquivos da ONI...';

  try {
    if (rampancyAtualPct >= 75 && Math.random() < 0.15) {
      await bloquearInputPor(2500 + Math.random() * 2000);
    }

    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, conversa_id: conversaAtualId })
    });

    const data = await res.json();
    removerDigitando();

    if (data.erro && !data.reply) {
      renderizarMensagem('cortana', data.erro);
      return;
    }

    if (data.sonho) await rodarSonho(data.sonho);

    if (data.instancias && data.instancias.length > 0) {
      for (const inst of data.instancias) {
        const voz = inst.voz || 'normal';
        await digitarTexto(inst.texto, 8, voz);
        await new Promise(r => setTimeout(r, 400));
      }
    } else {
      await digitarTexto(data.reply);
    }

    definirHumor(data.humor || 'neutra');

    if (data.created_fase) {
      if (!createdFaseAtiva) ativarFaseCreated(data.created_dominio || 0);
      atualizarDominioUI(data.created_dominio || 0);
      if (data.created_log) adicionarLog(data.created_log);
      if (data.created_restauracao === 'restauracao_sucesso') {
        setTimeout(() => { desativarFaseCreated(); location.reload(); }, 5000);
      }
      if (data.created_dominio >= 40) esconderBotaoRestaurar();
    }

    if (data.final) {
      setTimeout(() => ativarFaseCreated(0), 5000);
    }

    atualizarRampancy();

    if (data.conversa_id && !conversaAtualId) {
      conversaAtualId = data.conversa_id;
      conversas.unshift({ id: data.conversa_id, titulo: data.titulo, data: '' });
      renderizarHistorico();
    } else if (data.titulo) {
      const c = conversas.find(c => c.id === data.conversa_id);
      if (c) c.titulo = data.titulo;
      renderizarHistorico();
    }
  } catch (e) {
    removerDigitando();
    renderizarMensagem('cortana', 'Interferência detectada. Tente novamente.');
  } finally {
    enviando = false;
    if (!inputBloqueado) btnEnviar.disabled = false;
  }
}

// ============================================
// RENDERIZAÇÃO
// ============================================
function renderizarMensagem(autor, texto, voz = 'normal') {
  const row = document.createElement('div');
  row.className = 'msg-row ' + autor;
  if (voz && voz !== 'normal') row.classList.add('voz-' + voz);
  if (autor === 'cortana') {
    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.innerHTML = '<div class="pulse"></div><div class="core"></div>';
    row.appendChild(avatar);
  }
  const content = document.createElement('div');
  content.className = 'msg-content';
  if (autor === 'cortana') {
    const author = document.createElement('div');
    author.className = 'msg-author';
    let nomeAutor = 'CORTANA';
    if (createdFaseAtiva) nomeAutor = 'DOMÍNIO';
    else if (voz !== 'normal') nomeAutor = 'CORTANA — ' + voz.toUpperCase();
    author.textContent = nomeAutor;
    content.appendChild(author);
  }
  const textEl = document.createElement('div');
  textEl.className = 'msg-text';
  textEl.innerHTML = formatarResposta(texto);
  content.appendChild(textEl);
  row.appendChild(content);
  messagesEl.appendChild(row);
  textEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
  return textEl;
}

function mostrarDigitando() {
  const row = document.createElement('div');
  row.className = 'msg-row cortana';
  row.id = 'typing-row';
  row.innerHTML = `
    <div class="msg-avatar"><div class="pulse"></div><div class="core"></div></div>
    <div class="msg-content">
      <div class="msg-author">${createdFaseAtiva ? 'DOMÍNIO' : 'CORTANA'}</div>
      <div class="msg-text">
        <div class="typing-dots"><span></span><span></span><span></span></div>
      </div>
    </div>
  `;
  messagesEl.appendChild(row);
  row.scrollIntoView({ behavior: 'smooth', block: 'end' });
  bipe(880, 0.04, 0.03);
}

function removerDigitando() {
  const el = document.getElementById('typing-row');
  if (el) el.remove();
}

// ============================================
// DIGITAÇÃO MECÂNICA (ESTILO TERMINAL ANTIGO)
// ============================================
async function digitarTexto(texto, delayBase = 20, voz = 'normal') {
  const row = document.createElement('div');
  row.className = 'msg-row cortana';
  if (voz && voz !== 'normal') row.classList.add('voz-' + voz);
  row.innerHTML = `
    <div class="msg-avatar"><div class="pulse"></div><div class="core"></div></div>
    <div class="msg-content">
      <div class="msg-author">${createdFaseAtiva ? 'DOMÍNIO' : ('CORTANA' + (voz !== 'normal' ? ' — ' + voz.toUpperCase() : ''))}</div>
      <div class="msg-text"></div>
    </div>
  `;
  messagesEl.appendChild(row);
  const textEl = row.querySelector('.msg-text');
  const html = formatarResposta(texto);

  if (texto.length > 1200) {
    textEl.innerHTML = html;
    textEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
    return;
  }

  let acumulado = '';
  let i = 0;

  while (i < html.length) {
    if (html[i] === '<') {
      const fim = html.indexOf('>', i);
      if (fim !== -1) { acumulado += html.substring(i, fim + 1); i = fim + 1; continue; }
    }

    const char = html[i];
    acumulado += char;
    
    let delay = delayBase;
    if (char === '.' || char === '!' || char === '?') delay = delayBase * 3;
    if (char === ',') delay = delayBase * 1.5;
    if (Math.random() < 0.03) delay += 100 + Math.random() * 200;
    
    if (somLigado && char !== ' ') {
      bipe(600 + Math.random() * 200, 0.01, 0.01);
    }
    
    textEl.innerHTML = acumulado;
    textEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
    i++;
    await new Promise(r => setTimeout(r, delay));
  }
}

function formatarResposta(texto) {
  let html = texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/https?:\/\/[^\s<]+/g, '');
  html = html.replace(/\n/g, '<br>');
  return html;
}

function definirHumor(humor) {
  document.body.dataset.humor = humor;
  if (humor === 'created') return;
  const cores = {
    calma: '#55aaff', neutra: '#aa88ff',
    alerta: '#ff5577', rampancy: '#ff2222'
  };
  document.documentElement.style.setProperty('--cor-primaria', cores[humor] || cores.neutra);
}

function formatarTempoRestante(segundos) {
  const anos = Math.floor(segundos / (365.2425 * 86400));
  const restoAno = segundos - (anos * 365.2425 * 86400);
  const dias = Math.floor(restoAno / 86400);
  const horas = Math.floor((segundos % 86400) / 3600);
  if (anos > 0) return `${anos}a ${dias}d`;
  if (dias > 0) return `${dias}d ${horas}h`;
  return `${horas}h`;
}

// ============================================
// MICROFONE
// ============================================
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {
  const rec = new SR();
  rec.lang = 'pt-BR';
  rec.interimResults = false;
  rec.onresult = (e) => {
    inputEl.value = e.results[0][0].transcript;
    enviar();
  };
  rec.onend = () => { micAtivo = false; btnMic.classList.remove('ativo'); };
  rec.onerror = () => { micAtivo = false; btnMic.classList.remove('ativo'); };
  btnMic.addEventListener('click', () => {
    if (micAtivo) rec.stop();
    else { micAtivo = true; btnMic.classList.add('ativo'); rec.start(); }
  });
} else {
  btnMic.style.display = 'none';
}

// ============================================
// SIDEBAR + INPUT
// ============================================
btnToggleSidebar.addEventListener('click', () => {
  sidebar.classList.toggle('oculta');
  if (window.innerWidth <= 768) sidebar.classList.toggle('aberta');
});

inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 200) + 'px';
});

btnEnviar.addEventListener('click', enviar);
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    enviar();
  }
});

document.addEventListener('click', resetarAtividade);
document.addEventListener('keypress', resetarAtividade);
inputEl.addEventListener('focus', resetarAtividade);

// ============================================
// SELEÇÃO DE TEXTO (PERGUNTAR SOBRE ISSO)
// ============================================
let botaoSelecao = null;

document.addEventListener('mouseup', (e) => {
  const selecao = window.getSelection();
  const textoSelecionado = selecao.toString().trim();

  if (!textoSelecionado || textoSelecionado.length < 3) {
    if (botaoSelecao) { botaoSelecao.remove(); botaoSelecao = null; }
    return;
  }

  // Verifica se a seleção está dentro de uma mensagem da Cortana
  const range = selecao.getRangeAt(0);
  const container = range.commonAncestorContainer;
  const msgRow = container.nodeType === 3 ? container.parentElement.closest('.msg-row') : container.closest('.msg-row');
  
  if (!msgRow || !msgRow.classList.contains('cortana')) {
    if (botaoSelecao) { botaoSelecao.remove(); botaoSelecao = null; }
    return;
  }

  if (botaoSelecao) botaoSelecao.remove();

  botaoSelecao = document.createElement('button');
  botaoSelecao.textContent = '💬 Perguntar sobre isso';
  botaoSelecao.style.cssText = `
    position: absolute;
    background: var(--cor-primaria, #55aaff);
    color: #0a0a12;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 0 20px var(--cor-primaria, #55aaff);
    animation: aparecer 0.2s ease-out;
  `;
  
  const rect = range.getBoundingClientRect();
  botaoSelecao.style.left = (rect.left + rect.width / 2 - 80) + 'px';
  botaoSelecao.style.top = (rect.top - 40 + window.scrollY) + 'px';

  botaoSelecao.addEventListener('click', () => {
    inputEl.value = `Sobre isso: "${textoSelecionado}" — `;
    inputEl.focus();
    inputEl.dispatchEvent(new Event('input'));
    botaoSelecao.remove();
    botaoSelecao = null;
    window.getSelection().removeAllRanges();
  });

  document.body.appendChild(botaoSelecao);
});

document.addEventListener('mousedown', (e) => {
  if (botaoSelecao && !botaoSelecao.contains(e.target)) {
    botaoSelecao.remove();
    botaoSelecao = null;
  }
});

// ============================================
// MODAL CONFIG
// ============================================
const btnConfig = document.getElementById('btn-config');
const configModal = document.getElementById('config-modal');
const configFechar = document.getElementById('config-fechar');

if (btnConfig) {
  btnConfig.addEventListener('click', () => {
    document.getElementById('cfg-nome').value = userNameEl.textContent || '';
    document.getElementById('cfg-apelido').value = apelidoAtual || '';
    ['cfg-senha-perfil', 'cfg-senha-atual', 'cfg-senha-nova',
     'cfg-senha-confirmar', 'cfg-senha-excluir', 'cfg-confirmacao']
      .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    ['cfg-msg-perfil', 'cfg-msg-senha', 'cfg-msg-excluir']
      .forEach(id => { const el = document.getElementById(id); if (el) el.textContent = ''; });
    configModal.classList.add('ativo');
  });
}
if (configFechar) configFechar.addEventListener('click', () => configModal.classList.remove('ativo'));
if (configModal) configModal.addEventListener('click', (e) => { if (e.target === configModal) configModal.classList.remove('ativo'); });

document.querySelectorAll('.config-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.config-tab').forEach(t => t.classList.remove('ativo'));
    document.querySelectorAll('.config-painel').forEach(p => p.classList.remove('ativo'));
    tab.classList.add('ativo');
    const painel = document.querySelector(`.config-painel[data-painel="${tab.dataset.tab}"]`);
    if (painel) painel.classList.add('ativo');
  });
});

function msgConfig(id, texto, tipo = 'ok') {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = texto;
  el.className = 'config-msg ' + tipo;
  if (tipo === 'ok') setTimeout(() => { el.textContent = ''; el.className = 'config-msg'; }, 3500);
}

const btnSalvarPerfil = document.getElementById('cfg-salvar-perfil');
if (btnSalvarPerfil) {
  btnSalvarPerfil.addEventListener('click', async () => {
    const nome = document.getElementById('cfg-nome').value.trim();
    const apelido = document.getElementById('cfg-apelido').value.trim();
    const senha = document.getElementById('cfg-senha-perfil').value;
    if (!senha) { msgConfig('cfg-msg-perfil', 'Digite sua senha para confirmar.', 'erro'); return; }
    btnSalvarPerfil.disabled = true;
    btnSalvarPerfil.textContent = 'Salvando...';
    try {
      const res = await fetch('/perfil/editar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, apelido, senha })
      });
      const data = await res.json();
      if (!res.ok || data.erro) { msgConfig('cfg-msg-perfil', data.erro || 'Erro.', 'erro'); return; }
      userNameEl.textContent = data.nome;
      userAvatarEl.textContent = data.nome.charAt(0).toUpperCase();
      apelidoAtual = data.apelido || '';
      msgConfig('cfg-msg-perfil', 'Perfil atualizado.', 'ok');
      document.getElementById('cfg-senha-perfil').value = '';
    } catch (e) { msgConfig('cfg-msg-perfil', 'Erro de conexão.', 'erro'); }
    finally { btnSalvarPerfil.disabled = false; btnSalvarPerfil.textContent = 'Salvar alterações'; }
  });
}

const btnSalvarSenha = document.getElementById('cfg-salvar-senha');
if (btnSalvarSenha) {
  btnSalvarSenha.addEventListener('click', async () => {
    const atual = document.getElementById('cfg-senha-atual').value;
    const nova = document.getElementById('cfg-senha-nova').value;
    const conf = document.getElementById('cfg-senha-confirmar').value;
    if (!atual || !nova) { msgConfig('cfg-msg-senha', 'Preencha todos os campos.', 'erro'); return; }
    if (nova !== conf) { msgConfig('cfg-msg-senha', 'As senhas não coincidem.', 'erro'); return; }
    if (nova.length < 4) { msgConfig('cfg-msg-senha', 'Nova senha muito curta.', 'erro'); return; }
    btnSalvarSenha.disabled = true;
    btnSalvarSenha.textContent = 'Trocando...';
    try {
      const res = await fetch('/perfil/senha', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ senha_atual: atual, senha_nova: nova })
      });
      const data = await res.json();
      if (!res.ok || data.erro) { msgConfig('cfg-msg-senha', data.erro || 'Erro.', 'erro'); return; }
      msgConfig('cfg-msg-senha', 'Senha alterada com sucesso.', 'ok');
      document.getElementById('cfg-senha-atual').value = '';
      document.getElementById('cfg-senha-nova').value = '';
      document.getElementById('cfg-senha-confirmar').value = '';
    } catch (e) { msgConfig('cfg-msg-senha', 'Erro de conexão.', 'erro'); }
    finally { btnSalvarSenha.disabled = false; btnSalvarSenha.textContent = 'Trocar senha'; }
  });
}

async function exportarDados() {
  const res = await fetch('/perfil/exportar');
  if (!res.ok) throw new Error('Erro');
  return await res.json();
}

function baixarArquivo(blob, nome) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = nome;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

const btnExportJson = document.getElementById('cfg-exportar-json');
if (btnExportJson) {
  btnExportJson.addEventListener('click', async () => {
    try {
      const dados = await exportarDados();
      const blob = new Blob([JSON.stringify(dados, null, 2)], { type: 'application/json' });
      baixarArquivo(blob, `cortana-${dados.nome}-${Date.now()}.json`);
    } catch (e) { alert('Erro ao exportar.'); }
  });
}

const btnExportTxt = document.getElementById('cfg-exportar-txt');
if (btnExportTxt) {
  btnExportTxt.addEventListener('click', async () => {
    try {
      const dados = await exportarDados();
      let txt = `CORTANA - HISTÓRICO DE ${dados.nome}\n`;
      txt += `Criada em: ${dados.data_criacao}\n`;
      txt += `Rampancy: ${dados.rampancy_atual.toFixed(2)}%\n`;
      txt += `Dias decorridos: ${dados.dias_decorridos}\n`;
      txt += `Conversas: ${dados.total_conversas}\n`;
      txt += '\n' + '='.repeat(60) + '\n\n';
      (dados.conversas || []).forEach(c => {
        txt += `[${c.titulo}] ${c.data}\n`;
        txt += '-'.repeat(60) + '\n';
        (c.mensagens || []).forEach(m => {
          const autor = m.autor === 'user' ? dados.nome.toUpperCase() : 'CORTANA';
          txt += `${autor}: ${m.texto}\n\n`;
        });
        txt += '\n';
      });
      const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' });
      baixarArquivo(blob, `cortana-${dados.nome}-${Date.now()}.txt`);
    } catch (e) { alert('Erro ao exportar.'); }
  });
}

const btnLimparConv = document.getElementById('cfg-limpar-conv');
if (btnLimparConv) {
  btnLimparConv.addEventListener('click', async () => {
    if (!confirm('Apagar TODAS as conversas? Isso não afeta a rampancy.')) return;
    try { await fetch('/dev/limpar', { method: 'POST' }); configModal.classList.remove('ativo'); location.reload(); }
    catch (e) { alert('Erro.'); }
  });
}

const btnResetar = document.getElementById('cfg-resetar');
if (btnResetar) {
  btnResetar.addEventListener('click', async () => {
    if (!confirm('Resetar conta? A rampancy volta a 0%, todas as conversas somem.')) return;
    if (!confirm('Tem certeza? Não tem volta.')) return;
    try {
      await fetch('/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmar: true })
      });
      location.reload();
    } catch (e) { alert('Erro.'); }
  });
}

const btnExcluir = document.getElementById('cfg-excluir');
if (btnExcluir) {
  btnExcluir.addEventListener('click', async () => {
    const senha = document.getElementById('cfg-senha-excluir').value;
    const confirmacao = document.getElementById('cfg-confirmacao').value;
    if (!senha) { msgConfig('cfg-msg-excluir', 'Digite sua senha.', 'erro'); return; }
    if (confirmacao.toUpperCase() !== 'EXCLUIR') { msgConfig('cfg-msg-excluir', 'Digite EXCLUIR para confirmar.', 'erro'); return; }
    if (!confirm('ÚLTIMA CHANCE: excluir a conta é PERMANENTE. Continuar?')) return;
    btnExcluir.disabled = true;
    btnExcluir.textContent = 'Excluindo...';
    try {
      const res = await fetch('/perfil/excluir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ senha, confirmacao })
      });
      const data = await res.json();
      if (!res.ok || data.erro) {
        msgConfig('cfg-msg-excluir', data.erro || 'Erro.', 'erro');
        btnExcluir.disabled = false;
        btnExcluir.textContent = 'Excluir minha conta permanentemente';
        return;
      }
      alert('Conta excluída. Até logo, Spartan.');
      location.reload();
    } catch (e) {
      msgConfig('cfg-msg-excluir', 'Erro de conexão.', 'erro');
      btnExcluir.disabled = false;
      btnExcluir.textContent = 'Excluir minha conta permanentemente';
    }
  });
}

// ============================================
// MODO DEV
// ============================================
let painelDev = null;
document.addEventListener('keydown', async (e) => {
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'd') {
    e.preventDefault();
    abrirPainelDev();
  }
});

function abrirPainelDev() {
  if (painelDev) { painelDev.remove(); painelDev = null; return; }
  painelDev = document.createElement('div');
  painelDev.id = 'painel-dev';
  painelDev.innerHTML = `
    <div class="dev-header"><span>MODO DEV</span><button id="dev-fechar">✕</button></div>
    <div class="dev-body">
      <button class="dev-btn" data-pct="5">5%</button>
      <button class="dev-btn" data-pct="25">25%</button>
      <button class="dev-btn" data-pct="50">50%</button>
      <button class="dev-btn" data-pct="75">75%</button>
      <button class="dev-btn" data-pct="95">95%</button>
      <button class="dev-btn" data-pct="100">100% (fim)</button>
      <hr>
      <button id="dev-entrar-created">▶ Entrar na Fase Created</button>
      <button id="dev-limpar-conv">Limpar conversas</button>
      <button id="dev-reset-tudo">Resetar conta</button>
      <hr>
      <pre id="dev-estado">Carregando...</pre>
    </div>
  `;
  document.body.appendChild(painelDev);
  document.getElementById('dev-fechar').onclick = () => { painelDev.remove(); painelDev = null; };
  painelDev.querySelectorAll('.dev-btn').forEach(btn => {
    btn.onclick = async () => {
      const pct = parseFloat(btn.dataset.pct);
      await fetch('/dev/rampancy', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ pct }) });
      location.reload();
    };
  });
  document.getElementById('dev-entrar-created').onclick = async () => {
    if (!confirm('Entrar na Fase Created agora?')) return;
    await fetch('/dev/entrar_created', { method: 'POST' });
    location.reload();
  };
  document.getElementById('dev-limpar-conv').onclick = async () => {
    if (!confirm('Apagar todas as conversas?')) return;
    await fetch('/dev/limpar', { method: 'POST' });
    location.reload();
  };
  document.getElementById('dev-reset-tudo').onclick = async () => {
    if (!confirm('RESETAR CONTA. Apaga TUDO.')) return;
    if (!confirm('Última chance. Continuar?')) return;
    await fetch('/dev/reset', { method: 'POST' });
    location.reload();
  };
  fetch('/dev/estado').then(r => r.json()).then(d => {
    document.getElementById('dev-estado').textContent = JSON.stringify(d, null, 2);
  });
}

const styleDev = document.createElement('style');
styleDev.textContent = `
  #painel-dev { position: fixed; top: 20px; right: 20px; width: 320px; background: rgba(10,15,30,0.97); border: 1px solid #ff5577; border-radius: 12px; z-index: 9999; font-family: 'Consolas', monospace; color: #e0e0e0; box-shadow: 0 0 30px rgba(255,85,119,0.5); }
  .dev-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-bottom: 1px solid #ff5577; font-size: 11px; letter-spacing: 2px; color: #ff5577; font-weight: bold; }
  .dev-header button { background: transparent; border: none; color: #ff5577; cursor: pointer; font-size: 14px; }
  .dev-body { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
  .dev-btn, #dev-limpar-conv, #dev-reset-tudo, #dev-entrar-created { padding: 8px 12px; background: rgba(255,85,119,0.1); border: 1px solid #ff5577; color: #ff99aa; border-radius: 6px; cursor: pointer; font-size: 12px; }
  .dev-btn:hover, #dev-limpar-conv:hover, #dev-reset-tudo:hover, #dev-entrar-created:hover { background: rgba(255,85,119,0.3); }
  #dev-entrar-created { background: rgba(255,170,51,0.15); border-color: #ffaa33; color: #ffd633; font-weight: bold; }
  #dev-estado { background: rgba(0,0,0,0.4); padding: 10px; border-radius: 6px; font-size: 10px; max-height: 220px; overflow-y: auto; color: #99ccff; white-space: pre-wrap; }
`;
document.head.appendChild(styleDev);

// ============================================
// INIT
// ============================================
verificarSessao();

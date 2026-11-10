# 🦾 J.A.R.V.I.S. — Assistente Pessoal (Protótipo)

> *"Às suas ordens, senhor."*

Assistente estilo **Jarvis do Homem de Ferro**, feito em **HTML/CSS/JS puro** + um
mini-servidor Python **sem dependências externas**. Entende comandos em português,
responde falando e conversa com uma IA gratuita quando o assunto sai dos atalhos.

**v3.3 — Modo Turbo:** respostas locais instantâneas, imagens mais rápidas,
servidor com gzip/cache e animações leves.

![status](https://img.shields.io/badge/status-prot%C3%B3tipo-orange)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## ✨ Funcionalidades

| Comando | O que faz |
|---|---|
| `que horas são` / `que dia é hoje` | 🕐 Hora e data **sem sair da página** |
| `bateria` | 🔋 Nível real da bateria (quando o navegador permite) |
| `conta uma piada` | 😄 Humor local, sem esperar a IA |
| `2 + 2` / `quanto é 15 * 3` | 🧮 Calculadora local |
| `abrir youtube / whatsapp / drive / maps` | 🌐 Atalhos instantâneos |
| `transferir 50 reais para o Zé` | 💸 Pix **simulado**, execução imediata |
| `saldo` / `extrato` / `resetar saldo` | 💰 Carteira simulada (R$ 1.000 iniciais) |
| `otimizar o celular` | ⚡ Otimização **simulada** com barra rápida |
| `imagem de um dragão estilo anime` | 🎨 16 estilos, **turbo** por padrão; `HD` para mais qualidade |
| `estilos` / `outra` | 🎨 Lista estilos / refaz a última imagem |
| `notícias` / `clima` | 📰🌤️ Google News Brasil e wttr.in, com timeout curto |
| `timer de 10 segundos` | ⏱️ Aviso sonoro/visual |
| qualquer outra pergunta | 🧠 Cérebro neural (Pollinations) com contexto enxuto |
| 🎤 Botão de microfone | Fale os comandos por voz (Web Speech API, pt-BR) |

## ⚡ O que mudou no desempenho

- **Sem rede para o básico:** horas, data, bateria, piadas, contas, apps, saldo,
  Pix, extrato, otimizar e timer respondem direto no navegador.
- **Menos espera artificial:** o "digitando..." caiu de ~350 ms para ~60 ms; o boot
  e a otimização também ficaram quase instantâneos.
- **Imagens turbo:** `model=turbo`, `enhance=false`, 512×512 (ou 768×432 / 512×768),
  um único `<img>` com `fetchpriority=high`, espaço reservado e fallback automático
  para `flux` se o turbo falhar. O download começa **no mesmo instante** do pedido.
- **IA mais leve:** contexto curto, histórico de 2 trocas, `max_tokens=120`, corrida
  entre POST e GET com `AbortController` e timeout de 10 s.
- **Notícias/clima:** servidor local e fonte direta disputam em paralelo (6 s), com
  cache positivo, cache negativo e *stale-on-error* no `server.py`.
- **Servidor:** HTTP/1.1 keep-alive, gzip para HTML/JSON, `Cache-Control`, e
  compactação em memória por `mtime`.
- **Interface:** animações só com `transform`/`opacity`, sem `backdrop-filter`, sem
  progresso por `width`, relógio atualizado 1x por minuto e respeito a
  `prefers-reduced-motion`.

> 💡 Notícias e clima dependem de acesso externo. Em ambientes sem saída para a
> internet (como alguns sandboxes), o app avisa rápido em vez de ficar travado;
> os comandos locais continuam funcionando.

## 🛡️ Simulações e segurança

Nada aqui mexe com dinheiro ou com o sistema operacional de verdade:

- **Pix, saldo e otimização são simulações locais** — não há autenticação bancária,
  nem permissão para encerrar processos do aparelho.
- O Pix simulado é executado na hora, sem confirmação, conforme configurado pelo
  usuário ("modo confiança total"). Ainda é só um número no `localStorage`.
- Textos dinâmicos são escapados antes de ir para o DOM, e links externos usam
  `rel="noopener noreferrer"`.

## 🚀 Como rodar

```bash
python3 server.py
# abra http://localhost:8100
```

Não precisa instalar nada — só Python 3. O servidor escuta em `0.0.0.0:8100`,
então também funciona na prévia do Arena.ai e em outros dispositivos da mesma rede.

> 💡 Dica: no celular, abra no Chrome e use "Adicionar à tela inicial" para ter
> ícone de app de verdade.

## 🗺️ Roadmap de sonhos

- [x] Conectar a uma IA de verdade para conversar sobre qualquer coisa
- [ ] Integrar o áudio de boas-vindas ao boot (com botão de mudo)
- [ ] Versão Android nativa (WebView + plugins) para ações reais no aparelho
- [ ] Modo "Sexta-feira" (voz feminina)

## 📄 Licença

MIT — use, modifique e divirta-se. Criado com o Modo Agente da Arena.ai.

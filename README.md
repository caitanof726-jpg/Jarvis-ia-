# 🦾 J.A.R.V.I.S. — Assistente Pessoal (Protótipo)

> *"Às suas ordens, senhor."*

Assistente pessoal estilo **Jarvis do Homem de Ferro**, feito em HTML/CSS/JS puro + um
mini-servidor Python (sem dependências externas). Entende comandos em **português**,
**responde falando** e **nunca executa uma ação sensível sem confirmação do usuário**.

![status](https://img.shields.io/badge/status-prot%C3%B3tipo-orange)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## ✨ Funcionalidades

| Comando | O que faz |
|---|---|
| `transferir 50 reais para o Zé` | 💸 Pix **simulado** com modal de confirmação |
| `saldo` / `resetar saldo` | 💰 Carteira simulada (começa com R$ 1.000) |
| `otimizar o celular` | ⚡ Otimização **simulada** com barra de progresso |
| `notícias` | 📰 Manchetes **reais** do Google News Brasil, com detector de notícia importante |
| `que horas são` / `que dia é hoje` | 🕐 Hora e data |
| `bateria` | 🔋 Nível real da bateria (quando o navegador permite) |
| `abrir youtube / whatsapp / drive / maps` | 🌐 Atalhos |
| `conta uma piada` | 😄 Humor de estagiário |
| 🎤 Botão de microfone | Fale os comandos por voz (Web Speech API, pt-BR) |

## 🛡️ Filosofia de segurança

**Regra nº 1:** nenhuma ação sensível acontece sem o usuário clicar em **CONFIRMAR**.

**Por que as transferências são simuladas?** Bancos (ainda bem!) não permitem que
apps de terceiros movam dinheiro sozinhos — Pix e transferências exigem autenticação
dentro do app oficial do banco. Qualquer coisa prometendo o contrário é golpe.
Este projeto demonstra a **interface e o fluxo de confirmação** que um assistente
assim deveria ter.

**Por que a otimização é simulada?** Um app web não tem permissão para encerrar
processos do sistema. Para isso seria preciso um app nativo Android (com permissões
de acessibilidade) — fica de roadmap. 😉

## 🚀 Como rodar

```bash
python3 server.py
# abra http://localhost:8100
```

Não precisa instalar nada — só Python 3.

> 💡 Dica: no celular, abra no Chrome e use "Adicionar à tela inicial" para ter
> ícone de app de verdade.

## 🗺️ Roadmap de sonhos

- [ ] Conectar a uma IA de verdade (API de LLM) para conversar sobre qualquer coisa
- [ ] Versão Android nativa (WebView + plugins) para ações reais no aparelho
- [ ] Integrações via automação (Tasker/Termux) para quem for raiz
- [ ] Modo "Sexta-feira" (voz feminina)

## 📄 Licença

MIT — use, modifique e divirta-se. Criado com o Modo Agente da Arena.ai.

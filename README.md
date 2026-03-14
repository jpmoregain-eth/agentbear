# 🐻 Agent Bear Corps (ABC)

**Your personal AI agent. Multi-provider. Multi-personality. Yours to command.**

---

## 🤔 What is Agent Bear Corps?

Agent Bear Corps lets you create your own AI agent that:
- **Chats with you** like a personal assistant
- **Remembers conversations** (persistent memory)
- **Uses multiple AI brains** (Anthropic, OpenAI, Google, Chinese LLMs, etc.)
- **Has different personalities** (professional, funny, technical, etc.)
- **Runs on your computer** (your data stays private)
- **Has built-in tools** (file ops, code tools, GitHub, crypto, web search)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Download

```bash
git clone https://github.com/jpmoregain-eth/agentbearcorps.git
cd agentbearcorps
```

### Step 2: Install

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run Setup Wizard

```bash
python3 setup_wizard.py
```

This will:
1. **Open your browser** automatically (at http://localhost:5000)
2. **Guide you through 6 simple steps** to configure your agent
3. **Save your configuration** as a YAML file in `~/.agentbear/agents/`
4. **Launch your agent** (optional)

---

## 🎮 How to Use Your Agent

### Option A: Interactive Mode

```bash
python3 agent.py --config ~/.agentbear/agents/my-agent.yaml
```

Type your messages, press Enter. Type `exit` to quit.

### Option B: Start API Server

```bash
python3 api_server.py --config ~/.agentbear/agents/my-agent.yaml --port 8080
```

Then talk to your agent via API:
```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Option C: Telegram Bot 💬

If you enabled Telegram during setup, the bot starts automatically with the agent:

1. **Find your bot on Telegram:**
   - Search for your bot's username (set via @BotFather)
   - Or use the bot link: `t.me/YourBotName`

2. **Start chatting:**
   - Send `/start` to begin
   - Type any message - your agent will reply!
   - Use `/help` to see available commands

> 💡 **Tip:** The Telegram bot uses the same memory as the API, so conversations are remembered across platforms!

---

## 📁 File Structure

```
agentbearcorps/
├── agent.py                 # Main agent runtime
├── agentbear.py            # CLI tool (legacy)
├── api_server.py           # HTTP API server
├── setup_wizard.py         # Web-based setup wizard
├── config.py               # Configuration management
├── memory.py               # Conversation persistence
├── providers.py            # LLM provider integrations
├── security.py             # Security & encryption
├── crypto_utils.py         # Encryption utilities
├── file_tools.py           # File operations capability
├── code_tools.py           # Code generation/review capability
├── github_tools.py         # GitHub integration
├── crypto_tools.py         # CCXT crypto trading
├── web_search_tools.py     # Headless browser web search
├── telegram/               # Telegram bot handlers
├── templates/              # HTML templates for wizard
│   ├── base.html
│   ├── step1.html - step6.html
│   └── complete.html
├── config/                 # Default configurations
│   ├── capabilities.yaml   # Available capabilities
│   ├── providers.yaml      # AI provider configs
│   ├── personas.yaml       # Personality definitions
│   └── languages.yaml      # Language settings
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🔑 Getting API Keys

Your agent needs API keys to talk to AI services:

### Anthropic (Claude) - Recommended ⭐
1. Go to https://console.anthropic.com
2. Sign up / Log in
3. Click "Get API Keys"
4. Create new key (starts with `sk-ant-`)

### OpenAI (GPT)
1. Go to https://platform.openai.com
2. Sign up / Log in
3. Go to "API Keys" in settings
4. Create new secret key (starts with `sk-`)

### Google (Gemini)
1. Go to https://ai.google.dev
2. Sign up with Google account
3. Get API key

### Telegram Bot Token
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Copy the token (format: `123456789:ABCdef...`)

### GitHub Token (Optional)
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `read:user`

### Crypto Exchange Keys (Optional)
- Sign up at your preferred exchange (Binance, Coinbase, etc.)
- Generate API key in account settings
- **Note:** Optional - only needed for private data (balances)

> ⚠️ **Security:** API keys are automatically encrypted at rest using Fernet encryption. Your master key is stored at `~/.agentbear/.master_key`.

---

## 🛠️ Capabilities

### ✅ Working (No API Key Required)
| Capability | Description | Example Commands |
|------------|-------------|------------------|
| **File Operations** | Read, write, edit files | "Read ~/.bashrc", "Write hello to ~/test.txt" |
| **Code Tools** | Generate, review, debug code | "Generate Python sort function", "Review this code" |
| **Git Operations** | Git commands | (Planned) |
| **Web Fetch** | Download web pages | "Fetch https://example.com" |

### ✅ Working (API Key Required)
| Capability | Description | Required Keys |
|------------|-------------|---------------|
| **LLM Chat** | AI conversation | Anthropic/OpenAI/etc. API key |
| **Telegram Bot** | Telegram messaging | Telegram bot token |
| **GitHub Integration** | Repo access, issues | GitHub personal access token |
| **Crypto Trading** | Market data via CCXT | Exchange API key (optional) |
| **Web Search** | Google search | None (uses headless browser) |

---

## 🎭 Personalities (Personas)

Choose how your agent talks:

| Persona | Style |
|---------|-------|
| **Professional** | Formal, business-like, concise |
| **Friendly** | Warm, approachable, conversational |
| **Technical** | Precise, detailed, uses tech terms |
| **Teacher** | Patient, explanatory, educational |
| **Creative** | Imaginative, suggests ideas |
| **Humorous** | Witty, playful, tells jokes |

---

## 🧠 AI Models Available

### 🇺🇸 Western Models
| Provider | Best Models | Use Case |
|----------|-------------|----------|
| **Anthropic** | Claude Sonnet 4.6 ⭐ | Best overall, coding |
| **OpenAI** | GPT-5.4 | General purpose |
| **Google** | Gemini 3 Pro | Long documents |
| **xAI** | Grok-4 | Real-time knowledge |

### 🇨🇳 Chinese Models
| Provider | Best Models | Use Case |
|----------|-------------|----------|
| **DeepSeek** | V3.2 | Open-source coding |
| **Alibaba** | Qwen3.5-Plus | Versatile agent |
| **Moonshot** | Kimi K2.5 | Long context (256K) |
| **Baidu** | ERNIE 5.0 | Multimodal |

---

## 🔒 Security Features

- **Encrypted API Keys:** All API keys encrypted at rest
- **Jailbreak Detection:** Prevents prompt injection attacks
- **Secure Permissions:** Files restricted to `~/.agentbear/` directory
- **Audit Logging:** Security events logged
- **Secret Redaction:** Automatically redacts secrets from responses

---

## ❓ Troubleshooting

### "Module not found"
Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

### "Port already in use"
Kill existing process or change port:
```bash
# Kill on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
python3 setup_wizard.py  # Uses port 5000 by default
python3 api_server.py --port 8080
```

### "Telegram bot not responding"
- Check bot token is correct
- Ensure no other instance is using the same token
- Check `/tmp/<agent-name>.log` for errors

---

## 🤝 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     USER INTERFACES                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Telegram │  │ HTTP API │  │ Interactive Terminal │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
└───────┼─────────────┼───────────────────┼──────────────┘
        │             │                   │
        └─────────────┴───────────────────┘
                      │
        ┌─────────────▼─────────────┐
        │      ABCAIAgent           │
        │  ┌─────────────────────┐  │
        │  │  Security Manager   │  │
        │  │  - Jailbreak check  │  │
        │  │  - Secret redaction │  │
        │  └─────────────────────┘  │
        │  ┌─────────────────────┐  │
        │  │  Tool Router        │  │
        │  │  - File tools       │  │
        │  │  - Code tools       │  │
        │  │  - GitHub tools     │  │
        │  │  - Crypto tools     │  │
        │  └─────────────────────┘  │
        │  ┌─────────────────────┐  │
        │  │  LLM Provider       │  │
        │  │  - Anthropic        │  │
        │  │  - OpenAI           │  │
        │  │  - Google           │  │
        │  └─────────────────────┘  │
        └───────────────────────────┘
                      │
        ┌─────────────▼─────────────┐
        │      Persistence          │
        │  ┌─────────────────────┐  │
        │  │  SQLite Memory DB   │  │
        │  │  (~/.agentbear/)    │  │
        │  └─────────────────────┘  │
        └───────────────────────────┘
```

---

## 📜 License

MIT License - Agent Bear Corps 🐻

**Made with ❤️ for the AI community**

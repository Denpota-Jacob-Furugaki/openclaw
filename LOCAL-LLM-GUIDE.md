# Local LLM for OpenClaw - Complete Guide

## Why Use Local LLM?

**Cost Savings:**
- Claude Sonnet 4.5: ~$3 per 1M tokens
- OpenAI GPT-4: ~$10 per 1M tokens
- **Local LLM: $0** ✅

**Privacy:**
- All processing happens on your computer
- No data sent to external APIs

## Model Comparison

| Model | Size | RAM Needed | Best For | Speed |
|-------|------|------------|----------|-------|
| **qwen2.5-coder:14b** | 8.9GB | 12GB | Coding, OpenClaw | Fast |
| **deepseek-r1:7b** | 4.7GB | 8GB | Reasoning, thinking | Very Fast |
| **deepseek-r1:14b** | 8.9GB | 12GB | Advanced reasoning | Fast |
| **llama3.1:8b** | 4.7GB | 8GB | General chat | Very Fast |
| **mistral:7b** | 4.1GB | 6GB | Quick responses | Fastest |
| **codestral:22b** | 13GB | 16GB | Professional coding | Medium |
| **qwen2.5-coder:32b** | 20GB | 24GB | Best quality coding | Slow |

## Quick Setup

### 1. Install Ollama
```powershell
winget install Ollama.Ollama
```
Restart terminal after installation.

### 2. Download Model (Run the helper script)
```powershell
cd C:\Users\denpo\.openclaw
.\setup-local-llm.ps1
```

OR manually:
```powershell
# Choose one:
ollama pull qwen2.5-coder:14b    # Recommended for OpenClaw
ollama pull deepseek-r1:7b        # Lighter alternative
ollama pull llama3.1:8b           # General purpose
```

### 3. Update OpenClaw Config

Edit `openclaw.json`:
```json
{
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5-coder:14b"
    }
  }
}
```

### 4. Restart OpenClaw
```powershell
Stop-Process -Name node -Force
npx --no openclaw gateway --port 8080
```

## Advanced: Multiple Models

Keep both local and cloud models:

```json
{
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5-coder:14b"
    }
  }
}
```

In `agents/main/agent/models.json`:
```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://127.0.0.1:11434",
      "api": "ollama",
      "models": [
        {
          "id": "qwen2.5-coder:14b",
          "name": "qwen2.5-coder:14b"
        },
        {
          "id": "deepseek-r1:7b",
          "name": "deepseek-r1:7b"
        }
      ]
    },
    "anthropic": {
      "baseUrl": "https://api.anthropic.com",
      "api": "openai",
      "apiKey": "your-key"
    }
  }
}
```

Then switch models:
```powershell
# Use local (free)
npx --no openclaw message send --model "ollama/qwen2.5-coder:14b" --text "test"

# Use Claude (when you need best quality)
npx --no openclaw message send --model "anthropic/claude-sonnet-4-5" --text "test"
```

## Cost-Saving Strategy

**Daily work**: Use local model (free)
**Complex tasks**: Use Claude/GPT-4 (pay per use)

Example config:
- Default: `ollama/qwen2.5-coder:14b` (free)
- Fallback: `anthropic/claude-sonnet-4-5` (when local can't handle it)

## Performance Tips

### Speed Up Inference
```powershell
# Use smaller quantization
ollama pull qwen2.5-coder:7b      # Faster than 14b

# Or use Q4 quantization
ollama pull llama3.1:8b-q4_0      # Smaller, faster
```

### Multiple Models
```powershell
# Download multiple, switch as needed
ollama pull qwen2.5-coder:14b     # For coding
ollama pull llama3.1:8b           # For chat
ollama pull deepseek-r1:7b        # For reasoning

# Switch in OpenClaw by changing config
```

### Check Model Info
```powershell
ollama list                       # See downloaded models
ollama show qwen2.5-coder:14b    # Model details
```

## Troubleshooting

### Ollama not running?
```powershell
# Start Ollama service
Start-Service Ollama

# Or run manually
ollama serve
```

### OpenClaw can't connect?
Check `models.json` has correct baseUrl:
```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://127.0.0.1:11434",
      "api": "ollama"
    }
  }
}
```

### Model too slow?
- Use smaller model (7b instead of 14b)
- Close other applications
- Use Q4 quantization

### Out of memory?
- Use smaller model
- Close browser tabs
- Restart Ollama: `ollama serve`

## My Recommendation for You

Based on your setup:

**Start with:** `qwen2.5-coder:14b`
- Excellent for coding (OpenClaw's main use)
- Good balance of quality and speed
- Only 8.9GB

**Add later:** `deepseek-r1:7b`
- For complex reasoning tasks
- Lighter, faster
- Great complement

**Keep Claude as fallback:**
- For critical decisions
- When you need best quality
- Complex multi-step tasks

## Monthly Cost Comparison

**All Cloud (current):**
- 1000 messages/month
- Average 500 tokens/message
- Claude Sonnet: ~$1.50/month

**Hybrid (recommended):**
- 900 messages local (free)
- 100 messages Claude (important ones)
- Cost: ~$0.15/month
- **Savings: 90%**

**All Local:**
- 1000 messages/month
- Cost: $0
- **Savings: 100%**

Electricity cost: ~$0.01/hour = ~$2-3/month if running 24/7
Still cheaper than cloud!

# Education Planning Dashboard – Microservices Setup

## 📦 Overview

This project is a multi-service application built using Docker. It consists of four core services:

### 🔹 Main Services

#### 1. **djangoapi**

* Backend API built with Django
* Provides core data endpoints (programs, NOC groupings, etc.)
* Uses a SQLite database stored in a mounted volume

#### 2. **aiservice**

* FastAPI-based AI service
* Handles:

  * Chatbot queries
  * Match-making logic
  * Forecast and Income distribution analysis. 
  * Shared memory between models for conversational AI.
* Connects to a locally running **Ollama instance** (host machine)
* Please note that this relies on the host system have **Ollama installed** on the host system.
* We will be adding a container in the future that installs the Ollama ecosystem and required models. 

#### 3. **dataprocessingservice**

* FastAPI service responsible for:

  * Data transformation
  * Aggregation
  * KPI calculations
* Acts as a middleware between Django API and frontend

#### 4. **application**

* Dash web application (frontend)
* Consumes:
  * Data Processing Service
  * AI Service

---

## 🧱 Architecture

```
Application (Dash UI)
        ↓
[DataProcessingService] +  [AIService → Ollama (host)]
        ↓
    DjangoAPI
```

---

# 🚀 Getting Started

---

## 🔧 1. Prerequisites

### Install:

* Docker
* Docker Compose
* Ollama (installed locally on host machine)

---

# 🐳 Docker Usage

---

## 🔨 Build ALL services

```bash
docker-compose build
```

---

## ▶️ Run ALL services

```bash
docker-compose up
```

Or in detached mode:

```bash
docker-compose up -d
```

---

## 🧩 Build ONE service only

```bash
docker-compose build aiservice
```

Other examples:

```bash
docker-compose build djangoapi
docker-compose build dataprocessingservice
docker-compose build application
```

---

## ▶️ Run ONE service

```bash
docker-compose up aiservice
```

---

## 🔁 Rebuild after changes

```bash
docker-compose build <service_name>
```

Example:

```bash
docker-compose build dataprocessingservice
```

---

## 🛑 Stop all services

```bash
docker-compose down
```

---

# 🌐 Service Endpoints

| Service         | URL                   |
| --------------- | --------------------- |
| Django API      | http://localhost:8000 |
| AI Service      | http://localhost:8010 |
| Data Processing | http://localhost:8012 |
| Dash App        | http://localhost:8519 |

---

# 🤖 Ollama Setup (Required for AI Service)

The AI service expects Ollama to be running on your **host machine**, not in Docker.

---

## 🪟 Windows

### Install Ollama:

1. Download from: https://ollama.com/download
2. Run installer
3. Start Ollama (runs in background)

### Verify:

```bash
ollama list
```

---

## 🍎 macOS

### Install via Homebrew:

```bash
brew install ollama
```

### Start service:

```bash
ollama serve
```

---

## 🐧 Linux (Ubuntu)

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Start:

```bash
ollama serve
```

---

# 📥 Pull Required Models

Run these on your host machine:

```bash
ollama pull qwen2.5:14b-instruct-q4_K_M
ollama pull qwen2.5:7b-instruct
ollama pull granite3.3:8b
ollama pull llama3.1:8b
```

---

# 🔗 Docker ↔ Ollama Connection

The AI service connects to Ollama via:

```text
http://host.docker.internal:11434
```

This allows Docker containers to communicate with services running on your host machine.

---

# ⚠️ Important Notes

### 🔹 GPU Usage

* Ollama will automatically use GPU if available
* Ensure:

  * NVIDIA drivers installed
  * Ollama configured correctly

---

### 🔹 Health Checks

Each service includes a `/health/` endpoint used by Docker to manage dependencies.

---

### 🔹 Logs

Logs are written to:

```text
./logs/
```

---

### 🔹 Volumes

| Path                   | Purpose       |
| ---------------------- | ------------- |
| `./Repository`         | Shared data   |
| `./logs`               | Log files     |
| `~/.cache/huggingface` | Model caching |

---

# 🧪 Troubleshooting

---

## ❌ Cannot connect to Ollama

Check:

```bash
ollama serve
```

Then:

```bash
curl http://localhost:11434/api/tags
```

---

## ❌ Service cannot reach another service

Make sure:

* Using **service name**, not `localhost`
* Example:

  * ✅ `http://djangoapi:8000`
  * ❌ `http://localhost:8000`

---

## ❌ Changes not reflected

Rebuild:

```bash
docker-compose build <service>
```

---

# 🎯 Summary

* Docker runs all services except Ollama
* Ollama runs on host for GPU access
* Services communicate via Docker network
* Environment variables control endpoints

---

# 💡 Future Improvements

* Add GPU-aware container orchestration
* Centralized config management
* Service discovery layer
* Model routing (fast vs accurate)
* A new microservice that updates stats canada data. 
* Exposing our VectorDB through Django instead of allow AI service direct access.

---

## 👨‍💻 Authors

* Abira Esther Demello, Tejas Kumar and Ed Wang – 2026

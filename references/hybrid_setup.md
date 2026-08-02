# Настройка гибридной инфраструктуры разработки (Cloud Orchestrator + Local Workers)

В данном руководстве описан процесс развертывания и настройки гибридной среды для работы многоагентной системы SDD.

## Архитектурный паттерн

- **Orchestrator (Уровень 1-2)**: Облачные модели (Gemini 3.5 Pro / Flash). Имеют длинный контекст, высокую логику и общую координацию.
- **Workers (Уровень 3)**: Локальные модели для кодинга (Qwen 2.5 Coder, DeepSeek Coder). Выполняют генерацию мелкого кода по спецификации и тестам на локальном железе разработчика.

---

## 1. Установка и запуск локальной LLM

Для запуска локальной модели рекомендуется использовать **Ollama** (простота настройки) или **LM Studio** (удобный GUI).

### Вариант А: Использование Ollama (Рекомендуемый)
1. Скачайте и установите Ollama с официального сайта: [ollama.com](https://ollama.com/).
2. Откройте терминал и загрузите модель, оптимизированную для написания кода (например, Qwen 2.5 Coder 7B или DeepSeek Coder 6.7B):
   ```bash
   # Для видеокарт с 6-8 ГБ VRAM (рекомендуется Qwen 2.5 Coder 7B)
   ollama run qwen2.5-coder:7b
   
   # Для видеокарт с 12+ ГБ VRAM (рекомендуется 14B/32B версия)
   ollama run qwen2.5-coder:14b
   ```
3. Сервер Ollama автоматически запустится на порту `http://localhost:11434`.

### Вариант Б: Использование LM Studio
1. Скачайте LM Studio с [lmstudio.ai](https://lmstudio.ai/).
2. В строке поиска найдите `qwen2.5-coder` или `deepseek-coder` и скачайте GGUF-файл (выбирайте квантование `Q4_K_M` или `Q5_K_M`).
3. Перейдите во вкладку **Local Server** (значок двунаправленных стрелок слева).
4. Выберите скачанную модель наверху и нажмите **Start Server**.
5. Сервер по умолчанию запустится на порту `http://localhost:1234` с API, совместимым с OpenAI.

### Вариант В: Использование llama.cpp / llama-server
1. Соберите или скачайте бинарный файл `llama-server` (из проекта [llama.cpp](https://github.com/ggerganov/llama.cpp)).
2. Запустите сервер с нужной GGUF-моделью:
   ```bash
   llama-server -m models/qwen2.5-coder-7b-instruct-q4_k_m.gguf -c 8192 --port 8080
   ```
3. Сервер запустится на порту `http://127.0.0.1:8080` с OpenAI-совместимым REST API (`/v1/chat/completions`).

---

## 2. Использование скрипта интеграции (`ask_local_llm.py`)

На Слое 3 (Execution) агент-оркестратор вызывает локальный скрипт `ask_local_llm.py`. Скрипт поддерживает **LM Studio**, **Ollama** и **llama.cpp** с автоматическим обнаружением работающего локального сервера.

### Команды вызова `ask_local_llm.py`:

```bash
# Автоматическое определение (LM Studio :1234 -> Ollama :11434 -> llama.cpp :8080)
python scripts/ask_local_llm.py --prompt prompts/devops_task.md --out output.code

# Явное указание LM Studio
python scripts/ask_local_llm.py --provider lmstudio --prompt prompts/devops_task.md --out output.code

# Явное указание llama.cpp (порты/эндпоинты по умолчанию 127.0.0.1:8080)
python scripts/ask_local_llm.py --provider llamacpp --prompt prompts/devops_task.md --out output.code

# С передачей дополнительных правил фреймворка
python scripts/ask_local_llm.py --provider llamacpp --prompt prompt.md --rules references/backend_best_practices.md --out code.py
```

### Формат обращения к LM Studio / llama.cpp API (OpenAI Compatible):

```python
# Эндпоинт LM Studio: http://localhost:1234/v1/chat/completions
# Эндпоинт llama.cpp: http://127.0.0.1:8080/v1/chat/completions
payload = {
    "model": "local-model", # Или имя конкретной загруженной модели
    "messages": [
        {"role": "system", "content": rules_text},
        {"role": "user", "content": prompt_text}
    ],
    "temperature": 0.2,
    "stream": False
}
```

---

## 3. Рекомендации по оптимизации локальных моделей

- **Квантование (Quantization)**: Всегда выбирайте модели с квантованием `Q4_K_M` или `Q5_K_M`. Они сохраняют 99% точности оригинальной модели, но требуют в 2 раза меньше видеопамяти (VRAM).
- **VRAM limit**: Убедитесь, что модель полностью помещается в видеопамять вашей видеокарты. Если модель выйдет за пределы VRAM в оперативную память (RAM), скорость генерации кода упадет в 10–50 раз.
  - **Для 8 ГБ VRAM**: Использовать модели до 7B-8B параметров.
  - **Для 12 ГБ VRAM**: Использовать модели до 14B параметров.
  - **Для 16 ГБ VRAM**: Использовать модели до 32B параметров.

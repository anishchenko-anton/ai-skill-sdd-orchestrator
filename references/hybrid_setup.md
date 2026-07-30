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

---

## 2. Использование скрипта интеграции (`ask_local_llm.py`)

На Слое 3 (Execution) агент-оркестратор вызывает локальный скрипт `ask_local_llm.py`. Скрипт поддерживает как **LM Studio**, так и **Ollama** с автоматическим обнаружением работающего локального сервера.

### Команды вызова `ask_local_llm.py`:

```bash
# Автоматическое определение (сначала LM Studio на порту 1234, затем Ollama на 11434)
python scripts/ask_local_llm.py --prompt prompts/devops_task.md --out output.code

# Явное указание LM Studio
python scripts/ask_local_llm.py --provider lmstudio --prompt prompts/devops_task.md --out output.code

# С передачей дополнительных правил фреймворка
python scripts/ask_local_llm.py --provider lmstudio --prompt prompt.md --rules references/backend_best_practices.md --out code.py
```

### Формат обращения к LM Studio API (OpenAI Compatible):

```python
# Эндпоинт LM Studio по умолчанию: http://localhost:1234/v1/chat/completions
payload = {
    "model": "local-model", # В LM Studio по умолчанию используется загруженная модель
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

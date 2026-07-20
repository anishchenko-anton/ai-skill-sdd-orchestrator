import os
import urllib.request
import urllib.error
import json
from pathlib import Path

def check_file_exists(filepath: Path, name: str) -> bool:
    if filepath.exists():
        print(f"✅ {name} найден ({filepath})")
        return True
    else:
        print(f"❌ {name} НЕ НАЙДЕН. Ожидаемый путь: {filepath}")
        return False

def check_ollama_running() -> bool:
    url = "http://localhost:11434/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                models = [m['name'] for m in data.get('models', [])]
                print(f"✅ Ollama работает. Найдено моделей: {len(models)}")
                if models:
                    print(f"   Доступные модели: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
                else:
                    print("   ⚠️ Внимание: В Ollama нет скачанных моделей. Запустите 'ollama pull <model_name>'")
                return True
    except (urllib.error.URLError, ConnectionError):
        print("❌ Ollama НЕ ОТВЕЧАЕТ на http://localhost:11434. Проверьте, что сервер запущен.")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки Ollama: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 Инициализация SDD Orchestrator Environment")
    print("=" * 50)
    
    # Предполагаем, что скрипт запускается из корня проекта, или ищем корень
    project_root = Path.cwd()
    
    all_passed = True
    
    print("\n1. Проверка глобальных правил (AGENTS.md)...")
    agents_md = project_root / ".agents" / "AGENTS.md"
    if not check_file_exists(agents_md, "AGENTS.md"):
        print("   💡 Подсказка: Создайте папку .agents и файл AGENTS.md с глобальными правилами для ИИ.")
        all_passed = False
        
    print("\n2. Проверка системной архитектуры...")
    sys_arch = project_root / ".openspec" / "system-architecture.md"
    if not check_file_exists(sys_arch, "system-architecture.md"):
        print("   💡 Подсказка: Создайте папку .openspec и опишите стек технологий в system-architecture.md до начала разработки.")
        all_passed = False
        
    print("\n3. Проверка зависимых скиллов (frontend-design)...")
    frontend_design = project_root / ".agents" / "skills" / "frontend-design" / "SKILL.md"
    if not check_file_exists(frontend_design, "Скилл frontend-design"):
        print("   💡 Подсказка: Для работы UI-Designer установите скилл (см. README.md).")
        all_passed = False
        
    print("\n4. Проверка локальных LLM (Ollama)...")
    ollama_ok = check_ollama_running()
    
    print("\n" + "=" * 50)
    if all_passed and ollama_ok:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Ваша SDD-среда готова к работе.")
        print("   Вы можете написать Оркестратору в чат: 'Спроектируй первый модуль'.")
    else:
        print("⚠️ ЕСТЬ ЗАМЕЧАНИЯ. Пожалуйста, исправьте ошибки выше перед началом работы, чтобы агенты не галлюцинировали.")
    print("=" * 50)

if __name__ == "__main__":
    main()

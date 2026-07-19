#!/usr/bin/env python3
import sys
import json
import os
import re

def parse_coverage_json(file_path):
    """
    Парсит JSON-отчет покрытия (например, от Jest или coverage.py).
    Ищет общую branch coverage.
    """
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл отчета {file_path} не найден.", file=sys.stderr)
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Пример парсинга для Jest/Istanbul JSON summary
        if "total" in data and "branches" in data["total"]:
            return data["total"]["branches"]["pct"]
            
        # Пример для python coverage.py json
        if "totals" in data:
            totals = data["totals"]
            if "num_branches" in totals and totals["num_branches"] > 0:
                covered = totals.get("covered_branches", 0)
                total = totals["num_branches"]
                return (covered / total) * 100
            elif "percent_covered" in totals:
                return totals["percent_covered"]
                
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}", file=sys.stderr)
    return None

def parse_coverage_lcov(file_path):
    """
    Парсит LCOV-отчет покрытия.
    Вычисляет покрытие ветвлений по записям BRF (Branch Found) и BRH (Branch Hit).
    """
    if not os.path.exists(file_path):
        return None
        
    brf = 0
    brh = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("BRF:"):
                    brf += int(line.split(":")[1].strip())
                elif line.startswith("BRH:"):
                    brh += int(line.split(":")[1].strip())
        if brf > 0:
            return (brh / brf) * 100
    except Exception as e:
        print(f"Ошибка парсинга LCOV: {e}", file=sys.stderr)
    return None

def main():
    if len(sys.argv) < 2:
        print("Использование: python run_coverage.py <path_to_coverage_report> [min_percentage]")
        sys.exit(1)
        
    report_path = sys.argv[1]
    min_pct = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
    
    percentage = None
    if report_path.endswith('.json'):
        percentage = parse_coverage_json(report_path)
    elif report_path.endswith('.info') or 'lcov' in report_path:
        percentage = parse_coverage_lcov(report_path)
    else:
        print(f"Ошибка: Неподдерживаемый формат отчета {report_path}", file=sys.stderr)
        sys.exit(1)
        
    if percentage is None:
        print("Не удалось определить процент покрытия ветвлений.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Текущее покрытие ветвлений (Branch Coverage): {percentage:.2f}%")
    print(f"Минимально требуемое покрытие: {min_pct}%")
    
    if percentage < min_pct:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: Покрытие ветвлений ниже лимита ({percentage:.2f}% < {min_pct}%)!", file=sys.stderr)
        sys.exit(2)
        
    print("Проверка покрытия пройдена успешно!")
    sys.exit(0)

if __name__ == "__main__":
    main()

import re
import json
from typing import List, Dict, Optional

from pydantic import ValidationError

from infrastructure.thaifriendly.models import Message, UserBrowse, UserPlay

def parse_browse(
    html_content: str,
    verbose: bool = True,
    safe_mode: bool = True
) -> Optional[List[Dict]]:
    """
    Парсит данные пользователей из JavaScript-объекта thumbdata в HTML-коде

    Параметры:
    - html_content: HTML/JS код страницы
    - verbose: Выводить отладочную информацию
    - safe_mode: Возвращать None при ошибках вместо исключения

    Возвращает:
    - Список словарей с данными пользователей или None при ошибке
    """
    try:
        # Поиск thumbdata в коде
        if verbose:
            print("Поиск thumbdata в HTML...")
            
        match = re.search(
            r'var\s+thumbdata\s*=\s*({.*?});', 
            html_content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Объект thumbdata не найден в HTML")

        # Предварительная обработка данных
        raw_data = match.group(1).strip()
        if verbose:
            print(f"Найден сырой объект ({len(raw_data)} символов):\n{raw_data[:200]}...")

        # Преобразование в валидный JSON
        fixed_json = raw_data
        
        # 1. Исправляем ключи без кавычек
        fixed_json = re.sub(
            r'([{,]\s*)(\w+)(\s*:)', 
            lambda m: f'{m.group(1)}"{m.group(2)}"{m.group(3)}', 
            fixed_json
        )
        
        # 2. Заменяем одинарные кавычки на двойные
        fixed_json = re.sub(r"(?<!\\)'", '"', fixed_json)
        
        # 3. Удаляем трейлинговые запятые
        fixed_json = re.sub(r',(\s*[}\]])', r'\1', fixed_json)
        
        # 4. Исправляем неэкранированные кавычки
        fixed_json = re.sub(r'(?<!\\)"', r'\"', fixed_json)
        
        if verbose:
            print("Исправленный JSON:")
            print(fixed_json[:300] + ("..." if len(fixed_json) > 300 else ""))

        # Парсинг JSON
        data = json.loads(fixed_json)
        
        # Проверка структуры
        if 'thumbs' not in data or not isinstance(data['thumbs'], list):
            raise ValueError("Некорректная структура thumbdata")
            
        # Нормализация данных
        thumbs = []
        for user in data['thumbs']:
            normalized = {
                'username': user.get('username'),
                'age': int(user['age']) if user.get('age') else None,
                'city': user.get('city'),
                'avatar': user.get('avatar'),
                'userid': user.get('userid'),
                'faceverified': bool(user.get('faceverified', 0)),
                'last_active': user.get('la'),
                'is_new': bool(user.get('newmember', 0)),
                'is_popular': bool(user.get('ispop', 0)),
                'is_online': 'offline' not in user or not user['offline']
            }
            thumbs.append(normalized)

        if verbose:
            print(f"Успешно распаршено {len(thumbs)} пользователей")

        return [UserBrowse.model_validate(user) for user in thumbs]

    except Exception as e:
        if verbose:
            print(f"Ошибка парсинга: {str(e)}")
        if not safe_mode:
            raise
        return None
    
import json
from typing import List, Dict, Optional

def parse_play(
    json_data: str,
    verbose: bool = False,
    safe_mode: bool = True
) -> Optional[List[Dict]]:
    try:
        data = json.loads(json_data)
        
        if 'results' not in data:
            raise ValueError("Некорректная структура данных: отсутствует 'results'")
            
        users = []
        for user_data in data['results']:
            if not isinstance(user_data, dict):
                continue
                
            normalized = {
                'username': user_data.get('name'),
                'userid': user_data.get('id'),
                'age': int(user_data.get('age', None)),
                'city': user_data.get('city'),
                'gender': user_data.get('bg', 'unknown'),
            }
            
            users.append(normalized)
        return [UserPlay.model_validate(user) for user in users]


    except Exception as e:
        if verbose:
            print(f"Ошибка парсинга: {str(e)}")
        if not safe_mode:
            raise
        return None

# Abistep API

**Установка зависимостей:**
   ```bash
   pip install -r requirements.txt
   ```

**Разработка (с автоперезагрузкой)**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Продакшн**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

После запуска API будет доступен по адресу: http://localhost:8000

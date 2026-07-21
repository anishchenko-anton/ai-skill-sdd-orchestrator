# Security Code Review Checklist

Оркестратор ОБЯЗАН проверить каждый пункт перед принятием кода:

- [ ] JWT secret берётся из `process.env`, а не захардкожен
- [ ] `.env` файлы в `.gitignore`
- [ ] CORS настроен с конкретными origins (не `enableCors()` без параметров)
- [ ] ValidationPipe подключен глобально в `main.ts`
- [ ] Пароли хешируются (bcrypt), а не хранятся в открытом виде
- [ ] Нет `console.log` с чувствительными данными
- [ ] HTTP Interceptor использует `req.clone()` (Angular)
- [ ] API URL берётся из `environment.ts`, а не хардкодом

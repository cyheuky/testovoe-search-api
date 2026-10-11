# Тестовое задание. API поисковика по текстам документов

Микросервис для поиска по текстам документов. Проект использует PostgreSQL в качестве основного хранилища и Elasticsearch для быстрого полнотекстового поиска.

## Стек технологий
*   **Backend:** FastAPI, Python 3.11
*   **Базы данных:** PostgreSQL (asyncpg, SQLAlchemy), Elasticsearch (async)
*   **Инфраструктура:** Docker, Docker Compose
*   **Тестирование:** Pytest, httpx

## Гайд по поднятию

1. Убедитесь, что у вас установлен Docker и Docker Compose.
2. Поместите файл с исходными данными `posts.csv` в корневую директорию проекта.
3. Запустите проект командой:
   ```bash
   docker compose up --build -d
4. Выполните скрипт первичной загрузки данных из CSV в PostgreSQL и Elasticsearch:
   ```bash
   docker compose exec web python -m app.parser
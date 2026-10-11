import os
from elasticsearch import AsyncElasticsearch
from dotenv import load_dotenv

load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200").strip("\"'")
INDEX_NAME = "documents_index"

es_client = AsyncElasticsearch(ELASTIC_URL)


async def create_index():
    try:
        await es_client.info()
        print("Успешное подключение к Elasticsearch!")
    except Exception as e:
        print(f"Не удалось подключиться к Elasticsearch: {e}")
        return

    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "text": {
                    "type": "text",
                    "analyzer": "russian"
                }
            }
        }
    }

    try:
        await es_client.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Индекс '{INDEX_NAME}' успешно создан.")
    except Exception as e:
        # Если ошибка связана с тем, что индекс уже есть, это нормально
        if "resource_already_exists_exception" in str(e):
            print(f"Индекс '{INDEX_NAME}' уже существует, пропускаем создание.")
        else:
            print(f"Произошла ошибка при создании индекса: {e}")
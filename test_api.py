import pytest
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_search_documents():
    """Проверяем, что поиск возвращает до 20 документов и они отсортированы по дате."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/search", params={"q": "система"})

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 20, "Эндпоинт вернул больше 20 документов!"

    if len(data) > 1:
        dates = [datetime.fromisoformat(doc["created_date"]) for doc in data]
        assert dates == sorted(dates, reverse=True), "Документы не отсортированы по убыванию даты!"


@pytest.mark.asyncio
async def test_delete_document():
    """Проверяем успешное удаление существующего документа и ответ 404 для несуществующего."""
    async with httpx.AsyncClient() as client:
        search_res = await client.get(f"{BASE_URL}/search", params={"q": "система"})
        docs = search_res.json()

        if not docs:
            pytest.skip("Нет документов для теста удаления")

        doc_id = docs[0]["id"]

        del_res = await client.delete(f"{BASE_URL}/documents/{doc_id}")
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "success"

        del_again_res = await client.delete(f"{BASE_URL}/documents/{doc_id}")
        assert del_again_res.status_code == 404
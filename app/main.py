from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse
from app.elastic import es_client, INDEX_NAME

app = FastAPI(
    title="Search Service API",
    description="Микросервис для поиска документов",
    version="1.0.0"
)


@app.on_event("shutdown")
async def shutdown_event():
    """Закрываем соединение с Elasticsearch при остановке приложения."""
    await es_client.close()


@app.get("/search", response_model=List[DocumentResponse])
async def search_documents(
        q: str = Query(..., description="Текстовый запрос для поиска"),
        db: AsyncSession = Depends(get_db)
):
    """
    Поиск документов по тексту.
    Возвращает до 20 документов, отсортированных по дате создания.
    """
    es_response = await es_client.search(
        index=INDEX_NAME,
        query={
            "match": {
                "text": q
            }
        },
        size=10000
    )

    hits = es_response.get("hits", {}).get("hits", [])
    if not hits:
        return []

    doc_ids = [int(hit["_source"]["id"]) for hit in hits]

    stmt = (
        select(Document)
        .where(Document.id.in_(doc_ids))
        .order_by(Document.created_date.desc())
        .limit(20)
    )

    result = await db.execute(stmt)
    documents = result.scalars().all()

    return documents


@app.delete("/documents/{doc_id}")
async def delete_document(
        doc_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Удаляет документ из PostgreSQL и индекса Elasticsearch.
    """
    stmt = delete(Document).where(Document.id == doc_id)
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Документ не найден")

    try:
        await es_client.options(ignore_status=404).delete(index=INDEX_NAME, id=str(doc_id))
    except Exception as e:
        print(f"Ошибка удаления из ES: {e}")

    return {"status": "success", "message": f"Документ {doc_id} удален"}
import asyncio
import pandas as pd
import ast
from app.database import engine, Base, AsyncSessionLocal
from app.models import Document
from app.elastic import es_client, create_index, INDEX_NAME


async def init_db():
    """Создает таблицы в PostgreSQL."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def parse_and_load_csv(file_path: str):
    """Читает CSV и заливает данные в PostgreSQL и Elasticsearch."""
    df = pd.read_csv(file_path, encoding='utf-8')

    df['created_date'] = pd.to_datetime(df['created_date'])

    async with AsyncSessionLocal() as session:
        for index, row in df.iterrows():
            rubrics_raw = row['rubrics']
            if isinstance(rubrics_raw, str):
                try:
                    rubrics = ast.literal_eval(rubrics_raw)
                except:
                    rubrics = [r.strip() for r in rubrics_raw.split(',')]
            else:
                rubrics = rubrics_raw

            db_doc = Document(
                rubrics=rubrics,
                text=row['text'],
                created_date=row['created_date']
            )
            session.add(db_doc)
            await session.commit()
            await session.refresh(db_doc)

            doc_es = {
                "id": db_doc.id,
                "text": db_doc.text
            }
            await es_client.index(index=INDEX_NAME, id=str(db_doc.id), document=doc_es)

        print(f"Успешно загружено {len(df)} записей в БД и Elastic.")


async def main():
    print("Инициализация таблиц БД...")
    await init_db()

    print("Инициализация индекса Elasticsearch...")
    await create_index()

    print("Чтение и загрузка данных из posts.csv...")
    await parse_and_load_csv("posts.csv")

    await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())
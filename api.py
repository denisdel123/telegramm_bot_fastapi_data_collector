from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
import models
import constants
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

app = FastAPI()

user_db = constants.POSTGRES_USER
localhost_db = constants.POSTGRES_PORT
name_db = constants.POSTGRES_BD
password_db = constants.POSTGRES_PASSWORD

# конфигурация базы данных
DATABASE_URL = f"postgresql+asyncpg://{user_db}:{password_db}@localhost:{localhost_db}/{name_db}"

# создание движка
engin = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(bind=engin, expire_on_commit=False)


@app.post("/api/v1/products")
async def get_product(data: models.ProductRequest, db: AsyncSession = Depends(SessionLocal)):
    article = data.article

    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={article}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Продукты не найден на Wildberries.")

    product_data = response.json()

    try:
        product_info = product_data["data"]["products"][0]  # Извлекаем данные о товаре
        name = product_info["name"]
        price = product_info["salePriceU"] / 100  # Цена в копейках, переводим в рубли
        rating = product_info.get("rating", 0)
        quantity = sum(stock["qty"] for stock in product_info["sizes"])  # Кол-во на складах
    except (KeyError, IndexError) as e:
        raise HTTPException(status_code=500, detail="Invalid response structure from Wildberries")

    async with db as session:
        # Проверяем, существует ли уже запись
        existing_product = await session.execute(
            models.Product.__table__.select().where(models.Product.article == article)
        )
        if existing_product.scalar():
            # Обновляем запись
            await session.execute(
                models.Product.__table__.update()
                .where(models.Product.article == article)
                .values(
                    name=name,
                    price=price,
                    rating=rating,
                    quantity=quantity,
                    updated_at=datetime.utcnow().isoformat(),
                )
            )
        else:
            # Создаём новую запись
            new_product = models.Product(
                artikul=article,
                name=name,
                price=price,
                rating=rating,
                quantity=quantity,
            )
            session.add(new_product)

        await session.commit()

    return {
        "article": article,
        "name": name,
        "price": price,
        "rating": rating,
        "quantity": quantity,
    }
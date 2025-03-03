from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List
import subprocess
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI приложение
app = FastAPI()


class Flat(BaseModel):
    title: str
    price: str
    address: str
    link: str

@app.get("/test")
def test():
    return {"message": "FastAPI работает!"}

@app.get("/parse")
def parse(url: str = Query(..., description="URL для парсинга")):
    try:
        result = subprocess.run(
            ["python", "Parser.py", url],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Ошибка парсера: {result.stderr}")
            raise HTTPException(status_code=500, detail="Ошибка при выполнении парсера")

        return {"message": "Парсинг завершен и данные сохранены в базу данных"}

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flats", response_model=List[Flat])
def get_flats():
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host="localhost",
            user="localuser",
            password="",
            database="flats_db"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT title, price, address, link FROM flats")
        flats = cursor.fetchall()
        return flats
    except Exception as e:
        logger.error(f"Ошибка при получении данных: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

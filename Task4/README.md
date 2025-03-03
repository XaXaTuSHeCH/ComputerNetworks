Вот так, да, БД запускаю, дон:
```
mysql -u localuser -h localhost flats_db
```
Вот так потом, да, API точку стартую, дон:
```
uvicorn APIspot:app --reload
```
Дальше, да, тестируешь, что работает, дон:
```
curl http://127.0.0.1:8000/test 
```
Потом, парсер пускаешь, дон:
```
curl http://127.0.0.1:8000/parse\?url\=https://novosibirsk.cian.ru
```
Или так, да, чтобы ? и = не экранировать, дон:
```
curl "http://127.0.0.1:8000/parse?url=https://novosibirsk.cian.ru"
```
И на десерт, да, JSON типа себе выводишь, дон:
```
curl http://127.0.0.1:8000/flats 
```
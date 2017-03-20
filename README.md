# async_test_task
Create database for project:

```
sudo -u postgres psql -c "CREATE USER async_test WITH PASSWORD 'async_test';" \
                         "CREATE DATABASE async_test ENCODING 'UTF8';" \
                         "GRANT ALL PRIVILEGES ON DATABASE async_test TO async_test;"
```
Run application:
```
python main.py
```

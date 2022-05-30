## Reading list app backend
Search books via google books api and add them to your bookshelves synchronized with google library


* Fastapi
* Mongodb + motor
* Redis + aioredis
* JWT auth
* Google oauth and books api

Demo http://my-books-history.herokuapp.com/docs

## Run
```bash
# Install the requirements:
$ pip install -r requirements.txt

# Configure variables
$ cp .env.dist .env
$ vim .env
# or 
$ nano .env

# Start the service:
$ uvicorn app:app --reload
```

import motor.motor_asyncio

from config import MONGODB_URL

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.MyBooksHistory

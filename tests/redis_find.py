import sys
import os
sys.path.append(f'{os.path.dirname(__file__)}/../')
from botcore.bot_redis import RedisVectorDB

redis_db = RedisVectorDB()

data = {"title": "I have an old phone", "features": ["My phone has 4 GB RAM", "Is it function well? Well"]}
b = redis_db.search_wanted(data)
print(b)

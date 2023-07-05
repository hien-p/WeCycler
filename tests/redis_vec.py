import sys
import os
sys.path.append(f'{os.path.dirname(__file__)}/../')
from botcore.bot_redis import RedisVectorDB
from botcore.test_data import TEST_WANTED_DATA 

redis_db = RedisVectorDB()
data = TEST_WANTED_DATA

[redis_db.add_new_wanted(a) for a in data]

# after user input

data = {"title": "I have an old phone", "features": ["My laptop has 4 GB RAM", "Is it function well? Well"]}

b = redis_db.search_wanted(data)
print(b)

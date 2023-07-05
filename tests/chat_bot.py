import sys
import os
sys.path.append(f'{os.path.dirname(__file__)}/../')

from botcore.chains.bot_chat_chain import build_bot_chat_chain
from botcore.utils.memory_utils import QAMemory
from botcore.setup import trace_ai21

data = {
  "title": "Old phone",
  "features": [
    "What is the screen size? 2.8 inches",
    "What is the RAM size? 512 MB",
    "What is the storage capacity? 4 GB",
    "What is the battery capacity? 1500 mAh",
    "Is there any malfunction or defect? yes",
    "What is the current physical condition of the product? excellent",
    "Is the product still under warranty? yes"
  ]
}

model = trace_ai21(max_tokens=1000)

qa_memory = QAMemory('question')
qa_memory.import_qa(data)

chain = build_bot_chat_chain(model, qa_memory.memory)
ans = chain.run("Give me some recycling advice")
print(ans)

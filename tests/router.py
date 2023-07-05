import sys
import os
sys.path.append(f'{os.path.dirname(__file__)}/../')
from botcore.utils.json_parser import parse_nested_json
from botcore.utils.memory_utils import QAMemory
from botcore.setup import get_ai21_model, enable_tracing

MODEL = get_ai21_model(max_tokens = 400)
enable_tracing("assess")

## LOAD TO MEMORY

SAMPLE = '\n\n```\n[\n  {\n    "question": "Has the washing machine ever broken down?",\n    "options": [\n      "yes",\n      "no"\n    ]\n  },\n  {\n    "question": "What is the current physical condition of the washing machine?",\n    "options": [\n      "excellent",\n      "good",\n      "fair",\n      "poor"\n    ]\n  },\n  {\n    "question": "Does the washing machine have a warranty?",\n    "options": [\n      "yes",\n      "no"\n    ]\n  },\n  {\n    "question": "If the washing machine has a warranty, what is the warranty period?",\n    "options": [\n      "1 year",\n      "2 years",\n      "3 years",\n      "4 years",\n      "5 years"\n    ]\n  }\n]\n\n```'
DATA = parse_nested_json(SAMPLE)
# print(SAMPLE)
product = "washing machine"
ques = [e['question'] for e in DATA]
ans = [e['options'][0] for e in DATA]

bot_memory = QAMemory("question")
bot_memory.load_all(product, ques, ans)

## BUILD ROUTER

from botcore.routing.chat_route import ProductChatRouter

router = ProductChatRouter(MODEL,bot_memory)
router.build_router()

ans = router.chain({"input": "Please give a list of pros and cons."})
print(ans)


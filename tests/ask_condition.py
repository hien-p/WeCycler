import sys
import os
sys.path.append(f'{os.path.dirname(__file__)}/../')
from botcore.setup import trace_ai21
from botcore.chains.qa_condition import build_ask_condition_chain
from botcore.utils.json_parser import parse_nested_json

MODEL = trace_ai21()

chain = build_ask_condition_chain(MODEL)
print("Chain built")

ans = chain({"product": "laptop", "n_top": 4})
data = parse_nested_json(ans['result'])
print(data)

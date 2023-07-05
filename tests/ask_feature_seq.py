
import sys
import os
sys.path.append(f'{os.path.dirname(__file__)}/../')
from botcore.setup import trace_ai21, trace_openai
from botcore.chains.ask_feature import build_ask_feature_chain
from botcore.chains.generate_answer import build_generate_answer_chain
from botcore.utils.json_parser import parse_nested_json

MODEL = trace_ai21('ask_demo')

chain = build_ask_feature_chain(MODEL)
ans_chain = build_generate_answer_chain(MODEL)

product = "water bottles"
n = 3

questions = chain({"product": product, "n_top": n})
ques = parse_nested_json(questions['result'])
print("Questions:", ques)


for q in ques:
    ans = ans_chain({"product": product, "question": n})
    data = parse_nested_json(ans['result'])
    ## pass {question: answer} to UI
    print(data)

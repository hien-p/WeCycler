GENERATE_ANSWER_CONST = \
{"inputs":["product", "question"],
 "outputs": {"options": """a js array of possible answers for the question. The array's length should be greater than 5."""},
"template": """You are interesting in a {product}.
Given a question about a {product} delimited by triple backquotes.
```
{question}
```
{format_instructions}
Choices:"""}


from langchain.llms import BaseLLM
from langchain import LLMChain
import sys
import os
sys.path.append(f"{os.path.dirname(__file__)}/../..")
from botcore.utils.prompt_utils import build_prompt

def build_generate_answer_chain(model: BaseLLM):
    inputs = GENERATE_ANSWER_CONST['inputs']
    outputs = GENERATE_ANSWER_CONST['outputs']
    template = GENERATE_ANSWER_CONST['template']
    prompt = build_prompt(inputs, outputs, template, include_parser=True)
    chain = LLMChain(llm=model, prompt=prompt, output_key='result')
    return chain

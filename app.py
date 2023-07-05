import streamlit as st
from streamlit_chat import message  
import sys 
import os 
import json
from streamlit_option_menu import option_menu
import re
import html


sys.path.append(f'{os.path.dirname(__file__)}/../')
from botcore.chains.qa_feature import build_ask_feature_chain
from botcore.chains.qa_condition import build_ask_condition_chain
from botcore.utils.json_parser import parse_nested_json
from botcore.setup import trace_ai21

from src.components.format_message import *
from botcore.setup import get_ai21_model, enable_tracing
from botcore.bot_redis import connect_redis
from botcore.routing.explore_route import FeatureExplorer


# botchat
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts import PromptTemplate
from botcore.bot_agent import AgentBot
from botcore.utils.memory_utils import QAMemory

# redis
from botcore.bot_redis import RedisVectorDB
from botcore.test_data import TEST_WANTED_DATA 


st.set_page_config(
        page_title="Wecycler",
        page_icon="🌳",
    )

hide_hamburger()
set_bg_hack_url()
selected_options = option_menu(None, ["📝Analytics",  "💬chat Bot"], 
    icons=['📝', '🔎'], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#a5e69f"},
        "icon": {"color": "#76b31d", "font-size": "25px"}, 
        "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#76b31d"},
        "nav-link-selected": {"background-color": "#1fc724"},
    
    }
)


def chat(input_user, nums):
    MODEL = get_ai21_model(max_tokens = 400)
    enable_tracing("ask_demo")

    db = connect_redis()
    explorer = FeatureExplorer(MODEL, db)
    feat, cond = explorer.ask_user(input_user, nums)
    
    
    
    try:
        result = feat['questions']
        result.extend(cond['questions'])
    except:
        result = feat['questions']
        
    return result



if "user_text" not in st.session_state:
    st.session_state.user_text = ""
if "past" not in st.session_state:
    st.session_state.past = []
if "boxselect" not in st.session_state:
    st.session_state.boxselect = {}

if "question" not in st.session_state:
    st.session_state.question = 3    
    
if "number_quantity" not in st.session_state:
    st.session_state.number_quantity = 1

if "nums_Q" not in st.session_state:
     st.session_state.nums_Q = 1


if selected_options == '📝Analytics':
    with open("src/components/UI/test.md", "r") as sidebar_file:
        sidebar_content = sidebar_file.read()    
    st.sidebar.markdown(sidebar_content)
    
    
    st.session_state.user_text = st.text_input("Type your message", key="user_input")

    col_number, col_qua = st.columns(2)
    
    with col_number:
        nums_Q = st.number_input("Number of question",1, 10, 1)
        if nums_Q > 2:
            st.session_state.nums_Q  = nums_Q
    with col_qua:
        number_qua = st.number_input('Trash Quantity:',min_value=1,step=1)

        if number_qua > 1: 
            st.session_state.number_quantity = number_qua
        
        
    button_1 = st.button("Submit") 
    if st.session_state.get('button') != True:
        st.session_state['button'] = button_1    

    if st.session_state['button'] == True:
        with st.spinner('Wait for it...'):
            st.session_state.past.append(st.session_state.user_text)
            message(st.session_state.user_text,is_user=True, key=str("hello") + "_user",avatar_style="adventurer", # change this for different user icon
                seed=123,)

            data = chat(str(st.session_state.user_text),  st.session_state.nums_Q)
            #data = parse_nested_json(response['result'])

        # Routing class 
        
        if data:
            st.balloons()
            message("Let's learn more about your products. Please answer the following questions: ")
            list_answer = {}
            metadata_feature, metadata_conditions = [], []
            #number = st.number_input('Trash Quantity:',min_value=1,step=1)
            
            with st.form(key='my_form'):
                message(f"Features:{st.session_state.nums_Q} + Conditions: {st.session_state.nums_Q} ")
                for i, item in enumerate(data): 
                    if item['question'] not in st.session_state.boxselect:
                        st.session_state.boxselect[item['question']] = ""

                    st.session_state.boxselect[item['question']] = st.selectbox(
                        item['question'],
                        tuple(item['options']),
                        index=item['options'].index(st.session_state.boxselect[item['question']]) if st.session_state.boxselect[item['question']] in item['options'] else 0,
                        key=f"{item['question']}"
                    )    
                    metadata_feature.append(str(item['question'])+ " " + str(st.session_state.boxselect[item['question']]))
                
                list_answer['title'] = st.session_state.user_text
                list_answer['features'] = metadata_feature
                
                #list_answer['Quantity'] = st.session_state.number_quantity
                if st.form_submit_button('Confirm Responses'):
                    with st.spinner('I loading...'):
                        redis_db = RedisVectorDB()
                        data = TEST_WANTED_DATA
                        [redis_db.add_new_wanted(a) for a in data]
                        
                        st.write(list_answer)
                        b = redis_db.search_wanted(data)
                    st.write(b)
                    st.session_state['button'] = False


INITIAL_MESSAGE = [
    {"role": "user", "content": "Hi!"},
    {
        "role": "assistant",
        "content": "Hi there! I'm your Recycling Assistant, designed to help manage and understand your recycling needs. I can provide insights into your waste, help update your recycling preferences, connect you with matching recycling agents, and customize settings to suit your requirements. Let's start recycling smarter together!",
    },
]

def conservationBot(data, inputuser):
    MODEL = trace_ai21()
    TEMPLATE = """ 
    You are Wecycler, an AI-powered recycling chatbot. You specialize in providing insights about the environment, recycling processes, and the value of secondhand products. You excel at answering a variety of questions in these areas based on previous interactions.
    Chat history: {chat_history}
    Given the question: {question}
    Please, as Wecycler, provide your most informative and helpful response. 
    Be sure to refer to the user's items as 'your product' when providing details or assessments"""
        
    ques = [i.split("?")[0] for i in data['features']]
    ans = [i.split("?")[1] for i in data['features']]
    qa_mem = QAMemory('question')
    qa_mem.load_all(data['title'], ques, ans)
    
    prompt = PromptTemplate(input_variables=["question","chat_history"], template=TEMPLATE)
    chain = LLMChain(llm=MODEL, prompt=prompt, memory=qa_mem.memory)

    ans = chain.run(str(inputuser))
    
    return ans 
def append_chat_history(question, answer):
    st.session_state["history"].append((question, answer))

def append_message(content, role="assistant", display=False):
    message = {"role": role, "content": content}
    message_func(content, False, display)
    st.session_state.messages.append(message)
    if role != "data":
        append_chat_history(st.session_state.messages[-2]["content"], content)

if selected_options == '💬chat Bot':
    
    col1, col2 = st.columns((4, 1)) 
    styles_content = """
    <style> #input-container { position: fixed; bottom: 0; width: 100%; padding: 10px; background-color: white; z-index: 100; } h1 { font-family: 'Roboto Slab', serif; } .user-avatar { float: right; width: 40px; height: 40px; margin-left: 5px; margin-bottom: -10px; border-radius: 50%; object-fit: cover; } .bot-avatar { float: left; width: 40px; height: 40px; margin-right: 5px; border-radius: 50%; object-fit: cover; } </style>    
    """
    st.write(styles_content, unsafe_allow_html=True)
    
    
    # Initialize the chat messages history
    if "messages" not in st.session_state.keys():
        st.session_state["messages"] = INITIAL_MESSAGE

    if "history" not in st.session_state:
        st.session_state["history"] = []
    
    if "res" not in st.session_state:
        st.session_state["res"] = ""
        
        
    with col1:
        datas = {
        
        "title": "I have a phone",
        "features": [
            "What is the screen size? 5.5 inches",
            "What is the screen resolution? 1920x1080 pixels",
            "What is the RAM size? 2 GB",
            "What is the storage capacity? 16 GB",
            "Is there any malfunction or defect? yes",
            "What is the current physical condition of the product? poor",
            "Is there any warranty for this product? no"
        ]
    }
    
        
        if prompt := st.text_input(""):
            with st.spinner(text="Loading"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                res =   conservationBot(datas, prompt)
                if res: 
                    st.session_state["res"] = res
                    


    with col2: 
        customize_button()
        if st.button("Reset Chat"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.session_state["messages"] = INITIAL_MESSAGE
            st.session_state["history"] = []
        
    for message in st.session_state.messages:
        message_func(
            message["content"],
            True if message["role"] == "user" else False,
            True if message["role"] == "data" else False,
        )
        
    
    if st.session_state.messages[-1]["role"] != "assistant":
        content = st.session_state.messages[-1]["content"]
        if isinstance(content, str):
            result = st.session_state["res"]
            append_message(result)
        

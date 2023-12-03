import streamlit as st
import chromadb
import pprint
import google.generativeai as palm
import os
from utils import *
from dotenv import load_dotenv
load_dotenv()


custom_llm_server_token = os.getenv('local_codellm_fastapi_server_url')

if "messages" not in st.session_state:
    st.session_state.messages = []

if "complete_1" not in st.session_state:
    st.session_state.complete_1 = False

if "token" not in st.session_state:
    st.session_state.token = False

with st.sidebar:
    st.title("PyGen CodeLLM")
    st.write("Python program generator based on data from csv")
with st.form(key ='Form1'):
    with st.sidebar:
        st.session_state.token = st.text_input("Auth Token", type="password", placeholder="Enter your API token")
        st.session_state.csv = st.file_uploader("Upload csv file", type="csv")
        st.session_state.dd_text = st.file_uploader("Upload Data Dictionary", type="txt")
        submitted1 = st.form_submit_button(label = 'Submit and Index')
        
        if submitted1:
            if len(st.session_state.token) > 900: #and st.session_state.csv != None and st.session_state.dd_text != None:
                #Index into chroma vector db
                #
                #
                st.session_state.complete_1 = True
            else:
                st.session_state.complete_1 = False
            

# Chat Like stramlit interface where user can ask question
if st.session_state.complete_1 == True:
    
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = interact_code_llm(text = prompt, 
                                token = st.session_state.token, 
                                custom_llm_server_token = custom_llm_server_token)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
else:
    st.warning("Please upload csv and data dictionary")
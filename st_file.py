import streamlit as st
import chromadb
import os
from dotenv import load_dotenv
load_dotenv()


st.session_state.complete_1 = False
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
            if len(st.session_state.token) > 900 and st.session_state.csv != None and st.session_state.dd_text != None:
                #Index into chroma vector db
                #
                #
                st.session_state.complete_1 = True
            else:
                st.session_state.complete_1 = False
            

# Chat Like stramlit interface where user can ask question
if st.session_state.complete_1 == True:
    
    with st.chat_message("user"):
        
        st.write("Hello 👋")
else:
    st.warning("Please upload csv and data dictionary")
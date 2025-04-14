import streamlit as st
import os

def clear_chat_history():
    st.session_state.chat_history = []

def sidebar():
    with st.sidebar:
        
        st.markdown(
            "## Example use cases\n"
            "1. How can I contact the professor?\n" 
            "2. How to create a new SQLite database?\n"
            "3. How to create a table with proper data types? \n"
            "4. How to write a basic SELECT query? \n"
            "5. How to join two tables together?\n"
        )
        # st.markdown("---")
        st.markdown(
            "## General advice\n"
            "1. Specify if you're using SQLite CLI or another interface.\n" 
            "2. Include your table structure when asking about queries.\n"
            "3. For JOIN questions, describe the relationship between tables.\n"
        )
        st.markdown("---")
        st.markdown("# About")
        st.markdown(
            '''📖 Virtual TA helps with SQLite basics including:
            - Database and table creation
            - Basic SELECT queries
            - Table joins
            - SQLite CLI commands'''
        )
        st.markdown(
            "This tool is a work in progress. "
        )
        st.markdown("Made by Dr.Wenjun Gu (wenjun.gu@emory.edu)")
       

        # api_key_input = st.text_input(
        #     "OpenAI API Key",
        #     type="password",
        #     placeholder="Paste your OpenAI API key here (sk-...)",
        #     help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
        #     value=os.environ.get("OPENAI_API_KEY", None)
        #     or st.session_state.get("OPENAI_API_KEY", ""),
        # )

        # user_name = st.text_input(
        #     "Enter your name ",
        #     # type="password",
        #     placeholder="Your prefered name here...",
        #     help="This information will be deleted after each session",  # noqa: E501
        #     value='ISOM 352 Coder',
        # )

        # st.session_state["user_name"] = user_name

#         st.markdown("---")


#         st.markdown(
#         """
# # FAQ
# ## Best practice for interacting with virtual TA?
# Your query should provide as much information as possible to help identify the correct knowledge.  
# """
#         )

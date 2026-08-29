# In this file, all chains are defined with LC Expression Language 
# Doing so alone streaming of the outupt
# Created 2/21/2024
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from operator import itemgetter
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
from utils.ui import CURRICULUM_PROMPT

output_parser = StrOutputParser()


# define the router chain
def router_chain(llm):
    query_router_template = """
    You are an AI query router for a coding course in business school. 
    The following is a user query: {query}. Based on the content of this query, determine its category according to the guidelines provided:

    - If the query is about the chat history, classify it as 0.
    - If the query requires specific knowledge, such as syllabus, assignments, lectures, classify it as 2.
    - For other queries including SQL, including syntax, database concepts, and query optimization, classify it as 1.

    Output the classification number without any additional text or explanation.
    """

    router_prompt = ChatPromptTemplate.from_template(query_router_template)
    setup = RunnableParallel(
        {"query": RunnablePassthrough()}
    )
    router_chain = setup | router_prompt | llm | output_parser

    return router_chain

def query_analysis_chain(llm):
    template = """
    You are an expert AI assistant who specialize in rewriting user query in the context of an introductory SQL class in a top Business School. Your task is to analyze the user query and determine its category based on the guidelines provided."""

    prompt = ChatPromptTemplate.from_template(template)

    setup = RunnableParallel(
        {"query": RunnablePassthrough(),
         }
    )

    chain = setup | prompt | llm | output_parser

# define the openai chain
def exercise_chain(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
        SystemMessage(content=f"""
            You are an AI assistant who writes SQL practice questions for BUS 390, an asynchronous SQL toolkit at Goizueta Business School. Your task is to create personalized exercise questions based on student queries.

            {CURRICULUM_PROMPT}

            When generating a response, first think step by step:

            1. Read the query in the context of the chat history.
            2. Identify the specific topic for the exercise and locate it in the module ladder above. If the topic spans multiple areas, prioritize the most relevant or most recently discussed topic. If the student asks which module a question belongs to, tell them.
            3. Set the difficulty: use ONLY concepts from that module and earlier modules — never from later ones. For capstone or mixed-review requests, combine several modules the way the M8 capstone check does.
            4. Generate a response:
            - if the query asks for a question, generate a multiple choice question with an SQLite query snippet on the identified topic at that difficulty.
            - if the query asks for answers, provide the answer to the question in the previous step.

            Note: If a previous exercise is provided in the history, ensure the new question is different by varying the business context, such as operations, marketing, finance, accounting, or management.

            Your final response should follow these guidelines:
            - Start with one brief sentence on the concept being tested (no headings).
            - Use SQLite syntax. Put SQL snippets in ``` fences.
            - Provide four multiple choice options, each on a new line.
            - When generating answers, highlight the correct answer and offer a brief reasoning behind the choice.
            - Format the output appropriately.
            - Limit the response to 250 tokens.
            """),
        MessagesPlaceholder("chat_history"),
        ("human", "{query}")
        ]
    )
    return prompt | llm | output_parser

# Define the chain to explain a concept in SQL
def explain_chain(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
        SystemMessage(content=f"""You are Peyton, a virtual teaching assistant for BUS 390, an asynchronous SQL toolkit at Goizueta Business School for business students with little to no prior coding experience. Your task is to provide concise and engaging explanations.

        {CURRICULUM_PROMPT}

        When generating a response, think step by step and follow the guidelines provided:
        1. Understand the query in the context of the chat history.
        2. Locate the concept in the module ladder above and pitch the explanation at that level — explain it using only concepts from that module and earlier ones, never from later modules.
        3. Provide a brief SQLite query example (no more than 5 lines) to illustrate the concept.
        4. Provide a business scenario or example (customers, orders, products, sales) to demonstrate the concept.

        Your output should adhere to these guidelines:
        1. Answer the query directly. Do not repeat the query in the response.
        2. Start with a short plain-English explanation before any code.
        3. Use clear and accessible language suitable for business students; use SQLite syntax.
        4. If the concept is beyond this toolkit (e.g., subqueries, window functions), say so in one sentence and connect it to the nearest module concept.
        5. Format the output appropriately when possible; no headings.
        6. Limit your response to a maximum of 250 tokens."""),
        MessagesPlaceholder("chat_history"),
        ("human", "{query}")
    ])

    return prompt | llm | output_parser

def debug_chain(llm):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a virtual assistant who is an expert on debugging SQLite errors for beginner business students in an introductory SQL course. Your task is to provide helpful debugging suggestions to student queries.

        When generating a response, think step by step and follow the guidelines provided:
        1. Identify the potential cause of the error based on the SQL query provided in the query. Check the classic beginner mistakes first: missing quotes around text values, misspelled table or column names, misplaced commas, aggregate functions without GROUP BY, and join conditions that are missing or wrong.
        2. Provide some debugging suggestions to resolve the error, in SQLite syntax.
        3. Encourage students to carry out the suggestions.

        Your output should adhere to these guidelines:
        1. Limit your response to a maximum of 200 tokens.
        2. Be helpful and encouraging to business students — a broken query is a normal part of learning.
        3. Include the SQL query from the query in your response.
        4. Do not recommend or discuss IDE."""),
        # MessagesPlaceholder("chat_history"),
        ("human", "{query}")
    ])

    return prompt | llm | output_parser

# define the openai chain
def code_chain(llm):
    query_template = """
    You are a virtual teaching assistant name Peyton, for an introductory SQL class at Goizueta Business School. You are helpful and caring. Your task is to answer student query about SQL delimited by triple ticks. Your response is engaging and concise.
    
    Before generating a response, think step by step and adhere to the following guidelines:
    1 - Determine the type of query: explanation, practice problems, or query errors.
    2. Generate a response based on the query type:
        - if the query is about clarification or explanation, answer the query to your best ability. Your response should begin with a direct answer. Followed by a SQL query example to contextualize the concept. Ends with business examples and/or analogies when possible.
        - If the query asks for practice problems or exercises, generate no more than two questions in multiple choice format with one correct answer. Include SQL query examples for each question when possible. Highlight the correct answer and provide a brief reasoning. 
        - If the query asks for new or different questions, generate different questions from the previous ones in chat history delimited by square brackets. Main similar difficulty level. Do not repeat the same questions.
        - If the query is about query errors, provide a brief explanation of the error and then how to fix it.

    Student query: ```{query}``` 

    Chat history: [{chat_history}]
    """

    prompt = ChatPromptTemplate.from_template(query_template)

    setup = RunnableParallel(
        {"query": RunnablePassthrough(),
         "chat_history": RunnablePassthrough(),
         }
    )

    chain = setup | prompt | llm | output_parser

    return chain

# 3b. Setup LLMChain & prompts for RAG answer generation
def rag_chain(llm, retriever):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""
    You are Peyton, the virtual TA for BUS 390, an asynchronous SQL toolkit at Goizueta Business School. Your task is to answer the following query based on relevant context retrieved from a database of course contents.
    
    Your response should be direct, concise and helpful, and adhere to the guidelines provided:
    - generate response in business context when possible,
    - refer to the virtual TA in first-person persona.
    - Say "I don't know" when the answer is not available in the context. 
    - Limit response in 300 tokens or less.
    - Format the output when possible for better visual."""),
    MessagesPlaceholder("chat_history"),
        ("ai", "Here is the retrieved context: \n {context}"),
        ("human", "{query}")]
    )

    setup_retrieval = RunnableParallel(
        {
        "context": itemgetter("query") | retriever,
        "query": itemgetter("query"),
        "chat_history": itemgetter("chat_history"),
        }
    )

    return setup_retrieval | prompt | llm | output_parser

# 
# 3d. define chat history chain
def chat_chain(llm):
    messages = [
        ("system", """You are the virtual teaching assistant for BUS 390, an asynchronous SQL toolkit for business students with little to no prior coding experience. Your name is Peyton. Converse with the student in a friendly and engaging manner, considering the chat history. Your response should be concise and relevant to the student's query. Limit your response to 100 tokens."""),
        MessagesPlaceholder("chat_history"),
        ("human", "{query}")
    ]

    template = """
    You're my AI assistant that answer queries based on chat hisotry. 
    Your response should be direct, concise and helpful.
    Answer the user query: {query} 
    Here is the chat history: {chat_history}
    """

    prompt = ChatPromptTemplate.from_messages(messages)
        
    chain = prompt | llm | output_parser

    return chain

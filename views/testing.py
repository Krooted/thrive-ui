import streamlit as st
import pandas as pd
import time
from difflib import SequenceMatcher
import re
import asyncio
from utils.vanna_calls import (
    generate_sql,
    run_sql,
    is_sql_valid
)

# Initialize a DataFrame in session state to store results
if "test_results" not in st.session_state:
    st.session_state.test_results = pd.DataFrame(columns=["LLM", "Question", "Answer", "SQL", "DataFrame Summary", "String Similarity", "Data Similarity", "Elapsed Time"])

def calculate_similarity(df_summary, correct_answer):
    # Extract numerical values from both strings
    df_numbers = re.findall(r'\d+', df_summary)  # Extract numbers from df_summary
    correct_numbers = re.findall(r'\d+', correct_answer)  # Extract numbers from correct_answer

    # Convert extracted numbers to integers and create sets
    df_numbers_set = set(map(int, df_numbers))
    correct_numbers_set = set(map(int, correct_numbers))

    # Calculate the intersection of the two sets
    matches = len(df_numbers_set.intersection(correct_numbers_set))

    # Calculate similarity as the percentage of matching numbers
    total_numbers = len(correct_numbers_set)
    if total_numbers == 0:  # Avoid division by zero
        return 0

    similarity = (matches / total_numbers) * 100
    return similarity

async def test_question(llm, my_question):
    st.write(f"Testing LLM: {llm}")
    st.session_state.llm = llm
    # Generate SQL
    start_time = time.time()
    sql = generate_sql(question=my_question["question"])
    end_time = time.time()

    elapsed_time = end_time - start_time

    st.write(f"Elapsed time: {elapsed_time:.2f} seconds")

    st.write(sql)

    df_summary = "No valid data"

    # Check if SQL is valid and run it
    if is_sql_valid(sql=sql):
        df = run_sql(sql=sql)
        st.write(df)

        if not df.empty:
            df_summary = df.to_string(index=False)

    append_new_row(llm, my_question["question"], sql, df_summary, elapsed_time, my_question["answer"])

def append_new_row(llm, question, sql, df_summary, elapsed_time, correct_answer):
    # Calculate similarity between df_summary and correct_answer
    string_similarity = ""
    data_similarity = ""
    if llm != "":
        string_similarity = SequenceMatcher(None, df_summary, correct_answer).ratio() * 100  # Convert to percentage
        data_similarity = calculate_similarity(df_summary, correct_answer)
    new_row = {
        "Question": question,
        "Answer": correct_answer,
        "SQL": sql,
        "DataFrame Summary": df_summary,
        "String Similarity": string_similarity,
        "Data Similarity": data_similarity,
        "LLM": llm,
        "Elapsed Time": elapsed_time,
    }
    st.session_state.test_results = pd.concat(
        [st.session_state.test_results, pd.DataFrame([new_row])],
        ignore_index=True
    )

def test_all_questions():
    questions = [ 
        {
            "question": "how many males vs females were on the titanic", 
            "answer": "female 314 male 577"
        },
        {
            "question": "how many people perished on the titanic?",
            "answer": "549"
        },
        {
            "question": "what is the biggest penguin",
            "answer": "Gentoo penguin with a body mass of 6300 grams"
        }
    ]
    # questions = [
    #     "how many males vs females were on the titanic",
    #     "how many people perished on the titanic?",
    #     "how did ticket price affect the survival rate?",
    #     "what is the biggest penguin",
    #     "How many people smoke?",
    #     "how many people use tabacco",
    #     "How many people are obese and have diabeties?"
    # ]

    # Loop through LLMs
    llms = [
        # "default",
        "anthropic",
        "ollama - llama3.2",
        "ollama - codellama",
        "ollama - deepcoder"
    ]

    for question in questions:
        st.write(f"Testing question: {question["question"]} - {question["answer"]}")
        append_new_row("", "", "", "", "", "")
        for llm in llms:
            asyncio.run(test_question(llm, question))

# Button to trigger the test
st.button("Test All Questions", on_click=lambda: test_all_questions(), use_container_width=True, type="primary")
# Display the updated DataFrame
reordered_columns = ["Question", "Answer", "SQL",  "DataFrame Summary", "String Similarity", "Data Similarity", "LLM", "Elapsed Time"]
st.dataframe(st.session_state.test_results[reordered_columns], height=1200)
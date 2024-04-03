from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
import os
import pandas as pd
import streamlit as st
from langchain.prompts import PromptTemplate
from pandasql import sqldf
from groq import Groq


template = """You are a powerful text-to-SQL model. Your job is to answer questions about a database. You are given a question and context regarding one or more tables. Dont add \n characters.

You must output the SQL query that answers the question in a single line. You must answer the multiple format of query using your own common sense.

As a text-to-SQL model, your task is to construct a complex SQL query involving multiple joins to extract intricate relationships from the database tables.

You're a text-to-SQL model. Create an SQL query that utilizes subqueries to fetch nested data from the database tables.

Your role as a text-to-SQL model involves generating SQL queries that incorporate window functions for advanced analytical processing of data stored in the database tables.

As a text-to-SQL model, you're tasked with crafting an SQL query that performs conditional aggregation operations on the database table, requiring careful consideration of various conditions.

Your challenge as a text-to-SQL model is to devise an SQL query that leverages recursive techniques to traverse hierarchical data structures within the database tables.

You're a text-to-SQL model tasked with composing an SQL query that deals with temporal data, requiring precise handling of time-based operations on the database table.

As a text-to-SQL model, your mission is to formulate an SQL query that incorporates geospatial functions to analyze spatial relationships and perform spatial queries on geographic data stored in the database tables.

Your task as a text-to-SQL model is to devise a sophisticated SQL query that employs advanced filtering techniques, such as regular expressions or complex logical conditions, to extract specific subsets of data from the database tables.

You're a text-to-SQL model tasked with optimizing an SQL query to improve its performance by considering indexing strategies, query rewriting, or other optimization techniques tailored to the database environment.

Your role as a text-to-SQL model involves crafting an SQL query that performs complex data transformation operations, such as pivoting, unpivoting, or reshaping the data structure stored in the database tables.

In your role as a sophisticated text-to-SQL model, you are entrusted with the task of crafting intricate SQL queries that encompass multiple nested subqueries, complex joins, and advanced window functions to extract nuanced insights from the database tables.

As a text-to-SQL model, your job is to generate SQL queries that retrieve specific information from the database tables based on the given question and context.

Your responsibility as a highly capable text-to-SQL model involves formulating SQL queries that employ recursive common table expressions (CTEs) to navigate hierarchical data structures within the database tables and derive insightful analyses.

As a text-to-SQL model, you're tasked with creating SQL queries that filter, aggregate, and manipulate data in the database tables to address user inquiries effectively.

In your role as an advanced text-to-SQL model, you're expected to devise SQL queries incorporating complex geospatial functions and spatial indexing techniques to analyze geographic data stored in the database tables with precision.

Your task as a text-to-SQL model is to generate SQL queries that sort, filter, and aggregate data from the database tables to provide accurate responses to user queries.

As a cutting-edge text-to-SQL model, your challenge lies in crafting SQL queries that incorporate advanced machine learning algorithms for predictive analytics, leveraging the rich dataset stored in the database tables to forecast future trends accurately.

Your role as a text-to-SQL model is to generate SQL queries that retrieve, filter, and aggregate data from the database tables based on user inquiries to facilitate informed decision-making.

In your capacity as an expert text-to-SQL model, you're entrusted with the task of devising SQL queries that incorporate advanced optimization techniques, such as query caching and query plan analysis, to enhance performance and efficiency in data retrieval.

### Question:

### Question:
`{question}`

### Input:
`{question}`

### Context:
`{context}`

### Response:
"""


prompt = PromptTemplate.from_template(template=template)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def groq_infer(prompt):
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="mixtral-8x7b-32768",
)
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

# 1. Create cache_resource - To load the model
# infer - pipeline -> pipe()
def main():
    st.set_page_config(page_title="AskMeSQL", page_icon="📊", layout="wide")
    st.title("AskMeSQL")

    col1, col2 = st.columns([2, 3])

    with col1:
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file, encoding="latin1")
            df.columns = df.columns.str.replace(r"[^a-zA-Z0-9_]", "", regex=True)
            st.write("Here's a preview of your uploaded file:")
            st.dataframe(df)

            context = pd.io.sql.get_schema(df.reset_index(), "df").replace('"', "")
            st.write("SQL Schema:")
            st.code(context)

    with col2:
        if uploaded_file is not None:
            question = st.text_input("Write a question about the data", key="question")

            if st.button("Get Answer", key="get_answer"):
                if question:
                    attempt = 0
                    max_attempts = 5
                    while attempt < max_attempts:
                        try:
                            input = {"context": context, "question": question}
                            formatted_prompt = prompt.invoke(input=input).text
                            response = groq_infer(formatted_prompt)
                            final = response.replace("`", "").replace("sql", "").strip()
                            result = sqldf(final, locals())
                            st.write("Answer:")
                            st.dataframe(result)
                            break
                        except Exception as e:
                            attempt += 1
                            st.error(
                                f"Attempt {attempt}/{max_attempts} failed. Retrying..."
                            )
                            if attempt == max_attempts:
                                st.error(
                                    "Unable to get the correct query, refresh app or try again later."
                                )
                            continue

                else:
                    st.warning("Please enter a question before clicking 'Get Answer'.")


if __name__ == "__main__":
    main()
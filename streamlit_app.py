from dotenv import load_dotenv
from os import environ
from pandas import DataFrame
from pymysql import connect
import streamlit as st

load_dotenv()

DB_HOSTNAME = environ["DB_HOSTNAME"]
DB_USERNAME = environ["DB_USERNAME"]
DB_PASS = environ["DB_PASS"]
DB_PORT = int(environ["DB_PORT"])
DB_NAME = environ["DB_NAME"]


def connect_to_db(db_name):
    return connect(
        host = DB_HOSTNAME,
        port = DB_PORT,
        user = DB_USERNAME,
        password = DB_PASS,
        db = db_name
    )


st.set_page_config(
    layout = "wide",
    page_title = "yoyo money singh"
)

st.title("WhySQL Workbench")

if 'query_results' not in st.session_state:
    st.session_state['query_results'] = []
if 'selected_query_index' not in st.session_state:
    st.session_state['selected_query_index'] = 0

query = st.text_area("Enter your SQL query:", height = 150)

EXECUTE, REMOVE = st.columns([0.5, 0.5])

with EXECUTE:
    if st.button("Execute Query", key = "execute_query"):
        if not query.strip():
            st.error("Please enter a valid SQL query.")
        else:
            try:
                connection = connect_to_db(DB_NAME)
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]

                df = DataFrame(result, columns = columns)
                st.session_state['query_results'].append((query, df))
                st.session_state['selected_query_index'] = len(st.session_state['query_results']) - 1

            except Exception as e:
                st.error(f"An error occurred: {e}")

            finally:
                connection.close()

with REMOVE:
    if st.button("Remove Query", key = "remove_query"):
        if st.session_state['query_results']:
            st.session_state['query_results'].pop(st.session_state['selected_query_index'])
            st.session_state['selected_query_index'] = max(0, len(st.session_state['query_results']) - 1)

            st.rerun()

if st.session_state['query_results']:
    tab_options = [query for query, _ in st.session_state['query_results']]
    selected_query = st.radio(
        "Select a query to view its result:",
        tab_options,
        index = st.session_state['selected_query_index']
    )
    st.session_state['selected_query_index'] = tab_options.index(selected_query)
    st.dataframe(st.session_state['query_results'][st.session_state['selected_query_index']][1])

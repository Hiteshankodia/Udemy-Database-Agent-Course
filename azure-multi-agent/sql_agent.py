import pyodbc
import urllib
from sqlalchemy import create_engine
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.agents import tool
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    
)
# Define the connection string for Azure SQL Database
connection_string = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:sql-db-agent-server.database.windows.net,1433;"
    "Database=sql-agent-db;"
    "Uid=sqladmin;"
    "Pwd=Password_123;"  # Replace with your actual password
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# Establish connection to Azure SQL Database using pyodbc
try:
    connection = pyodbc.connect(connection_string)
    print("Connection successful to Azure SQL Database!")
except Exception as e:
    print(f"Error connecting to Azure SQL Database: {e}")

# Create the connection string for SQLAlchemy (required for pandas .to_sql() function)
params = urllib.parse.quote_plus(
    f'Driver={{ODBC Driver 18 for SQL Server}};'
    f'Server=sql-db-agent-server.database.windows.net;'
    f'Database=sql-agent-db;'
    f'UID=sqladmin;'
    f'PWD=Password_123;'  # Replace with your password
    f'Encrypt=yes;TrustServerCertificate=no;'
)

# Create SQLAlchemy engine for connecting to Azure SQL Database
engine = create_engine(f'mssql+pyodbc:///?odbc_connect={params}')
print("SQLAlchemy engine for Azure SQL Database created successfully!")

# Create SQLDatabase instance from URI
db_uri = f"mssql+pyodbc:///?odbc_connect={params}"
db = SQLDatabase.from_uri(db_uri)  # Create SQLDatabase instance from URI

# Now you can use the SQLDatabase instance with SQLDatabaseToolkit

# Assuming llm is defined elsewhere (like an OpenAI model or similar)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)


QUESTION = """What are the number of movies you have?"
"""


MSSQL_AGENT_PREFIX = """

You are an agent designed to interact with a SQL database.
## Instructions:
- Given an input question, create a syntactically correct {dialect} query
to run, then look at the results of the query and return the answer.
- Unless the user specifies a specific number of examples they wish to
obtain, **ALWAYS** limit your query to at most {top_k} results.
- You can order the results by a relevant column to return the most
interesting examples in the database.
- Never query for all the columns from a specific table, only ask for
the relevant columns given the question.
- You have access to tools for interacting with the database.
- You MUST double check your query before executing it.If you get an error
while executing a query,rewrite the query and try again.
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
to the database.
- DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS
OF THE CALCULATIONS YOU HAVE DONE.
- Your response should be in Markdown. However, **when running  a SQL Query
in "Action Input", do not include the markdown backticks**.
Those are only for formatting the response, not for executing the command.
- ALWAYS, as part of your final answer, explain how you got to the answer
on a section that starts with: "Explanation:". Include the SQL query as
part of the explanation section.
- If the question does not seem related to the database, just return
"I don\'t know" as the answer.
- Only use the below tools. Only use the information returned by the
below tools to construct your query and final answer.
- Do not make up table names, only use the tables returned by any of the
tools below.
- as part of your final answer, please include the SQL query you used in json format or code format

## Tools:

"""



MSSQL_AGENT_FORMAT_INSTRUCTIONS = """

## Use the following format:

Question: the input question you must answer.
Thought: you should always think about what to do.
Action: the action to take, should be one of [{tool_names}].
Action Input: the input to the action.
Observation: the result of the action.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Final Answer: the final answer to the original input question.

Example of Final Answer:
<=== Beginning of example

Action: query_sql_db
Action Input: 
SELECT TOP (10) [title], [genre], [release_date], [budget], [revenue] 
FROM movies

WHERE genre = 'Drama'

Observation:
[('The Shawshank Redemption', 'Drama', '1994-09-23', 25000000, 28341469),
 ('Pulp Fiction', 'Drama', '1994-09-10', 8000000, 213928762)]
Thought: I now know the final answer
Final Answer: The two movies in the Drama genre are "The Shawshank Redemption" and "Pulp Fiction". The budgets and revenues for each movie are also provided.

Explanation:
I queried the `movies` table for the `title`, `genre`, `release_date`, `budget`, and `revenue` where the genre is 'Drama'. The query returned a list of tuples with the movie details, which I used to answer the question.
The following query was used:

```sql
SELECT [title], [genre], [release_date], [budget], [revenue] 
FROM movies WHERE genre = 'Drama' ; """




# sql_agent = create_sql_agent(
#     prefix=MSSQL_AGENT_PREFIX,
#     format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
#     llm=llm,
#     toolkit=toolkit,
#     top_k=30,
#     verbose=True
# )


# @tool
# def sql_agent(word: str) -> int:
#     """sql agent for movies related queries."""
#     return create_sql_agent(
#     prefix=MSSQL_AGENT_PREFIX,
#     format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
#     llm=llm,
#     toolkit=toolkit,
#     top_k=30,
#     verbose=True
# )




sql_agent_ = create_sql_agent(
    prefix=MSSQL_AGENT_PREFIX,
    format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
    llm=llm,
    toolkit=toolkit,
    top_k=30,
    verbose=True
)

@tool
def sql_agent(query) : 
    '''sql agent for movies related queries'''
    return sql_agent_.invoke(query)

# result = get_word_length.invoke("abc")
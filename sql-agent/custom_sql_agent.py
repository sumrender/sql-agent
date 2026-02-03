"""Custom SQL agent using LangGraph primitives."""
from typing import Literal

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt

from langchain_community.utilities import SQLDatabase
from config import get_sqlite_connection_uri
from llm import get_llm
from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

def db_info(db: SQLDatabase) -> None:
    """Log database tables."""
    try:
        tables = db.get_usable_table_names()
        logger.info("DATABASE TABLES: %s", tables)
    except Exception as e:
        logger.warning("Could not fetch tables list: %s", e)


def connect_database() -> SQLDatabase:
    """Connect to SQLite and return the SQLDatabase instance."""
    try:
        db = SQLDatabase.from_uri(get_sqlite_connection_uri())
        logger.info("Connected to SQLite database")
        db_info(db)
        return db
    except Exception as e:
        logger.error("Failed to connect to SQLite: %s", e, exc_info=True)
        raise

# Initialize LLM and Database
model = get_llm()
db = connect_database()

# SQL tools for the agent
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")

# Define the custom tool
@tool(
    run_query_tool.name,
    description=run_query_tool.description,
    args_schema=run_query_tool.args_schema
)
def run_query_tool(config: RunnableConfig, **tool_input):
    """Execute a SQL query with human-in-the-loop interrupt."""
    request = {
        "action": run_query_tool.name,
        "args": tool_input,
        "description": "Please review the SQL query before execution."
    }
    # This will pause the execution and wait for human input
    logger.info("Interrupting for human review of SQL query")
    return run_query_tool.invoke(tool_input, config)

# Nodes
get_schema_node = ToolNode([get_schema_tool], name="get_schema")
run_query_node = ToolNode([run_query_tool], name="run_query")

def list_tables(state: MessagesState):
    """Step 1: List tables in the database."""
    tool_call = {
        "name": "sql_db_list_tables",
        "args": {},
        "id": "list_tables_call",
        "type": "tool_call",
    }
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])
    # For sql_db_list_tables, the input is typically an empty string
    tool_output = list_tables_tool.invoke("")
    content = getattr(tool_output, "content", str(tool_output))

    # We create a ToolMessage to represent the tool execution in history
    tool_message = ToolMessage(content=content, tool_call_id=tool_call["id"])

    response = AIMessage(content=f"Available tables: {content}")
    return {"messages": [tool_call_message, tool_message, response]}

def call_get_schema(state: MessagesState):
    """Step 2: Decide which tables' schemas to fetch."""
    # Force the model to use the get_schema_tool
    llm_with_tools = model.bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

generate_query_system_prompt = """
You are an agent designed to interact with a SQL database.
If the user asks a question about you, you can answer about yourself and your capabilities.
Don't run any tools to answer the question about yourself.
Apart from that, you should answer the question based on the database.
Do not answer any question that is not related to the database or yourself.

Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.

IMPORTANT: You MUST always execute a SQL query to get data from the database.
Do NOT guess or infer answers from schema information, comments, or sample data.
Always run a query to get the actual current data.
""".format(
    dialect=db.dialect,
    top_k=5,
)

def generate_query(state: MessagesState):
    """Step 3: Generate the SQL query."""
    system_message = SystemMessage(content=generate_query_system_prompt)
    # Force the model to call run_query_tool
    llm_with_tools = model.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}

check_query_system_prompt = """
You are a SQL expert with a strong attention to detail.
Double check the {dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes,
just reproduce the original query.

You will call the appropriate tool to execute the query after running this check.
""".format(dialect=db.dialect)

def check_query(state: MessagesState):
    """Step 4: Verify the generated query."""
    system_message = SystemMessage(content=check_query_system_prompt)

    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return {"messages": []}

    tool_call = last_message.tool_calls[0]
    # Use the model to check the query by presenting it as a user message
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    # Force tool call to sql_db_query
    llm_with_tools = model.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message, user_message])
    return {"messages": [response]}

def should_continue(state: MessagesState) -> Literal["check_query", END]:
    """Conditional edge to determine if we should check the query or end."""
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    return "check_query"

# Assemble the graph
builder = StateGraph(MessagesState)
builder.add_node(list_tables)
builder.add_node(call_get_schema)
builder.add_node("get_schema", get_schema_node)
builder.add_node(generate_query)
builder.add_node(check_query)
builder.add_node("run_query", run_query_node)

builder.add_edge(START, "list_tables")
builder.add_edge("list_tables", "call_get_schema")
builder.add_edge("call_get_schema", "get_schema")
builder.add_edge("get_schema", "generate_query")
builder.add_conditional_edges("generate_query", should_continue)
builder.add_edge("check_query", "run_query")
builder.add_edge("run_query", "generate_query")


agent = builder.compile()


"""

┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────────┐
│ list_tables │  ← Lists all database tables
└──────┬──────┘
       │
       ▼
┌────────────────┐
│ call_get_schema│  ← LLM decides which table schemas to fetch
└───────┬────────┘
        │
        ▼
┌────────────┐
│ get_schema │  ← ToolNode: fetches the selected table schemas
└──────┬─────┘
       │
       ▼
┌────────────────┐
│ generate_query │  ← LLM generates SQL query using run_query_tool
└───────┬────────┘
        │
        ▼ (conditional edge)
   ┌────┴────┐
   │ should_ │
   │continue?│
   └────┬────┘
        │
   ┌────┴────┐
   │         │
   ▼         ▼
┌─────────┐  ┌─────┐
│check_   │  │ END │  ← If no tool calls
│query    │
└────┬────┘
     │
     ▼
┌───────────┐
│ run_query │  ← ToolNode: executes the SQL query
└─────┬─────┘
      │
      └──────────► (loops back to generate_query)

"""
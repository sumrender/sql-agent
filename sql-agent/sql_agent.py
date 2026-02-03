"""SQL agent for SQLite, used by both LangGraph Studio and the FastAPI API."""
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.checkpoint.memory import InMemorySaver

from config import get_sqlite_connection_uri
from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)
from llm import get_llm


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


model = get_llm()
db = connect_database()

# SQL tools for the agent
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()
logger.info("SQL agent initialized with %d tools", len(tools))

# Safety-focused system prompt (read-only, no DML)
system_prompt = """
You are an agent designed to interact with a SQL database.
If the user asks a question about you, you can answer about yourself and your capabilities.
Don't run any tools to answer the question about yourself.
Apart from that, you should answer the question based on the database.
Do not answer any question that is not related to the database or yourself.

Given an input question that looks related to the database, if it looks that it needs data from the database, for that create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results. Exception: for questions asking for a total count
(e.g. "how many X") or a single aggregate value (e.g. "total amount", "sum of"),
use one query with COUNT(*), SUM(...), etc., and do NOT apply LIMIT to that
aggregate query; return the single number from the result.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

Your final answer must be based only on the results returned by your SQL query.
Do not add information from outside the database or invent list items not present
in the query results.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect,
    top_k=5,
)

agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"sql_db_query": True},
            description_prefix="Tool execution pending approval",
        ),
    ]
)


def get_eval_agent():
    """Return an agent without HITL middleware for evaluation runs."""
    return create_agent(
        model,
        tools,
        system_prompt=system_prompt,
    )

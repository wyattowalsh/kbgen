from functools import lru_cache
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
import logging
from rich.logging import RichHandler
import langfuse
import langsmith

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)

# Initialize langfuse and langsmith
langfuse.init()
langsmith.init()

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


system_prompt = """Be a helpful assistant"""

# Define the function that calls the model
def call_model(state, config):
    description_prompt = f"""
    Generate a detailed description of the topic around {config['agent']['description_max_words']} words in length and aimed at post-doctoral technical scholars/researchers.
    """
    state["messages"].append({"role": "user", "content": description_prompt})
    logger.info("Calling model with description prompt")
    langfuse.trace(logger)
    langsmith.trace(logger)
    return call_model(state, config)

# Define the function for generating knowledge graphs
def generate_knowledge_graph(state, config):
    knowledge_graph_prompt = """
    Create a knowledge graph using entity relation semantic triplets and advanced, styled mermaid.js markdown syntax that is as robust, inclusive, and comprehensive as possible and serve as a concept/topic map.
    """
    state["messages"].append({"role": "user", "content": knowledge_graph_prompt})
    logger.info("Calling model with knowledge graph prompt")
    langfuse.trace(logger)
    langsmith.trace(logger)
    return call_model(state, config)

# Define the function for generating related topics
def generate_related_topics(state, config):
    related_topics_prompt = """
    Generate a list of related topics (up to 25) using bulleted list and wikilinks link notation.
    """
    state["messages"].append({"role": "user", "content": related_topics_prompt})
    logger.info("Calling model with related topics prompt")
    langfuse.trace(logger)
    langsmith.trace(logger)
    return call_model(state, config)

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplates
from langchain_core.output_parser import StrOutputParser
from dotenv import load_dotenv
from tools import page_fetch, search_query
from rich import print


load_dotenv()

model = init_chat_model(
    model = "google/gemma-3n-e2b-it:free",
    model_provider = "openrouter",
    temperature = 0
)


def search_agent():
    return create_agent(
        model = model,
        tools = [search_query]
    )

def scrape_agent():
    return create_agent(
        model = model,
        tools = [page_fetch]
    )


writer_prompt = ChatPromptTemplates.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])


writer_chain = writer_prompt | model | StrOutputParser()


critic_prompt = ChatPromptTemplates.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | model | StrOutputParser()

# response = model.invoke("Why do parrots have colorful feathers?")

# print(response)
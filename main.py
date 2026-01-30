from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
import os
import asyncio
import requests
from faker import Faker
from langchain_mcp_adapters.client import MultiServerMCPClient
import os, shutil


node_dir = r"C:\Program Files\nodejs"
npm_user_bin = os.path.join(os.environ["APPDATA"], "npm")  # где обычно лежит npx.cmd

os.environ["PATH"] = node_dir + ";" + npm_user_bin + ";" + os.environ.get("PATH", "")


class AgentState(TypedDict):
    """Состояние агента, содержащее последовательность сообщений."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
async def add(a: int, b: int) -> int:
    """Складывает два целых числа и возвращает результат."""
    await asyncio.sleep(0.1)
    return a + b


@tool
async def list_files() -> list:
    """Возвращает список файлов в текущей папке."""
    await asyncio.sleep(0.1)
    return os.listdir(".")

tools = [add, list_files]


@tool
async def get_random_user_name(gender: str) -> str:
    """
    Возвращает случайное мужское или женское имя в зависимости от условия:
    male - мужчина, female - женщина
    """
    faker = Faker("ru_RU")
    gender = gender.lower()
    if gender == "male":
        return f"{faker.first_name_male()} {faker.last_name_male()}"
    return f"{faker.first_name_female()} {faker.last_name_female()}"


custom_tools = [get_random_user_name]


async def get_all_tools():
    """Получение всех инструментов: ваших + MCP"""
    # Настройка MCP клиента
    mcp_client = MultiServerMCPClient(
        {
            "filesystem": {
                "command":  r"C:\Program Files\nodejs\npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
                "transport": "stdio",
            },
            "context7": {
                "transport": "streamable_http",
                "url": "https://mcp.context7.com/mcp",
            },
        }
    )

    # Получаем MCP инструменты
    mcp_tools = await mcp_client.get_tools()

    # Объединяем ваши инструменты с MCP инструментами
    return custom_tools + mcp_tools


from langchain.agents import create_agent


llm = ChatOpenAI(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    base_url="http://localhost:8000/v1",
    api_key="localtoken",
    temperature=0)


async def main():
    all_tools = await get_all_tools()
    agent = create_agent(
        model=llm,
        tools=all_tools)

    result = await agent.ainvoke({"messages": [{'role': 'system',
                                                'content': "Ты дружелюбный ассистент, который может генерировать фейковых пользователей, \
    выполнять вычисления и делиться интересными фактами.",},
                                               {"role": "user", "content": "Сгенерируй мне случайного пользователя"}]})
    print(result["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())

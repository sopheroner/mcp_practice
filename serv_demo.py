from fastmcp import FastMCP
import os

node_dir = r"C:\Program Files\nodejs"
npm_user_bin = os.path.join(os.environ["APPDATA"], "npm")  # где обычно лежит npx.cmd

os.environ["PATH"] = node_dir + ";" + npm_user_bin + ";" + os.environ.get("PATH", "")

mcp = FastMCP("Мой сервер")


@mcp.tool
def add(a: int, b: int) -> int:
    """Складывает два числа"""
    return a + b


@mcp.tool
async def fetch_weather(city: str) -> str:
    """Получает погоду для города"""
    # Здесь может быть вызов API
    return f"В городе {city} сегодня солнечно"


@mcp.resource("user://profile/{user_id}")
def get_user_profile(user_id: str) -> str:
    """Получает профиль пользователя по ID"""
    return f"Профиль пользователя {user_id}: активный, премиум-подписка"


@mcp.resource("docs://readme")
def get_readme() -> str:
    """Возвращает README проекта"""
    with open("README.md", "r") as f:
        return f.read()


@mcp.prompt
def debug_code(error_message: str) -> str:
    """Помогает отладить код по сообщению об ошибке"""
    return f"""
    Анализируй эту ошибку и предложи решение:

    Ошибка: {error_message}

    Дай пошаговые инструкции для исправления.
    """


@mcp.prompt
def review_code(code: str) -> list:
    """Создает промпт для ревью кода"""
    return [
        {"role": "user", "content": f"Проверь этот код:\n\n{code}"},
        {"role": "assistant", "content": "Я помогу проверить код. Что конкретно тебя беспокоит?"}
    ]


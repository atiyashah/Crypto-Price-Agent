
import chainlit as cl
from agents import (
    OpenAIChatCompletionsModel,
    Agent,
    Runner,
    AsyncOpenAI,
    function_tool,
    set_tracing_disabled
)
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

# Disable tracing
set_tracing_disabled(True)

# Gemini client setup
provider = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=GEMINI_API_KEY,
)

# Model definition
model = OpenAIChatCompletionsModel("gemini-2.0-flash", openai_client=provider)

# Tool 1: Specific coin price tool
@function_tool
def fetch_coin_rate(name: str, symbol: str):
    """
    Fetches real-time USD price of a given cryptocurrency by name or symbol.
    Arguments:
    - name (str): The name, symbol, or ID of the cryptocurrency.
    """
    print(f"Getting {name} price ...")
    response = requests.get("https://api.coinlore.net/api/tickers/")
    coins = response.json()["data"]

    for coin in coins:
        if (
            coin["name"].lower() == name.lower()
            or coin["symbol"].lower() == name.lower()
            or coin["nameid"].lower() == name.lower()
        ):
            price = coin["price_usd"]
            print(f"Fetched Rate: {price}")
            return {
                "name": coin["name"],
                "symbol": coin["symbol"],
                "price_usd": price,
            }

    return {
        "status": "fail",
        "details": f"Coin '{name}' is not available in the current coin list.",
    }

# Tool 2: Get top 10 coins
@function_tool
def fetch_top_coins(topic: str = "top coins"):
    """
    Fetches the top 10 cryptocurrencies by market cap.
    Use it when the user asks about top coins, trending coins, or BTC list.
    """
    print("Fetching Top 10 Cryptocurrencies ...")
    response = requests.get("https://api.coinlore.net/api/tickers/?limit=10")
    coins = response.json()["data"]

    result = "**Top 10 Cryptocurrencies by Market Cap:**\n"
    for idx, coin in enumerate(coins, start=1):
        result += f"{idx}. {coin['name']} ({coin['symbol']}) - ${coin['price_usd']}\n"

    return result

# Agent Setup
CryptoAgent = Agent(
    name="CryptoAgent",
    instructions="""
You are a dedicated Crypto Agent specialized in providing real-time cryptocurrency prices using the 'fetch_coin_rate' and 'fetch_top_coins' tools.

- For the price of a single coin like Bitcoin, Ethereum, or any coin name or symbol, use the 'fetch_coin_rate' tool.

- If the user asks any of the following:
  "top coins today"
  "top 10"
  "top crypto list"
  "top 10 crypto prices"
  "which coins are trending today"
Then use the 'fetch_top_coins' tool.

You should only respond with data from these tools. Do not answer any unrelated questions.
""",
    model=model,
    tools=[fetch_coin_rate, fetch_top_coins],
)

# Chat start handler
@cl.on_chat_start
async def handle_chat_start():
    await cl.Message(content="**Welcome to the Crypto Price Agent!** 🪙\nAsk me about any cryptocurrency’s price, or say 'top 10 coins' to get trending crypto list.").send()

# Chat message handler
@cl.on_message
async def on_message(message: cl.Message):
    user_input = message.content
    result = await Runner.run(CryptoAgent, user_input)
    await cl.Message(content=str(result.final_output)).send()
















# import chainlit as cl
# from agents import (
#     OpenAIChatCompletionsModel,
#     Agent,
#     Runner,
#     AsyncOpenAI,
#     function_tool,
#     set_tracing_disabled
# )

# from dotenv import load_dotenv
# import os
# import requests

# # ✅ Load environment variables
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

# # ✅ Disable tracing (optional)
# set_tracing_disabled(True)

# # ✅ Gemini client setup
# provider = AsyncOpenAI(
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#     api_key=GEMINI_API_KEY,
# )

# # ✅ Model definition
# model = OpenAIChatCompletionsModel("gemini-2.0-flash", openai_client=provider)

# # ✅ Tool 1: Get price of one coin
# @function_tool
# def fetch_coin_rate(name: str, symbol: str):
#     """
#     Fetches real-time USD price of a given cryptocurrency by name or symbol.
#     Arguments:
#     - name (str): The name, symbol, or ID of the cryptocurrency.
#     """
#     print(f"Getting {name} Price ...")
#     response = requests.get("https://api.coinlore.net/api/tickers/")
#     coins = response.json()["data"]

#     for coin in coins:
#         if (
#             coin["name"].lower() == name.lower() 
#             or coin["symbol"].lower() == name.lower() 
#             or coin["nameid"].lower() == name.lower() 
#         ):
#             price = coin["price_usd"]
#             print(f"Fetched Rate: {price}")
#             return {
#                 "name": coin["name"],
#                 "symbol": coin["symbol"],
#                 "price_usd": price,
#             }

#     return {
#         "status": "fail",
#         "details": f"Coin '{name}' is not available in the current coin list.",
#     }

# # 🔧 Tool 2: Get top 10 coins (CHANGED: added 'topic' argument + better return format)
# @function_tool
# def fetch_top_coins(topic: str = "top coins"):
#     """
#     Fetches the top 10 cryptocurrencies by market cap.

#     This tool returns a list of the top 10 crypto coins based on real-time data.
#     Use it when the user asks about top coins, trending coins, or BTC list.
#     """
#     print("Fetching Top 10 Cryptocurrencies ...")
#     response = requests.get("https://api.coinlore.net/api/tickers/?limit=10")
#     coins = response.json()["data"]

#     result = "**Top 10 Cryptocurrencies by Market Cap:**\n"
#     for idx, coin in enumerate(coins, start=1):
#         result += f"{idx}. {coin['name']} ({coin['symbol']}) - ${coin['price_usd']}\n"

#     return result

# # ✅ Agent Setup (already correct, just keeping both tools here)
# CryptoAgent = Agent(
#     name="CryptoAgent",
#     instructions="""
# You are a dedicated Crypto Agent specialized in providing real-time cryptocurrency prices using the 'fetch_coin_rate' and 'fetch_top_coins' tools.

# - Use 'fetch_coin_rate' to respond to queries about specific coins (e.g., "Bitcoin", "ETH").
# - Use 'fetch_top_coins' when the user asks about top coins, trending crypto, or top 10 cryptocurrencies.
# - Always prefer accurate, real-time data.
# - Only respond to cryptocurrency-related queries.
# """,
#     model=model,
#     tools=[fetch_coin_rate, fetch_top_coins],
# )

# # ✅ Welcome Message
# @cl.on_chat_start
# async def handle_chat_start():
#     await cl.Message(content="**Welcome to the Crypto Price Agent!** 🪙\nAsk me about any cryptocurrency's price, or say 'top 10 coins' to get trending crypto list.").send()

# # ✅ Message Handler
# @cl.on_message
# async def on_message(message: cl.Message):
#     user_input = message.content
#     result = await Runner.run(CryptoAgent, user_input)
#     await cl.Message(content=str(result.final_output)).send()
















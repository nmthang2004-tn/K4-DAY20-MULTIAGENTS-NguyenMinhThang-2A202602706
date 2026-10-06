"""PROVIDED - do not edit. Builds the chat model from environment variables (see .env.example).

Two configurations are supported (the first that matches wins):

1. Azure OpenAI or an OpenAI-compatible gateway - set all three variables:
   AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT_MODEL
   (optional: AZURE_OPENAI_API_VERSION, used only for real Azure endpoints).
2. Any LangChain provider - set LAB_MODEL="<provider>:<model>" (default "deepseek:deepseek-chat")
   and the key variable of that provider (for example DEEPSEEK_API_KEY).
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


def make_model():
    """Return a chat model configured from the environment."""
    temperature = float(os.getenv("LAB_TEMPERATURE", "0"))

    # Option 1: OpenAI API (OPENAI_API_KEY + OPENAI_MODEL)
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL")
    if openai_key and openai_model:
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(api_key=openai_key, model=openai_model, timeout=120)
        # Model doesn't support temperature parameter, so don't set it
        return model

    # Option 2: Azure OpenAI
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_MODEL")
    if endpoint and key and deployment:
        if "openai.azure.com" in endpoint or "cognitiveservices.azure.com" in endpoint:
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(
                azure_endpoint=endpoint, api_key=key, azure_deployment=deployment,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                temperature=temperature, timeout=120,
            )
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(base_url=endpoint, api_key=key, model=deployment, temperature=temperature, timeout=120)

    # Option 3: Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            api_key=gemini_key,
        )

    # Option 4: Default (deepseek)
    return init_chat_model(os.getenv("LAB_MODEL", "deepseek:deepseek-chat"), temperature=temperature)

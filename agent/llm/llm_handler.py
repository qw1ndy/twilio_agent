import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.prompts import ChatPromptTemplate
from utils.promts import extract_prompt_template
from utils.state import User_Info
from typing import cast


load_dotenv()


GENAI_API_KEY = os.getenv("GENAI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=GENAI_API_KEY)
structured_llm = llm.with_structured_output(User_Info)

extract_prompt = ChatPromptTemplate.from_template(
    extract_prompt_template
)


def extract_info(history: list[str]) -> User_Info:
    prompt = extract_prompt.format(history="\n".join(history))
    output = structured_llm.invoke(prompt)
    return cast(User_Info, output)
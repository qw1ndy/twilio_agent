import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from utils.promts import extract_prompt_template
from utils.state import User_Info


load_dotenv()


GENAI_API_KEY = os.getenv("GENAI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=GENAI_API_KEY)
parser = PydanticOutputParser(pydantic_object=User_Info)

extract_prompt = PromptTemplate.from_template(
    extract_prompt_template
).partial(format_instructions=parser.get_format_instructions())


def extract_info(history: list[str]) -> User_Info:
    prompt = extract_prompt.format(history="\n".join(history))
    output = llm.predict(prompt)
    return parser.parse(output)
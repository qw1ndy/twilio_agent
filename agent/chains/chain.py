from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from utils.state import User_Info
from utils.promts import extract_prompt_template, system_prompt
import os
from dotenv import load_dotenv
from typing import List, cast

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")

class Pipeline:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=GENAI_API_KEY
        )

        self.structured_llm = self.llm.with_structured_output(User_Info)

        self.extract_prompt = ChatPromptTemplate.from_template(extract_prompt_template)
        self.extract_chain = self.extract_prompt | self.structured_llm

        self.dialogue_prompt = ChatPromptTemplate.from_template(system_prompt)
        self.dialogue_chain = self.dialogue_prompt | self.llm

    def run_turn(self, history: List[str]) -> tuple[str, User_Info]:
        """
        Processes one step of the conversation: generates a response + extracts information
        """
        prompt_text = "\n".join(history)

        ai_response = self.dialogue_chain.invoke({"history": prompt_text})
        
        if hasattr(ai_response, "content"):
            ai_text = str(ai_response.content)
        elif isinstance(ai_response, str):
            ai_text = ai_response
        elif isinstance(ai_response, list):
            ai_text = "\n".join([str(item) for item in ai_response])
        else:
            ai_text = str(ai_response)

        history.append(f"AI: {ai_text}")

        user_info = self.extract_chain.invoke({"history": "\n".join(history)})

        return ai_text, cast(User_Info, user_info)
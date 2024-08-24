import fitz
import json

from langchain.chains.openai_tools import create_extraction_chain_pydantic
from langchain_openai import ChatOpenAI
from autogen import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager

from . import models, documentation
from config import settings

class ResumeTool():
    def __init__(self, model: str):
        self.model = model
        self.chat = ChatOpenAI(model=model, api_key=settings.open_ai_api_key)
        self.resume_chain = create_extraction_chain_pydantic(
            [models.Education, 
             models.Experience, 
             models.Certifications, 
             models.Resume, 
             models.Projects], 
             self.chat
        )

    def extract_text_from_pdf(self, resume_path: str) -> str:
        text = ""
        with fitz.open(resume_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def extract_resume_details(self, resume_path: str) -> models.Resume:
        text = self.extract_text_from_pdf(resume_path)
        response = self.resume_chain.invoke({"input" : text})
        return response
    
    def extract_job_search_details_v2(self, extracted_content):
        config = [{
            "model": self.model,
            "api_key": settings.open_ai_api_key
        }]
        llm_config = {
            "cache_seed": 29,
            "temperature": 0,
            "config_list": config,
            "timeout": 120
        }
        user_proxy = UserProxyAgent(
            name="Admin",
            system_message="""A human admin. Interact with the Extractor to discuss the strategy to extract the details from the resume. Strategy execution must be approved by this admin. 
            When you receive a JSON from the Extractor that has been approved by the Critique, you must return it as the final response.
            Your response should only be the exact JSON received, with no additional text or formatting.""",
            human_input_mode="NEVER",
            code_execution_config=False,
            llm_config=llm_config
        )

        extractor = AssistantAgent(
            "Extractor",
            llm_config=llm_config,
            system_message=documentation.extraction_documentation.get("extractor")
        )
    
        critique = AssistantAgent(
            "Critique",
            llm_config=llm_config,
            system_message=documentation.extraction_documentation.get("critique")
        )

        allowed_transitions_dict = {
            user_proxy: [],
            extractor: [critique, user_proxy],
            critique: [extractor]
        }

        group_chat = GroupChat(
           agents=[user_proxy, extractor, critique], messages=[], allowed_or_disallowed_speaker_transitions=allowed_transitions_dict, speaker_transitions_type="allowed"
        )

        manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
        user_proxy.initiate_chat(
            manager,
            message=f"""
                {documentation.extraction_documentation.get("user_proxy")}
                The resume info is available here {extracted_content}

                Ensure that the final message is always from the Admin. 
            """,
        )

        final_json = None
        # go in reverse and find the first message that is json parseable

        for message in reversed(group_chat.messages):
            try:
                final_json = json.loads(message.get("content"))
                break
            except:
                pass
        
        print(final_json)
        return final_json

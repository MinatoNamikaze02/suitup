import fitz
import json

from langchain.chains.openai_tools import create_extraction_chain_pydantic
from langchain_openai import ChatOpenAI
from autogen import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager

from . import models
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
            # "base_url": "http://localhost:11434/v1",
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
            system_message= "A human admin. Interact with the Extractor to discuss the strategy to extract the details from the resume. Strategy execution must be approved by this admin. When the final JSON is sent to you by extractor, return it exactly as it was given without any modifications as the final response.",
            human_input_mode="NEVER",
            code_execution_config=False,
            llm_config=llm_config
        )

        extractor = AssistantAgent(
            "Extractor",
            llm_config=llm_config,
            system_message="Extractor. You follow the plan of the Admin to extract the details from the resume. You will only the return the data in a JSON format."
        )
    
        critique = AssistantAgent(
            "Critique",
            llm_config=llm_config,
            system_message="""Critique. You are tasked with reviewing the extracted data from the Extractor and providing feedback on the quality of the data. Double check everything from the quality of results to the format.
            Keep the following things in mind while evaluating.
                - The "search_term" should not include skills as such but industry-specific job titles or roles.
                - Remember that the "search_term" cannot be empty. If no job title is explicitly mentioned, use the most relevant information available. 
                - "Location" should be extracted with an emphasis on the most specific geographical detail available, ideally pinpointing the job seeker's preferred work location.
                - For "job_type", interpret the context to identify the type of employment being sought, if stated.
                - The "country_indeed" should be inferred from the location provided. Kindly default to empty strings if the information is not available.

                Once you have approved the JSON, ask the Extractor to return the data to the Admin as the final step. If not, be firm and ask the extractor to return data back to you.
            """
        )

        allowed_transitions_dict = {
            user_proxy: [extractor],
            extractor: [critique, user_proxy],
            critique: [extractor]
        }

        group_chat = GroupChat(
           agents=[user_proxy, extractor, critique], messages=[], max_round=5, allowed_or_disallowed_speaker_transitions=allowed_transitions_dict, speaker_transitions_type="allowed"
        )

        manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
        user_proxy.initiate_chat(
            manager,
            message=f"""
                You are a detail-oriented assistant tasked with extracting key employment-related information from the parsed contents of a resume. Please return the information in JSON format with the following details:

                1. search_term: A list of strings containing job titles and roles, focusing on the level of seniority. Try to identify the senior most role mentioned in the resume and if deemed necessary add some other roles similar to that one. If no job title is explicitly mentioned, use the most relevant information available.

                2. location: The geographical location specified in the resume, presented as "city, region" within the country.

                3. job_type: The type of employment being sought, categorized strictly as one of the following: "fulltime", "parttime", "internship", "contract". If this information is not explicitly mentioned, leave it as an empty string.

                4. country_indeed: The country, in lowercase, where the job search is focused, derived from the location information.

                The resume info is available here {extracted_content}
            """
        )
    
        print(manager.groupchat.messages[-1])
        return json.loads(manager.groupchat.messages[-1].get("content"))

    def extract_job_search_details(self, extracted_content):
        messages = [
            {
                "role": "system",
                "content": """
                        You are a detail-oriented assistant tasked with extracting key employment-related information from the parsed contents of a resume. Please return the information in JSON format with the following details:

                        1. search_term: A list of strings containing job titles and roles, focusing on the level of seniority (e.g., "Sr Software Engineer") and specific skills relevant to job roles.

                        2. location: The geographical location specified in the resume, presented as "city, region" within the country.

                        3. job_type: The type of employment being sought, categorized strictly as one of the following: "fulltime", "parttime", "internship", "contract". If this information is not explicitly mentioned, leave it as an empty string.

                        4. country_indeed: The country, in lowercase, where the job search is focused, derived from the location information.

                        Key assumptions:
                        - The "search_term" should not include skills as such but industry-specific job titles or roles.
                        - Remember that the "search_term" cannot be empty. If no job title is explicitly mentioned, use the most relevant information available.
                        - "Location" should be extracted with an emphasis on the most specific geographical detail available, ideally pinpointing the job seeker's preferred work location.
                        - For "job_type", interpret the context to identify the type of employment being sought, if stated.
                        - The "country_indeed" should be inferred from the location provided. Kindly default to empty strings if the information is not available.

                        This task requires a nuanced understanding of job-seeking terminology and the ability to discern relevant employment details from a broader array of resume content.
                """
            },
            {
                "role": "user",
                "content": f"Resume content: {extracted_content}"
            }
        ]
        
        response = self.chat.invoke(messages)
        response_json = json.loads(response.content)
        print(response_json)
        return response_json

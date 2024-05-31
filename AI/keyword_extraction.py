import fitz
import json

from langchain.chains.openai_tools import create_extraction_chain_pydantic
from langchain_openai import ChatOpenAI

from . import models
from config import settings

class ResumeTool():
    def __init__(self, model: str):
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
                        - Remember that the "search_term" CANNOT be empty. If no job title is explicitly mentioned, use the most relevant information available.
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
    


        
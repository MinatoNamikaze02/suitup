import chainlit as cl
import os
import shutil
import json
import toml
import traceback
import html
import markdown

from chainlit.input_widget import Select, TextInput, NumberInput, Switch
from AI.keyword_extraction import ResumeTool
from search.job_search import JobScraper
from search.logger import get_logger
from config import settings

import utils

logger = get_logger(__name__)

UPLOAD_DIR = settings.upload_dir
CONFIG_PATH = settings.config_path

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@cl.action_callback("Sync Jobs")
async def sync_jobs(action):
    try:
        config = utils.load_config()
        resume_file_path = config.get("Resume", {}).get("resumeFilePath", "")
        if not os.path.exists(resume_file_path):
            await cl.Message(content="Resume file not found").send()
            return

        resume_ext = ResumeTool(model=config.get("GenAI", {}).get("openAIModel", "gpt-3.5-turbo-instruct"))
        if not os.path.exists("user_info.json"):
            resume_details = resume_ext.extract_resume_details(resume_file_path)
            dict_repr = resume_details[0].dict()
            with open("user_info.json", "w") as f:
                json.dump(dict_repr, f)
        else:
            with open("user_info.json", "r") as f:
                dict_repr = json.load(f)

        job_search_settings = resume_ext.extract_job_search_details_v2(dict_repr)

        for key, value in job_search_settings.items():
            if not value:
                job_search_settings[key] = config.get("JobSearch", {}).get(key, value)

        logger.info(f"Job search settings: {job_search_settings}")

        job_scraper = JobScraper()
        args = config.get("JobSearch", {})
        args.update(job_search_settings)

        temp = args.get("search_term", [])
        for term in temp:
            args["search_term"] = term
            job_scraper.scrape_and_save(**args)

        msg = await cl.Message(content="Jobs synced successfully").send()
        await cl.Action(name="View Jobs", value="view_jobs").send(for_id=msg.id)
    except Exception as e:
        logger.error(traceback.format_exc())
        await cl.Message(content=f"Error syncing jobs: {str(e)}").send()

@cl.action_callback("Upload Resume")
async def upload_resume(action):
    files = await cl.AskFileMessage(
        content="Please upload your resume to continue", accept=["text/plain", "application/pdf"]
    ).send()

    if files:
        resume = files[0]
        try:
            file_path = os.path.join(UPLOAD_DIR, resume.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)

            config = utils.load_config()
            config['Resume']['resumeFilePath'] = file_path

            with open(CONFIG_PATH, 'w') as config_file:
                toml.dump(config, config_file)

            if os.path.exists("user_info.json"):
                os.remove("user_info.json")

            msg = await cl.Message(content=f"Resume uploaded: {resume.filename}").send()
            await cl.Action(name="Sync Jobs", value="sync_jobs").send(for_id=msg.id)
        except Exception as e:
            await cl.Message(content=f"Error uploading resume: {str(e)}").send()

@cl.action_callback("Purge Jobs")
async def purge_jobs(action):
    try:
        if os.path.exists("jobs.db"):
            os.remove("jobs.db")
        msg = await cl.Message(content="Jobs purged successfully").send()
        await cl.Action(name="Sync Jobs", value="sync_jobs").send(for_id=msg.id)
    except Exception as e:
        await cl.Message(content=f"Error purging jobs: {str(e)}").send()

@cl.action_callback("View Jobs")
async def view_jobs(action):
    job_scraper = JobScraper()
    jobs = job_scraper.get_all_jobs()

    for job in jobs:
        logo_url = job.get("logo_photo_url", "")
        title = job.get("title", "No Title")
        compensation = job.get("compensation", "Not specified")
        job_type = job.get("job_type", "Unknown")
        site = job.get("site", "No site")
        description = job.get("description", "No Description")
        apply_link = job.get("job_url_direct", "#")
        date_posted = job.get("date_posted", "No date")
        company_name = job.get("company", "No company")

        
        description_cutoff = description[:300] + "..." if len(description) > 300 else description
        # Escape HTML tags in the description
        description_cutoff = html.escape(description_cutoff)
        # Convert markdown to HTML if necessary
        description_cutoff = markdown.markdown(description_cutoff)

        if not description_cutoff:
            description_cutoff = "No Description Provided"

        if not logo_url:
            logo_url = "https://via.placeholder.com/50"

        if not job_type:
            job_type = "Unknown"

        card_content = f"""
        <div style="border: 0.5px solid #ddd; border-radius: 10px; padding: 16px; margin: 16px 0; max-width: 600px; box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);">
            <div style="display: flex; align-items: center;">
                <img src="{logo_url}" alt="Company Logo" style="width: 50px; height: 50px; object-fit: contain; margin-right: 16px;">
                <div style="flex-grow: 1;">
                    <h3 style="margin: 0; font-size: 18px; font-weight: bold;">{title}</h3>
                    <p style="margin: 4px 0 0; font-size: 14px; color: #555;">{company_name} - {job_type} - {site}</p>
                    <p style="margin: 4px 0 0; font-size: 14px; color: #888;">Posted on {date_posted}</p>
                </div>
            </div>
            <div style="margin-top: 16px;">
                <div style="margin: 0; font-size: 14px; color: #ddd;">
                    {description_cutoff}
                </div>
                <p style="margin: 8px 0 0; font-size: 14px; font-weight: bold; color: #333;">Compensation: {compensation}</p>
                <a href="{apply_link}" target="_blank" style="display: inline-block; margin-top: 16px; padding: 8px 16px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 4px;">Apply Now</a>
            </div>
        </div>
        """

        msg = await cl.Message(content=card_content).send()

    await cl.Action(name="Purge Jobs", value="purge_jobs").send(for_id=msg.id)

@cl.on_chat_start
async def on_chat_start():
    config = utils.load_config()
    
    settings = [
        Select(
            id="Open AI model",
            label="Choose a Model",
            values=["gpt-3.5-turbo", "gpt-4"],
            initial_index=0
        ),
        TextInput(
            id="location",
            label="Location",
            initial=config.get("Job Search", {}).get("location", "")
        ),
        NumberInput(
            id="distance",
            label="Distance",
            initial=config.get("Job Search", {}).get("distance", 50),
            min=0,
            max=1000
        ),
        Select(
            id="job_type",
            label="Job Type",
            values=["Any", "Full Time", "Part Time", "Contract", "Internship"],
            initial_index=0,
            multiple=True
        ),
        Switch(
            id="is_remote",
            label="Is Remote",
            initial=config.get("Job Search", {}).get("is_remote", True)
        ),
        NumberInput(
            id="results_wanted",
            label="Results Wanted",
            initial=config.get("Job Search", {}).get("results_wanted", 10),
            min=1,
            max=100
        ),
        Switch(
            id="easy_apply",
            label="Easy Apply",
            initial=config.get("Job Search", {}).get("easy_apply", False)
        ),
        TextInput(
            id="country_indeed",
            label="Country",
            initial=config.get("Job Search", {}).get("country_indeed", "india")
        ),
        NumberInput(
            id="hours_old",
            label="Hours Old",
            initial=config.get("Job Search", {}).get("hours_old", 24),
            min=0,
            max=168  # 1 week
        )
    ]
    await cl.ChatSettings(settings).send()
    resume_file_path = config.get("Resume", {}).get("resumeFilePath", "")

    if not os.path.exists(resume_file_path):
        msg = await cl.Message(content="No resume found. Please upload your resume.").send()
        await cl.Action(name="Upload Resume", value="upload_resume").send(for_id=msg.id)
    elif not os.path.exists("jobs.db"):
        msg = await cl.Message(content="Resume found, but no jobs synced yet.").send()
        await cl.Action(name="Sync Jobs", value="sync_jobs").send(for_id=msg.id)
    else:
        msg = await cl.Message(content="Jobs are available.").send()
        await cl.Action(name="View Jobs", value="view_jobs").send(for_id=msg.id)
        await cl.Action(name="Purge Jobs", value="purge_jobs").send(for_id=msg.id)

if __name__ == "__main__":
    cl.run()
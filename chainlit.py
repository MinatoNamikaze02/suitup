import chainlit as cl
import os
import shutil
import json
import toml
import traceback

import AI.utils as vanna_utils
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

global_settings = {}

@cl.step(type="run", name="Jobs Analyst")
async def chain(human_query: str):
    config = utils.load_config()
    sql_query = await vanna_utils.gen_query(human_query)
    result, error = await vanna_utils.execute_query(sql_query)

    if error:
        await cl.Message(content=result, author="Jobs Analyst").send()
        return

    if config.get("Display", {}).get("display_as_markdown", False):
        await cl.Message(content=result.to_markdown(), author="Jobs Analyst").send()
    else:
        for jobs in result.to_dict(orient="records"):
            card_content = utils.jobs_to_valid_html(jobs)
            await cl.Message(content=card_content, author="Jobs Analyst").send()

@cl.on_settings_update
async def handle_settings_update(settings: dict):
    try:
        config = utils.load_config()
                
        for key, value in settings.items():
            if key in config["JobSearch"]:
                config["JobSearch"][key] = value
            if key in config["GenAI"]:
                config["GenAI"][key] = value
            if key in config["Display"]:
                config["Display"][key] = value

        # Save updated settings
        utils.save_config(config)

        await cl.Message(content="Settings updated successfully", author="Jobs Analyst").send()
    except Exception as e:
        await cl.Message(content=f"Error updating settings: {str(e)}", author="Jobs Analyst").send()

@cl.on_message
async def on_message(message: cl.Message):
    if not os.path.exists("jobs.db"):
        await cl.Message(content="No jobs synced yet. Please sync jobs first.").send()
        return
    await chain(message.content)

@cl.action_callback("Sync Jobs")
async def sync_jobs(action):
    try:
        config = utils.load_config()
        resume_file_path = config.get("Resume", {}).get("resumeFilePath", "")
        if not os.path.exists(resume_file_path):
            await cl.Message(content="Resume file not found", author="Jobs Analyst").send()
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

        msg = await cl.Message(content="Jobs synced successfully", author="Jobs Analyst").send()
        await cl.Action(name="View Jobs", value="view_jobs").send(for_id=msg.id)
    except Exception as e:
        logger.error(traceback.format_exc())
        await cl.Message(content=f"Error syncing jobs: {str(e)}", author="Jobs Analyst").send()

@cl.action_callback("Upload New Resume")
async def upload_new_resume(action):
    config = utils.load_config()

    files = await cl.AskFileMessage(
        content="Please upload your resume to continue", accept=["text/plain", "application/pdf"]
    ).send()

    if os.path.exists(config.get("Resume", {}).get("resumeFilePath", "")):
        os.remove(config.get("Resume", {}).get("resumeFilePath", ""))

    if files:
        resume = files[0]
        try:
            file_path = os.path.join(UPLOAD_DIR, resume.name)
            # read the pdf contents
            with open(resume.path, "rb") as content:
                resume_content = content.read()

            with open(file_path, "wb") as buffer:
                buffer.write(resume_content)

            config['Resume']['resumeFilePath'] = file_path

            with open(CONFIG_PATH, 'w') as config_file:
                toml.dump(config, config_file)

            if os.path.exists("user_info.json"):
                os.remove("user_info.json")

            msg = await cl.Message(content=f"Resume uploaded: {resume.name}", author="Jobs Analyst").send()
            await cl.Action(name="Sync Jobs", value="sync_jobs").send(for_id=msg.id)
        except Exception as e:
            await cl.Message(content=f"Error uploading resume: {str(e)}", author="Jobs Analyst").send()


@cl.action_callback("Upload Resume")
async def upload_resume(action):
    files = await cl.AskFileMessage(
        content="Please upload your resume to continue", accept=["text/plain", "application/pdf"]
    ).send()

    if files:
        resume = files[0]
        try:
            file_path = os.path.join(UPLOAD_DIR, resume.name)

            # read the pdf contents
            with open(resume.path, "rb") as content:
                resume_content = content.read()

            with open(file_path, "wb") as buffer:
                buffer.write(resume_content)

            config = utils.load_config()
            config['Resume']['resumeFilePath'] = file_path

            with open(CONFIG_PATH, 'w') as config_file:
                toml.dump(config, config_file)

            if os.path.exists("user_info.json"):
                os.remove("user_info.json")

            msg = await cl.Message(content=f"Resume uploaded: {resume.name}", author="Jobs Analyst").send()
            await cl.Action(name="Sync Jobs", value="sync_jobs").send(for_id=msg.id)
        except Exception as e:
            await cl.Message(content=f"Error uploading resume: {str(e)}", author="Jobs Analyst").send()

@cl.action_callback("Reset cache seed")
async def reset_cache_seed(action):
    # delete .cache folder
    if os.path.exists(".cache"):
        shutil.rmtree(".cache")

    if os.path.exists("user_info.json"):
        os.remove("user_info.json")

    msg = await cl.Message(content="Cache seed reset successfully", author="Jobs Analyst").send()
    await cl.Action(name="Sync Jobs", value="sync_jobs", author="Jobs Analyst").send(for_id=msg.id)

@cl.action_callback("Purge Jobs")
async def purge_jobs(action):
    try:
        if os.path.exists("jobs.db"):
            os.remove("jobs.db")
        msg = await cl.Message(content="Jobs purged successfully", author="Jobs Analyst").send()
        await cl.Action(name="Sync Jobs", value="sync_jobs").send(for_id=msg.id)
        await cl.Action(name="Upload New Resume", value="upload_resume").send(for_id=msg.id)
        await cl.Action(name="Reset cache seed", value="reset_cache_seed").send(for_id=msg.id)
    except Exception as e:
        await cl.Message(content=f"Error purging jobs: {str(e)}", author="Jobs Analyst").send()

@cl.action_callback("View Jobs")
async def view_jobs(action):
    job_scraper = global_settings.get("job_scraper")
    jobs = job_scraper.get_all_jobs()

    msg = await cl.Message(content="Jobs Scraped:", author="Jobs Analyst").send()
    for job in jobs:
        card_content = utils.jobs_to_valid_html(job)
        msg = await cl.Message(content=card_content).send()

    await cl.Action(name="Purge Jobs", value="purge_jobs").send(for_id=msg.id)

@cl.on_chat_start
async def on_chat_start():
    config = utils.load_config()
    job_scraper = JobScraper()
    
    global_settings["job_scraper"] = job_scraper
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
            values=["fulltime", "parttime", "contract", "internship"],
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

        Switch(
            id="display_as_markdown",
            label="Display as Markdown",
            initial=config.get("Display", {}).get("display_as_markdown", False)
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
        msg = await cl.Message(content="No resume found. Please upload your resume.",  author="Jobs Analyst").send()
        await cl.Action(name="Upload Resume", value="upload_resume").send(for_id=msg.id)
    elif not os.path.exists("jobs.db"):
        msg = await cl.Message(content="Resume found, but no jobs synced yet.", author="Jobs Analyst").send()
        await cl.Action(name="Sync Jobs", value="sync_jobs").send(for_id=msg.id)
        await cl.Action(name="Upload New Resume", value="upload_resume").send(for_id=msg.id)
        await cl.Action(name="Reset cache seed", value="reset_cache_seed").send(for_id=msg.id)
    else:
        msg = await cl.Message(content="Jobs are available.", author="Jobs Analyst").send()
        await cl.Action(name="View Jobs", value="view_jobs").send(for_id=msg.id)
        await cl.Action(name="Purge Jobs", value="purge_jobs").send(for_id=msg.id)

if __name__ == "__main__":
    cl.run()
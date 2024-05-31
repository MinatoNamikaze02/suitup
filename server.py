import json
import os
import traceback

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from dotenv import load_dotenv
import shutil
import toml

import utils
from AI.keyword_extraction import ResumeTool
from search.job_search import JobScraper
from search.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

app = FastAPI()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.toml")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_resume(resume: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, resume.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        # Save resume file path to config.toml
        config = utils.load_config()
        config['Resume']['resumeFilePath'] = file_path
        with open(CONFIG_PATH, 'w') as config_file:
            toml.dump(config, config_file)
        return JSONResponse(content={"filename": resume.filename})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/uploads")
async def get_uploads():
    uploads = os.listdir(UPLOAD_DIR)
    return JSONResponse(content={"uploads": uploads})

@app.post("/api/sync")
async def sync_jobs():
    try:
        # Load config
        config = utils.load_config()

        # Load resume file path
        # Load resume file path
        resume_file_path = config.get("Resume", {}).get("resumeFilePath", "")
        if not os.path.exists(resume_file_path):
            raise HTTPException(status_code=400, detail="Resume file not found")

        # Extract details from resume
        resume_ext = ResumeTool(model="gpt-3.5-turbo")
        resume_details = resume_ext.extract_resume_details(resume_file_path)
        dict_repr = resume_details[0].dict()

        # Save user info to JSON file
        with open("user_info.json", "w") as f:
            json.dump(dict_repr, f)

        # Extract job search settings
        job_search_settings = resume_ext.extract_job_search_details(dict_repr)

        # Apply default values for empty AI results
        for key, value in job_search_settings.items():
            if not value:
                job_search_settings[key] = config.get("JobSearch", {}).get(key, value)

        logger.info(f"Job search settings: {job_search_settings}")

        # Initialize job scraper
        job_scraper = JobScraper()
        args = config.get("JobSearch", {})
        args.update(job_search_settings)

        # Scrape jobs
        temp = args.get("search_term", [])
        for term in temp:
            args["search_term"] = term
            job_scraper.scrape_and_save(**args)

        # Retrieve and order jobs
        jobs = job_scraper.get_all_jobs()
        # user_info = json.load(open("user_info.json", "r"))
        # jobs = job_ordering.JobOrderingChain(model="gpt-3.5-turbo-instruct").order_jobs(jobs, user_info)

        return JSONResponse(content=jobs)
    
    except Exception as e:
        # Log full stack trace
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/api/old")
async def sync_jobs_old():
    job_scraper = JobScraper()
    content = job_scraper.get_all_jobs()

    if not content:
        raise HTTPException(status_code=404, detail="No jobs found")

    return JSONResponse(content=content)

@app.post("/api/settings")
async def save_settings(settings: dict):
    try:
        # Load existing settings
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as config_file:
                existing_settings = toml.load(config_file)
        else:
            existing_settings = {}

        # Update the existing settings with the new ones
        for key, value in settings.items():
            if isinstance(value, dict) and key in existing_settings:
                existing_settings[key].update(value)
            else:
                existing_settings[key] = value

        # Write the updated settings back to the file
        with open(CONFIG_PATH, 'w') as config_file:
            toml.dump(existing_settings, config_file)
        
        return JSONResponse(content=existing_settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
async def load_settings():
    try:
        with open(CONFIG_PATH, 'r') as config_file:
            settings = toml.load(config_file)
        return settings
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)



from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import uuid

from jobspy import scrape_jobs
from .logger import get_logger

Base = declarative_base()
logger = get_logger(__name__)

class JobPost(Base):
    __tablename__ = 'job_posts'
    id = Column(String, primary_key=True)
    site = Column(String, nullable=True)
    job_url = Column(String, nullable=True)
    job_url_direct = Column(String, nullable=True)
    title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    date_posted = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    interval = Column(String, nullable=True)
    min_amount = Column(String, nullable=True)
    max_amount = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    is_remote = Column(String, nullable=True)
    job_function = Column(String, nullable=True)
    emails = Column(String, nullable=True)
    description = Column(String, nullable=True)
    company_industry = Column(String, nullable=True)
    company_url = Column(String, nullable=True)
    company_url_direct = Column(String, nullable=True)
    company_addresses = Column(String, nullable=True)
    company_num_employees = Column(String, nullable=True)
    company_revenue = Column(String, nullable=True)
    company_description = Column(String, nullable=True)
    search_term = Column(String, nullable=True)

def setup_database(database_uri='sqlite:///jobs.db'):
    engine = create_engine(database_uri)
    Base.metadata.create_all(engine)
    return engine

class JobScraper:
    def __init__(self, database_uri='sqlite:///jobs.db'):
        self.engine = create_engine(database_uri)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def generate_unique_id(self, row):
        return str(uuid.uuid4())
    
    def do_jobs_exist_in_db(self):
        return self.session.query(self.session.query(JobPost).exists()).scalar()
    
    def get_all_jobs(self):
        jobs = self.session.query(JobPost).all()
        self.session.close()
        jobs_json = []
        for job in jobs:
            job_dict = job.__dict__
            job_dict.pop('_sa_instance_state')
            jobs_json.append(job_dict)

        return jobs_json
    
    def purge_jobs(self):
        self.session.query(JobPost).delete()
        self.session.commit()
        self.session.close()
    
    def process_df(self, df):
        df = df.fillna('')

        # Convert all columns to string type
        for column in df.columns:
            df[column] = df[column].astype(str)

        # drop id column if it exists
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        
        return df
    
    def scrape_and_save(self, site_name, search_term, location="", distance=50, job_type="", proxy=None,
                       is_remote=False, results_wanted=50, easy_apply=False, linkedin_fetch_description=False,
                       linkedin_company_ids=None, description_format="markdown", country_indeed="india",
                       offset=0, hours_old=72, verbose=2, hyperlinks=False):
        logger.info(f"Scraping job posts for search term: {search_term}")
        jobs = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            location=location,
            distance=distance,
            job_type=job_type,
            proxy=proxy,
            is_remote=is_remote,
            results_wanted=results_wanted,
            easy_apply=easy_apply,
            linkedin_fetch_description=linkedin_fetch_description,
            linkedin_company_ids=linkedin_company_ids,
            description_format=description_format,
            country_indeed=country_indeed,
            offset=offset,
            hours_old=hours_old,
            verbose=verbose,
            hyperlinks=hyperlinks
        )        
        logger.info("Job posts scraped successfully!")

        # Get valid fields from JobPost
        valid_fields = {column.name for column in JobPost.__table__.columns}

        # Process the DataFrame
        df = self.process_df(jobs)

        # Filter out any columns not in the JobPost schema
        df = df[[col for col in df.columns if col in valid_fields]]

        # Add any missing columns from the schema that aren't in the DataFrame
        for field in valid_fields:
            if field not in df.columns and field != 'id' and field != 'search_term':
                df[field] = ''

        session = self.Session()
        jobs_cleaned = df.where(pd.notnull(df), None)

        for _, row in jobs_cleaned.iterrows():
            job_dict = row.to_dict()
            job_dict['id'] = self.generate_unique_id(row)
            job_dict['search_term'] = search_term
            job_post = JobPost(**job_dict)
            session.add(job_post)

        try:
            session.commit()
            logger.info("Job posts saved successfully!")
        except Exception as e:
            logger.error(f"Error saving job posts: {e}")
            session.rollback()
            raise
        finally:
            session.close()

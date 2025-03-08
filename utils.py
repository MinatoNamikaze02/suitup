import toml
import html
import markdown

def load_config():
    try:
        with open("config.toml", 'r') as config_file:
            config = toml.load(config_file)
        return config
    except Exception as e:
        raise e
    
def save_config(config):
    with open("config.toml", 'w') as config_file:
        toml.dump(config, config_file)

def jobs_to_valid_html(job):
    logo_url = job.get("logo_photo_url", "")
    title = job.get("title", "No Title")
    compensation = f"{job.get('min_amount', 'N/A')} - {job.get('max_amount', 'N/A')} {job.get('currency', '')}" if job.get("min_amount") and job.get("max_amount") else "Not specified"
    job_type = job.get("job_type", "Unknown")
    site = job.get("site", "No site")
    description = job.get("description", "No Description")
    apply_link = job.get("job_url_direct", job.get("job_url", "#"))
    date_posted = job.get("date_posted", "No date")
    company_name = job.get("company", "No company")
    location = job.get("location", "Location not specified")
    is_remote = job.get("is_remote", "Unknown")
    job_function = job.get("job_function", "Not specified")
    company_industry = job.get("company_industry", "Not specified")
    company_url = job.get("company_url", "")
    company_num_employees = job.get("company_num_employees", "Not specified")
    company_revenue = job.get("company_revenue", "Not specified")
    
    description_cutoff = description[:300] + "..." if len(description) > 300 else description
    description_cutoff = html.escape(description_cutoff)
    description_cutoff = markdown.markdown(description_cutoff)
    
    if not description_cutoff:
        description_cutoff = "No Description Provided"
    
    if not logo_url:
        logo_url = "https://via.placeholder.com/50"
    
    if not job_type:
        job_type = "Unknown"
    
    card_content = f"""
    <div style="border-radius: 15px; padding: 20px; margin: 20px 0; max-width: 650px; 
                background-color: #1e1e1e; color: #e0e0e0; font-family: Arial, sans-serif;
                box-shadow: 0 6px 15px rgba(255, 255, 255, 0.1);">
        <div style="display: flex; align-items: center;">
            <img src="{logo_url}" alt="Company Logo" style="width: 60px; height: 60px; object-fit: contain; 
                 margin-right: 20px; border-radius: 50%; background-color: #333; padding: 5px;">
            <div style="flex-grow: 1;">
                <h2 style="margin: 0; font-size: 22px; font-weight: 600; color: #ffffff;">{title}</h2>
                <p style="margin: 5px 0; font-size: 14px; color: #bbbbbb;">{company_name} | {location} | {job_type}</p>
                <p style="margin: 0; font-size: 14px; color: #888888;">Posted on {date_posted} | {is_remote}</p>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <p style="margin: 0; font-size: 16px; color: #cccccc;">{description_cutoff}</p>
            <div style="margin-top: 16px; font-size: 14px; color: #aaaaaa;">
                <strong>Compensation:</strong> {compensation} <br>
                <strong>Job Function:</strong> {job_function} <br>
                <strong>Company Industry:</strong> {company_industry} <br>
                <strong>Employees:</strong> {company_num_employees} <br>
                <strong>Revenue:</strong> {company_revenue}
            </div>
            <a href="{apply_link}" target="_blank" 
               style="display: inline-block; margin-top: 20px; padding: 12px 24px; background-color: #007bff; 
                      color: #ffffff; text-decoration: none; font-weight: bold; border-radius: 4px;">
                Apply Now
            </a>
        </div>
    </div>
    """
    return card_content

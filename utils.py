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

    return card_content
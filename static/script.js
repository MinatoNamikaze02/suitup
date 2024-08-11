window.onload = async function() {
    try {
        // Fetch settings data from the API
        const response = await fetch('/api/settings');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Settings:', data);

        // Update the settings form with the data
        document.getElementById("Open AI model").value = data.GenAI.openAIModel;

        document.getElementById("location").value = data.JobSearch.location;
        document.getElementById("distance").value = data.JobSearch.distance;
        document.getElementById("job_type").value = data.JobSearch.job_type;
        document.getElementById("is_remote").checked = data.JobSearch.is_remote;
        document.getElementById("results_wanted").value = data.JobSearch.results_wanted;
        document.getElementById("easy_apply").checked = data.JobSearch.easy_apply;
        document.getElementById("country_indeed").value = data.JobSearch.country_indeed;
        document.getElementById("hours_old").value = data.JobSearch.hours_old;

        // Find the file if already uploaded
        const fileResponse = await fetch('/api/uploads');
        if (!fileResponse.ok) {
            throw new Error(`HTTP error! status: ${fileResponse.status}`);
        }
        const fileData = await fileResponse.json();
        if (fileData.uploads.length > 0) {
            console.log('Uploaded file:', fileData.uploads[0]);
            document.getElementById("file-name").innerText = fileData.uploads[0];
            document.getElementById("uploaded-info").style.display = "flex";
            document.getElementById("purged-info").style.display = "flex";
            document.getElementById("upload-section").style.display = "none";
        } else {
            alert('No Resume uploaded.');
            return
        }

        const jobsResponse = await fetch('/api/old');
        if (!jobsResponse.ok) {
            throw new Error(`HTTP error! status: ${jobsResponse.status}`);
        }
        const jobs = await jobsResponse.json();
        if (!jobs.length) {
            alert('No jobs found. Please sync with AI to get job listings.');
            return
        }
        displayJobListings(jobs);

    } catch (error) {
        console.error('Error loading settings:', error);
        alert('Failed to load settings.');
    }
}
function openSidebar() {
    document.getElementById("sidebar").style.width = "500px";
}

function closeSidebar() {
    document.getElementById("sidebar").style.width = "0";
}

async function saveSettings() {
    const openAIModelSelect = document.getElementById("Open AI model");
    const location = document.getElementById("location").value;
    const distance = document.getElementById("distance").value;
    const job_type = document.getElementById("job_type").value;
    const is_remote = document.getElementById("is_remote").checked;
    const results_wanted = document.getElementById("results_wanted").value;
    const easy_apply = document.getElementById("easy_apply").checked;
    const country_indeed = document.getElementById("country_indeed").value;
    const hours_old = document.getElementById("hours_old").value;

    const settings = {
        GenAI: {
            openAIModel: openAIModelSelect.options[openAIModelSelect.selectedIndex].value,
        },
        JobSearch: {
            location,
            distance: parseInt(distance),
            job_type,
            is_remote,
            results_wanted: parseInt(results_wanted),
            easy_apply,
            country_indeed,
            hours_old: parseInt(hours_old),
        }
    };

    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        alert("Settings saved!");
        closeSidebar();
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('Failed to save settings.');
    }
}

async function syncWithAI() {
    const syncBtn = document.querySelector('.sync-btn');
    syncBtn.classList.add('loading');
    syncBtn.disabled = true;

    console.log('Syncing jobs with AI...');

    try {
        const response = await fetch('/api/sync', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jobs = await response.json();

        // Handle successful sync and display jobs
        displayJobListings(jobs);
        alert("Jobs synced successfully!");
    } catch (error) {
        console.error('Error syncing jobs:', error);
        alert('Failed to sync jobs.');
    } finally {
        syncBtn.classList.remove('loading');
        syncBtn.disabled = false;
    }
}

async function purgeFromDB() {
    const purgeBtn = document.querySelector('.purge-btn');
    purgeBtn.classList.add('loading');

    console.log('Purging jobs from AI...');
    try {
        const response = await fetch('/api/jobs/purge', {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        alert("Jobs purged successfully!");
    } catch (error) {
        console.error('Error purging jobs:', error);
        alert('Failed to purge jobs.');
    }
    purgeBtn.classList.remove('loading');
}

function displayJobListings(jobs) {
    const container = document.querySelector('.job-listings');

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.classList.add('job-card');

        // Top section of the card
        const topSection = document.createElement('div');
        topSection.classList.add('job-card-top');

        // Company Logo
        const logo = document.createElement('img');
        logo.src = job.logo_photo_url || 'https://media.istockphoto.com/id/1142192548/vector/man-avatar-profile-male-face-silhouette-or-icon-isolated-on-white-background-vector.jpg?s=2048x2048&w=is&k=20&c=lyki7QHyULuJNNheEf-BI_DQNCDi2NRYMfVGTQj_4UM=';
        logo.alt = job.company || 'Unknown Company';
        logo.classList.add('job-logo');
        topSection.appendChild(logo);

        // Company and Time Info
        const companyInfo = document.createElement('div');
        companyInfo.classList.add('company-info');
        const company = document.createElement('p');
        company.classList.add('job-company');
        company.innerText = job.company || 'Unknown Company';
        const timePosted = document.createElement('p');
        timePosted.classList.add('job-time-posted');
        timePosted.innerText = job.date_posted || 'Unknown Date';
        companyInfo.appendChild(company);
        companyInfo.appendChild(timePosted);
        topSection.appendChild(companyInfo);

        // Title and Type
        const title = document.createElement('h3');
        title.classList.add('job-title');
        title.innerText = job.title || 'Unknown Title';

        const jobType = document.createElement('span');
        jobType.classList.add('job-type');
        jobType.innerText = job.job_type || 'Unknown Job Type';

        jobCard.appendChild(topSection);
        jobCard.appendChild(title);
        jobCard.appendChild(jobType);

        // Adding top section to job card
        jobCard.appendChild(topSection);

        // Description
        const description = document.createElement('p');
        description.classList.add('job-description');
        description.innerHTML = job.description ? marked.parse(job.description.substring(0, 100)) + '...' : 'No description available';
        jobCard.appendChild(description);

        // Apply Link
        const link = document.createElement('a');
        link.href = job.job_url_hyper ? job.job_url_hyper.match(/href="([^"]*)"/)[1] : '#';
        link.innerText = 'Apply';
        link.target = '_blank';
        link.classList.add('apply-btn');
        jobCard.appendChild(link);

        container.appendChild(jobCard);

        // // Additional Details Section
        // const detailsSection = document.createElement('div');
        // detailsSection.classList.add('details-section');

        // // Location
        // const location = document.createElement('p');
        // location.classList.add('job-location');
        // location.innerText = `Location: ${job.location || 'Location not specified'}`;
        // detailsSection.appendChild(location);

        // // Compensation
        // const compensation = document.createElement('p');
        // compensation.classList.add('job-compensation');
        // compensation.innerText = job.min_amount && job.max_amount ?
        //     `Compensation: ${job.min_amount} - ${job.max_amount} ${job.currency || ''}` :
        //     'Compensation: Not specified';
        // detailsSection.appendChild(compensation);

        // // Add the details section below the job card
        // container.appendChild(detailsSection);
    });
}


async function handleFileUpload(event) {
    uploadBtn = document.getElementById("upload-section");
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append("resume", file);

        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById("file-name").innerText = data.filename;
            document.getElementById("uploaded-info").style.display = "flex";
            document.getElementById("purged-info").style.display = "flex";
            uploadBtn.style.display = "none";
        } else {
            alert("Failed to upload file.");
        }
    }
}
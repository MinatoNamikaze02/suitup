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
        select = document.getElementById("Open AI model");
        select.value = data.openAIModel;

        // find the file if already uploaded
        const fileResponse = await fetch('/api/uploads');
        if (!fileResponse.ok) {
            throw new Error(`HTTP error! status: ${fileResponse.status}`);
        }
        const fileData = await fileResponse.json();
        if (fileData.uploads.length > 0) {
            document.getElementById("file-name").innerText = fileData.uploads[0];
            document.getElementById("uploaded-info").style.display = "flex";
            document.getElementById("upload-section").style.display = "none";
        }

        const jobsResponse = await fetch('/api/old');
        if (!jobsResponse.ok) {
            throw new Error(`HTTP error! status: ${jobsResponse.status}`);
        }
        const jobs = await jobsResponse.json();
        displayJobListings(jobs);

    } catch (error) {
        console.error('Error loading settings:', error);
        alert('Failed to load settings.');
    }
}

function openSidebar() {
    document.getElementById("sidebar").style.width = "250px";
}

function closeSidebar() {
    document.getElementById("sidebar").style.width = "0";
}

async function saveSettings() {
    select = document.getElementById("Open AI model");
    const settings = {
        openAIModel: select.options[select.selectedIndex].value,
    };
    try {
        // Send settings data to the API
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

function displayJobListings(jobs) {
    const container = document.createElement('div');
    
    container.classList.add('job-listings');

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.classList.add('job-card');

        const logo = document.createElement('img');
        logo.src = job.logo_photo_url || 'https://media.istockphoto.com/id/1205270037/photo/question-mark-on-speech-bubble.jpg?s=2048x2048&w=is&k=20&c=OhpGGcQv2dB31ly7yqcn9b0GDJAM6XTKEdWHu8DhWJc=';
        logo.alt = job.company || 'Unknown Company';
        logo.classList.add('job-logo');
        jobCard.appendChild(logo);

        const title = document.createElement('h3');
        title.innerText = job.title || 'Unknown Title';
        jobCard.appendChild(title);

        const company = document.createElement('p');
        company.classList.add('job-company');
        company.innerText = job.company || 'Unknown Company';
        jobCard.appendChild(company);

        const description = document.createElement('p');
        description.classList.add('job-description');
        description.innerText = job.description ? job.description.substring(0, 200) + '...' : 'No description available';
        jobCard.appendChild(description);

        const link = document.createElement('a');
        link.href = job.job_url_direct || 'https://www.google.com';
        link.innerText = 'Read More';
        link.target = '_blank';
        jobCard.appendChild(link);

        container.appendChild(jobCard);
    });

    // Remove existing job listings if any
    const existingContainer = document.querySelector('.job-listings');
    if (existingContainer) {
        existingContainer.remove();
    }

    // Append the new job listings
    document.body.appendChild(container);
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
            uploadBtn.style.display = "none";
        } else {
            alert("Failed to upload file.");
        }
    }
}
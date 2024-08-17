## Suit Up
Suit Up is an intelligent job tracking tool that combines the power of Generative AI and [jobspy](https://github.com/Bunsly/JobSpy) to help you keep track of jobs that match your skills. Simply upload your resume, and Suit Up will sync and display job listings from multiple sources, all in one place.

## What it does?

- Converts resume into json through an extraction chain.
- identifies specific information (like location and search terms) which is used to scrape alongside other filters from multiple sources like linkedin, indeed, etc

## Why use this?
- Firstly, this removes the painful process of manually searching for jobs in different listing websites.
- For the rare ones who are way too talented and apply to several roles, this tool does multiple role searches in one go.

## How it looks?
![implementation.png](https://github.com/MinatoNamikaze02/suitup/blob/master/assets/Screenshot%202024-08-17%20at%2012.42.34.png)
![implementation2.png](https://github.com/MinatoNamikaze02/suitup/blob/master/assets/Screenshot%202024-08-17%20at%2012.42.48.png)

## What could go wrong?
- Sync Errors: Occasionally, the tool might fail to sync, showing an error message like "Failed to sync." This usually happens because the initial extraction chain encountered an issue, which is expected with LLMs. If this occurs, simply retrigger the process, and it should work correctly.
- Speed Issues: It could take a minute or two to load up. Check the logs for more info.
- Jobpsy has certain rate limiting controls. If you want to tinker with the code to bring in proxies, be my guest.

## Notes
This is a tool meant for personal use.

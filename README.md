## Suit Up
Suit Up is an intelligent job scraping tool that combines the power of Generative AI and [jobspy](https://github.com/Bunsly/JobSpy) to help you keep track of jobs that match your skills. Simply upload your resume, and Suit Up will sync and display job listings from multiple sources, all in one place. 

## What it does?

- Converts resume into json through an extraction chain.
- Uses an [autogen](https://microsoft.github.io/autogen/) group chat to identify potential search terms (roles), job types(fulltime, parttime, contract, internships) and location preferences.

## Why use this?
- Firstly, this removes the painful process of manually searching for jobs in different listing websites.
- For the rare ones who are way too talented and apply to several roles, this tool does multiple role searches in one go.
- Uses vanna to let you filter and interact with the data using textual queries.

## How to use
1. Setup vanna and open ai
  - Get your vanna credentials [here](https://vanna.ai/) and populate your `.env` based on `config.py` in root.
  - Get your open ai api key and add it to `.env`
2. Install Requirements
```
$ pip install -r requirements.txt
```
3. Train vanna
```
$ python AI/training.py
```
4. Run the App
```
$ chainlit run chainlit.py
```

## How it looks?
![implementation.png](https://github.com/MinatoNamikaze02/suitup/blob/master/assets/Screenshot%202024-08-17%20at%2015.02.22.png)
![implementation2.png](https://github.com/MinatoNamikaze02/suitup/blob/master/assets/Screenshot%202024-08-17%20at%2015.02.53.png)
![implementation3.png](https://github.com/MinatoNamikaze02/suitup/blob/master/assets/Screenshot%202024-08-17%20at%2015.03.07.png)

## What could go wrong?
- Sync Errors: Occasionally, the tool might fail to sync. This usually happens because the initial extraction chain encountered an issue, which is expected with LLMs. If this occurs, simply retrigger the process, and it should work correctly.
- Speed Issues: It could take a minute or two to load up. Check the logs for more info.
- Jobpsy has certain rate limiting controls. If you want to tinker with the code to bring in proxies, be my guest.

## Notes
This is a tool meant for personal use.

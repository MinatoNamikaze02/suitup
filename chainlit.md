## Suit Up
Suit Up is a smart job search assistant that leverages Generative AI and [Jobspy](https://github.com/Bunsly/JobSpy) to track job opportunities that match your skills. By simply uploading your resume, Suit Up will scan and display relevant job listings from multiple sources, all in one centralized location. 

## What it does?

- Converts resume into json through an extraction chain.
- Uses an [autogen](https://microsoft.github.io/autogen/) group chat to identify potential search terms (roles), job types(fulltime, parttime, contract, internships) and location preferences.
- Uses [Jobpsy](https://github.com/Bunsly/JobSpy) to search for jobs based on preferences.
- Uses [Vanna](https://vanna.ai/) to let you control the data with simple human language.

## What you can do with it?
- At any point of time you can
  - Sync for a resume
  - Modify the resume
  - Retry extraction process for the same resume with a new seed
  - Change location, radius of search, job type, remote jobs, result count and much more.
  - Display as markdown or card-layout, whatever you like.
  - Control what model you want to be using.
  - **Filter and play around with the data with simple text queries**

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

### Settings
You can edit the settings and save them directly from the chainlit web client [http://localhost:8000](http://localhost:8000).
The following settings are available:
```
model: Options["gpt-3.5-turbo", "gpt-4"]
location: str (CITY, STATE)
distance: int
Job Type: Options["Any" , "fulltime", "parttime", "contract", "internship"]
is_remote: bool
results_wanted: int
easy_apply: bool (only for linkedIn)
display as markdown: bool (this is to enable tablular view of data)
country: str
hours_old: int
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

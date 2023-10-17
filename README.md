# linked-linkedin
Linkedin Web Scraper that can be customized
The scraper file consists of a couple of functions:
1. create_driver() opens a headless driver - it is fairly important that we use a headless version as the runtime can be reduced (and selenium can be very slow)
2. get_user_credentials() will ask for user input when logging in.
3. login_linkedin(username, password) logs in to linkedin
4. collect_links(username, password, locations, positions) after logging in.
5. scrape_linkedin_job(job_url) scrapes all information given a URL. One can also just collect the links and then use beautiful soup for parsing, but the job description is loaded dynamically after clicking "see more". 
The CSS selectors are based on the fact that one looks at the site while logged in - these can easily be changed.
6. main() defines locations, job tags, then creates a driver, collects the links, parses them and writes the output to a JSON file.

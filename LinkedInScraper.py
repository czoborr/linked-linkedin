import json
import multiprocessing
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd  # This import is only necessary if you want to load something from the outside or write data in DF.


def create_driver():
    options = Options()
    options.add_argument("--headless")  # Run headless browser
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    return driver


def get_user_credentials():
    username = input("Enter your LinkedIn username: ")
    password = input("Enter your LinkedIn password: ")
    return username, password


def login_linkedin(username, password):
    driver = create_driver()

    try:
        # open website
        driver.get('https://www.linkedin.com/login')
        driver.implicitly_wait(10)

        # Accept cookies
        driver.find_element(By.XPATH,
                            '//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[1]').click()

        # Fill in credentials
        driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)

        # Login button - wait until clickable?
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="organic-div"]/form/div[3]/button'))
        )
        driver.execute_script("arguments[0].scrollIntoView();", sign_in_button)
        sign_in_button.click()

        return driver
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return None


def collect_links(username, password, locations, positions):
    # It is not strictly necessary to login, but in that case, one needs to rename the CSS selectors and class names,
    # as the structure of the website and namings are different.
    driver = login_linkedin(username, password)
    links = []

    for location in locations:
        for position in positions:

            driver.get("https://www.linkedin.com/jobs/search/?keywords={}&location={}".format(position, location))
            print("https://www.linkedin.com/jobs/search/?keywords={}&location={}".format(position, location))

            try:
                for page in range(1, 40):
                    time.sleep(2)
                    jobs_block = driver.find_element(By.CLASS_NAME, 'jobs-search-results-list')
                    jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')

                    for job in jobs_list:
                        all_links = job.find_elements(By.TAG_NAME, 'a')
                        for a in all_links:
                            if str(a.get_attribute('href')).startswith(
                                    "https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links:
                                links.append(a.get_attribute('href'))
                            else:
                                pass
                        # scroll down for each job element
                        driver.execute_script("arguments[0].scrollIntoView();", job)

                    print(f'Collecting the links in the page: {page - 1}')
                    # go to next page:
                    driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']").click()
                    time.sleep(3)
            except:
                pass
            print('Found ' + str(len(links)) + ' links for job offers')

    return links


def scrape_linkedin_job(job_url):
    try:
        driver = create_driver()  # Create a new WebDriver instance for each job URL
        driver.get(job_url)
        driver.implicitly_wait(7)
        driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/div/section[1]/div/div/section/button[1]').click()

        scraped_data = {
            "job_title": driver.find_element(By.TAG_NAME, "h1").text,
            "company_name": driver.find_element(By.CSS_SELECTOR, '#main-content > section.core-rail.mx-auto.papabear'
                                                                 '\:w-core-rail-width.mamabear\:max-w-\['
                                                                 '790px\].babybear\:max-w-\[790px\] > div > '
                                                                 'section.top-card-layout.container-lined.overflow'
                                                                 '-hidden.babybear\:rounded-\[0px\] > div > '
                                                                 'div.top-card-layout__entity-info-container.flex.flex'
                                                                 '-wrap.papabear\:flex-nowrap > div > h4 > '
                                                                 'div:nth-child(1) > span:nth-child(1)').text,
            "company_location": driver.find_element(By.CSS_SELECTOR, '#main-content > '
                                                                     'section.core-rail.mx-auto.papabear\:w-core-rail'
                                                                     '-width.mamabear\:max-w-\['
                                                                     '790px\].babybear\:max-w-\[790px\] > div > '
                                                                     'section.top-card-layout.container-lined.overflow'
                                                                     '-hidden.babybear\:rounded-\[0px\] > div > '
                                                                     'div.top-card-layout__entity-info-container.flex'
                                                                     '.flex-wrap.papabear\:flex-nowrap > div > h4 > '
                                                                     'div:nth-child(1) > '
                                                                     'span.topcard__flavor.topcard__flavor--bullet').text,
            "post_date": driver.find_element(By.CSS_SELECTOR, '#main-content > section.core-rail.mx-auto.papabear\:w'
                                                              '-core-rail-width.mamabear\:max-w-\['
                                                              '790px\].babybear\:max-w-\[790px\] > div > '
                                                              'section.top-card-layout.container-lined.overflow-hidden'
                                                              '.babybear\:rounded-\[0px\] > div > '
                                                              'div.top-card-layout__entity-info-container.flex.flex'
                                                              '-wrap.papabear\:flex-nowrap > div > h4 > div:nth-child('
                                                              '2) > span').text,
            "job_description": driver.find_element(By.CLASS_NAME, "decorated-job-posting__details").text,
            "applicant_number": driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/section['
                                                              '2]/div/div[1]/div/h4/div[2]').text
        }
        print("Scraping done")
    except Exception as e:
        scraped_data = {"job_title": "None",
                        "company_name": "None",
                        "company_location": "None",
                        "post_date": "None",
                        "job_description": "None",
                        "applicant_number": "None"}
    finally:
        driver.quit()  # Make sure to quit the driver when done

    return scraped_data


def main():
    # Set locations
    locations = {'Germany', 'Austria', 'Switzerland'}
    # Set job titles
    positions = {'DataAnalyst', 'DataScientist', 'DataEngineer'}

    username, password = get_user_credentials()

    # Set the number of processes to use
    num_processes = multiprocessing.cpu_count()

    # List of LinkedIn profile URLs to scrape - if you have this list from an outside source, comment line 154 and 160
    links = collect_links(username, password, locations, positions)

    # In case you want to have the links in a separate file, uncomment
    # links_data = pd.DataFrame(links, columns=['Links'])
    # links_data.to_csv('All_links.csv')

    # Use in case have already collected urls
    # links = pd.read_csv('All_links.csv')['Links'].tolist()

    with multiprocessing.Pool(processes=num_processes) as pool:
        scraped_data_list = pool.map(scrape_linkedin_job, links)

    # Save the scraped data in JSON format
    with open("linkedin_data.json", "w", encoding="utf-8") as json_file:
        json.dump(scraped_data_list, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Scraping completed in {end_time - start_time} seconds.")

# For 5000 jobs the code runs in roughly 1.3 hours

# %%
import pandas as pd
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import langcodes as lc
import os
import re

# - Global variables
lang_code  = 'en'
sort_by = 'highest-rated' # popularity|newest
timeout = 15
csv_file_name = 'Udemy Free Courses.csv'

# %%
# - Choose language
# lc.get('en').display_name()
while True:
    language_name = input('Please type your language (or type x to quit): ')
    language_err = False
    lang_code = ''
    if language_name.lower().strip() == "x":
        exit(0)
        break
    try:
        lang_code = lc.find(language_name).language
    except LookupError as err:
        print(err)
        language_err = True
    except Exception as err:
        print("Something went wrong")
        print(type(err).__name__)
        language_err = True
    if not language_err: break

#print(lang_code)

# %%
# - Methods
def generate_page_dataframe(elements_collection):
    page_dataframe = pd.DataFrame()
    # - get list with all courses texts
    # all_text = [el.text for el in courses_elements]
    # - get list with all links
    links = [el.get_attribute('href') for el in elements_collection]
    page_dataframe['Url'] = links
    
    # - get list with all titles
    titles = [el.find_element_by_xpath(".//div[contains(@class,'course-card--course-title')]").text for el in elements_collection]
    page_dataframe['Course Title'] = titles
    
    # - get list with all headlines
    headlines = [el.find_element_by_xpath(".//*[contains(@data-purpose,'course-headline')]").text for el in elements_collection]
    page_dataframe['Course Headline'] = headlines
    
    # - get list with all authors
    authors = [el.find_element_by_xpath(".//*[contains(@data-purpose,'visible-instructors')]").text for el in elements_collection]
    page_dataframe['Course Author(s)'] = authors
    
    # - get list with all ratings
    ratings = [el.find_element_by_xpath(".//*[contains(@data-purpose,'rating-number')]").text for el in elements_collection]
    page_dataframe['Rating'] = ratings
    
    # - get list with all ratings number
    number_ratings = [re.sub(r'[()]', '', el.find_element_by_xpath(".//span[contains(@class,'course-card--reviews-text')]").text) for el in elements_collection]
    page_dataframe['Number of Ratings'] = number_ratings
    
    # - get list with all courses durations
    durations = [el.find_element_by_xpath(".//*[contains(@class,'course-card--course-meta-info')]/span[position()=1]").text for el in elements_collection]
    page_dataframe['Course Duration'] = durations
    
    # - get list with all courses lectures quantity
    number_lectures = [el.find_element_by_xpath(".//*[contains(@class,'course-card--course-meta-info')]/span[position()=2]").text for el in elements_collection]
    page_dataframe['Number of Lectures'] = number_lectures
    
    # - get list with all courses lectures levels of difficulty
    levels = [el.find_element_by_xpath(".//*[contains(@class,'course-card--course-meta-info')]/span[position()=3]").text for el in elements_collection]
    page_dataframe['Difficulty'] = levels
    return page_dataframe

# %%
# - Create driver with local binaries
try:
    driver_location = r"{0}/webdriver/geckodriver.exe".format(os.getcwd())
    # - Disable images for fsater scraping
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_binary = FirefoxBinary(r"{0}/FirefoxPortable/App/Firefox64/firefox.exe".format(os.getcwd()))
    driver = webdriver.Firefox(firefox_binary=firefox_binary, executable_path=driver_location, firefox_profile=firefox_profile)
except Exception as err:
    print('Sorry, but there was an error in launching the browser.')
    exit(0)
    
driver.implicitly_wait(timeout)

#print("driver OK")

# %%
# - main try/catch (try)

try:

    curr_page = 1
    url = 'https://www.udemy.com/courses/free/?lang={lang}&p={page}&sort={sort}'.format(lang=lang_code,page=curr_page,sort=sort_by)
    driver.get(url)
    
    last_page = int(driver.find_element_by_xpath("//a[contains(@class,'pagination--next')]/preceding-sibling::*[1]").text)
    
    output_df = pd.DataFrame()

    for curr_page in range(1,last_page + 1):
        if curr_page > 1:
            url = 'https://www.udemy.com/courses/free/?lang={lang}&p={page}&sort={sort}'.format(lang=lang_code,page=curr_page,sort=sort_by)
            driver.get(url)
        courses_elements = driver.find_elements_by_xpath("//*[contains(@class,'browse-course-card--link--3KIkQ')]")
        page_df = generate_page_dataframe(courses_elements)
        output_df = output_df.append(page_df)

    # - export CSV
    output_df.to_csv('Udemy Free Courses.csv',sep=";",index=False,encoding='utf-8-sig')
        
# - main try/catch  (catch)
except TimeoutException as err:
    print("Driver timeout after {0}s".format(timeout))
    exit(1)
except Exception as err:
    if "sibling" in str(err):
        print("Query doesn't return any course. Review languague name that you typed")
    else:
       print(err) 
    exit(1)
finally:
    driver.quit()  

print('CSV file exported at path: "{0}".'.format(os.path.realpath(__file__+"/{}".format(csv_file_name))))
print('Bye..')


import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login_linkedin(driver, email, password):
    wait = WebDriverWait(driver, 20)
    driver.get('https://www.linkedin.com/login')

    email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    password_input = driver.find_element(By.ID, "password")

    email_input.send_keys(email)
    password_input.send_keys(password)
    password_input.submit()


def scrape_jobs_on_page(driver):

    wait = WebDriverWait(driver, 60)
    job_cards = driver.find_elements(By.CSS_SELECTOR, "a[class*='job-card-container__link']")
    time.sleep(5)

    jobs = []
    for job_card in job_cards:

        driver.execute_script("arguments[0].click();", job_card)
        #job_card.click()

        ### job_title
        job_title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[class='ember-view']")))

        job_title = job_title_element.text
        print(job_title)

        # company
        company_element = driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name")
        company = company_element.text
        print(company)


        ### job_detail
        job_detail_element = driver.find_element(By.CSS_SELECTOR, ".jobs-description-content__text--stretch")
        job_detail = job_detail_element.text
        #print(job_detail)

        ### location
        location_element = driver.find_element(By.CSS_SELECTOR,".job-card-container__metadata-wrapper")
        location = location_element.text
        print(location)

        jobs.append({
            "Title": job_title,
            "Company": company,
            "Location": location,
            "Description": job_detail,
        })

        print(jobs)

    return jobs


def find_and_click_next_page(driver):
    try:
        # find "Next" button and click
        next_button = driver.find_element(By.CSS_SELECTOR, ".jobs-search-pagination__button--next")
        next_button.click()
        return True

    except (NoSuchElementException, ElementNotInteractableException):
        # if not found or not clickable, return False
        return False


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # wait



def main():
    # Conf
    EMAIL = ""              # fill your email
    PASSWORD = ""           # fill your password
    SEARCH_KEYWORD = "Data Engineer"    # fill your search keyword. ex: Data Engineer
    LOCATION = "Vietnam"

    # Init webdriver
    driver = webdriver.Chrome()
    driver.maximize_window()

    # login
    login_linkedin(driver, EMAIL, PASSWORD)
    time.sleep(5)

    # Define search URL
    print("Searching")

    search_url = f"https://www.linkedin.com/jobs/search/?keywords={SEARCH_KEYWORD.replace(' ', '%20')}&location={LOCATION.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(5)

    job_list_data = []

    page_number = 1
    while True:
        print(f"--- Đang lấy dữ liệu từ trang {page_number} ---")

        # scroll to bottom to load all jobs
        scroll_to_bottom(driver)

        # get all jobs on current page
        jobs_on_current_page = scrape_jobs_on_page(driver)
        job_list_data.extend(jobs_on_current_page)

        # Chuyển trang
        can_continue = find_and_click_next_page(driver)
        if not can_continue:
            print("Đã đến trang cuối cùng. Dừng lại.")
            break

        # Chờ trang mới tải xong trước khi tiếp tục vòng lặp
        time.sleep(3) 
        page_number += 1

        #if page_number == 3:
        #    break


    if job_list_data:
        df = pd.DataFrame(job_list_data)

        # Xóa các dòng trùng lặp
        df_unique = df.drop_duplicates()

        ## Save to .csv file
        #file_name = f"{SEARCH_KEYWORD.replace(' ', '_')}_all_jobs.csv"
        #df_unique.to_csv(file_name, index=False, sep = ';', encoding='utf-8-sig')

        ## Save to .xlsx file
        df_unique.to_excel('jobs_data.xlsx', index=False)
        print(f"Đã lưu {len(job_list_data)} job vào file 'jobs_data.xlsx' thành công!")
    else:
        print("Không có dữ liệu để lưu.")


if __name__ == "__main__":
    main()


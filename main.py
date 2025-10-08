from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import openpyxl
from openpyxl import Workbook
import psycopg2
import pandas as pd



def making_workbook():
    wb = Workbook()
    ws = wb.active
    ws.title = "Job Listings"
    ws.append(["Title", "Company", "Location", "Benefits"])
    wb.save("indeed_jobs.xlsx")
    
    return wb, ws


# driver = webdriver.Chrome()
def job_extraction(ws, wb):
    driver = webdriver.Chrome()
    jobs = []

    for page in range(0, 50, 10):
        url = f"https://www.indeed.com/jobs?q=python+developer&l=India&start={page}"
        driver.get(url)
        time.sleep(3)

        job_cards = driver.find_elements(By.XPATH, "//div[@class='job_seen_beacon']")

        for card in job_cards:
            try:
                title = card.find_element(By.XPATH, ".//h2//span").text
            except:
                title = ""

            try:
                company = card.find_element(By.XPATH, ".//span[@data-testid='company-name']").text
            except:
                company = ""

            try:
                 loc_main = card.find_element(By.XPATH, ".//div[@data-testid='text-location']").text
  
            except:
                loc_main = ""

            try:
                benefits_elements = card.find_elements(By.XPATH, ".//li[contains(@class, 'css-5ooe72')]")
                benefits = ", ".join([b.text for b in benefits_elements if b.text.strip()])
            except:
                benefits = ""

            ws.append([title, company, loc_main, benefits])
            jobs.append({
                "Title": title,
                "Company": company,
                "Location": loc_main,
                "Benefits": benefits
            })

    driver.quit()
    wb.save("indeed_jobs.xlsx")

    df = pd.DataFrame(jobs)
    df.to_csv("indeed_jobs.csv", index=False)

import psycopg2
import pandas as pd

def database_integration():
    df = pd.read_excel("indeed_jobs.xlsx")

    
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="12345"
    )
    cursor = conn.cursor()

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_listings (
            title TEXT,
            company TEXT,
            location TEXT,
            benefits TEXT
        )
    """)

    # Insert data row by row
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO job_listings (title, company, location, benefits)
            VALUES (%s, %s, %s, %s)
        """, (row['Title'], row['Company'], row['Location'], row['Benefits']))

    conn.commit()
    cursor.close()
    conn.close()
    print("Data inserted into PostgreSQL ")
    


if __name__ == "__main__":
    # wb, ws = making_workbook()
    # job_extraction(ws, wb)
    database_integration()




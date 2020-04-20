import requests
import datetime as dt
import pymongo
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import xlsxwriter
import black

url = "https://austin.craigslist.org/d/software-qa-dba-etc/search/sof"

conn = "mongodb://127.0.0.1:27017/"
client = pymongo.MongoClient(conn)
db = client["jobsDataBase"]
jobscollection = db["jobInformation"]


def make_soup(url):
    r = requests.get(url)
    return bs(r.text, "html.parser")


def main(url):
    while url:
        print("Web Page: ", url)
        soup = soup_process(url, db)
        nextlink = soup.find("a", rel="next")

        url = False
        if nextlink:
            url = nextlink["a"]

    make_excel(db)


def soup_process(url, db):
    global total_added

    soup = make_soup(url)
    results = soup.find_all("a", class_="result-title hdrlnk")
    print(results)
    results = list(results)
    for result in results:
        job = {
            "_id": result["data-id"],
            "Job Title": result.get_text(),
            "Webpage URL": result["href"],
        }

        try:
            jobscollection.insert_one(job)
        except pymongo.errors.DuplicateKeyError:
            continue

    return soup


def make_excel(db):
    Headlines = ["Job Title", "Webpage URL", "Created"]
    row = 0

    workbook = xlsxwriter.Workbook("jobs.xlsx")
    worksheet = workbook.add_worksheet()

    worksheet.set_column(0, 0, 15)  # Job Title
    worksheet.set_column(1, 1, 20)  # URL

    for col, title in enumerate(Headlines):
        worksheet.write(row, col, title)

    for item in jobscollection.find():
        row += 1
        worksheet.write(row, 0, item["Job Title"])
        worksheet.write_url(row, 1, item["Webpage URL"], string="Web Page")
    workbook.close()


main(url)

import csv
import glob
import os
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import pandas as pd
import requests


base_url = "https://www.goodreads.com"

# lists from https://www.goodreads.com/list/tag/most-ratings
# hopefully enough to cover the majority of most people's bookshelves
list_urls = [
    "https://www.goodreads.com/list/show/35857",
    "https://www.goodreads.com/list/show/35776",
    "https://www.goodreads.com/list/show/36384",
    "https://www.goodreads.com/list/show/141019",
    "https://www.goodreads.com/list/show/141016",
    "https://www.goodreads.com/list/show/141024",
    "https://www.goodreads.com/list/show/141025",
    "https://www.goodreads.com/list/show/141027",
    "https://www.goodreads.com/list/show/141032",
    "https://www.goodreads.com/list/show/141033",
    "https://www.goodreads.com/list/show/141034",
    "https://www.goodreads.com/list/show/141035",
    "https://www.goodreads.com/list/show/39332",
    "https://www.goodreads.com/list/show/117368",
    "https://www.goodreads.com/list/show/35708",
    "https://www.goodreads.com/list/show/117146",
    "https://www.goodreads.com/list/show/36647",
    "https://www.goodreads.com/list/show/35177",
    "https://www.goodreads.com/list/show/35080",
]

def scrape_list_pages(list_url):
    print("scraping: ", list_url)
    response = requests.get(list_url)
    html = response.content
    soup = BeautifulSoup(html, "lxml")

    filename = "scrapes/" + list_url.split('/')[-1] + '.html'
    with open(filename, 'wb') as file:
        file.write(soup.prettify('utf-8'))

    next_page_link = soup.find("a", {"class": "next_page"})
    if next_page_link:
        scrape_list_pages(urljoin(base_url, next_page_link["href"]))
    

def scrape_lists():
    for list_url in list_urls:
        scrape_list_pages(list_url)


def write_html_data_to_csv():
    for filename in glob.glob('scrapes/*.html'):
        with open(os.path.join(os.getcwd(), filename)) as file:
            content = file.read()
            soup = BeautifulSoup(content, "lxml")
            links = soup.find_all("a", {"class": "authorName"})
            hrefs = [link["href"] for link in links]

            def get_id_and_name(href):
                return href.split("/show/")[1].split(".")
            
            rows = [get_id_and_name(href) for href in hrefs]

            with open('output.csv', 'a') as csvfile:
                csvwriter = csv.writer(csvfile) 
                csvwriter.writerows(rows)


def remove_duplicate_entries_in_csv():
    df = pd.read_csv("output.csv")
    df.drop_duplicates(subset=None, inplace=True)
    df.to_csv( "output_duplicates_removed.csv", index=False)


def tidy_csv_data():
    df = pd.read_csv("output_duplicates_removed.csv")
    first_name_initialized = df[df["name"].str.contains("^\w_")]
    first_name_initialized.to_csv( "first_name_initialized.csv", index=False)
    
def merge_manually_cleaned_data():
    output_duplicates_removed = pd.read_csv("output_duplicates_removed.csv")
    first_name_initialized_replaced = pd.read_csv("first_name_initialized_replaced.csv")
    merged = pd.merge(output_duplicates_removed, first_name_initialized_replaced, on="id", how="left")
    merged.to_csv( "merged.csv", index=False)

def fetch_gender_prediction_for_names():
    # conditionally create output file to allow for batching
    if not os.path.isfile('predictions.csv'):
        print("predictions.csv doesn't exist. cloning merged.csv")
        df = pd.read_csv("merged.csv")
        predictions = df.assign(
            gender=None,
            probability=None,
            count=None,
            api_name=None
        )
        predictions.to_csv("predictions.csv", sep=",", index=False)

    predictions = pd.read_csv("predictions.csv")
    predictions.fillna("", inplace=True)


    def get_first_name(full_name):
        if pd.isna(full_name):
            return False
        return full_name.split("_")[0]
    
    # for x in range(len(predictions)):
    for x in range(0, 230):

        endpoint = "https://api.genderize.io?"

        # in batches of 10
        for i in range(10):
            row_index = i + x * 10
            row = predictions.iloc[row_index]
            name_x = row["name_x"]
            name_y = row["name_y"]
            first_name =  get_first_name(name_y) or get_first_name(name_x)

            endpoint += f"name[]={first_name}&"

        print(f"requesting :: {endpoint}")

        response = requests.get(endpoint)
        json = response.json()

        for index, prediction in enumerate(json):
            row_index = index + x * 10
            predictions.at[row_index, "gender"] = prediction["gender"]
            predictions.at[row_index, "api_name"] = prediction["name"]
            predictions.at[row_index, "probability"] = prediction["probability"]
            predictions.at[row_index, "count"] = prediction["count"]

        predictions.to_csv("predictions.csv", sep=",", index=False)


def clean_predictions():
    predictions = pd.read_csv("predictions.csv")
    predictions = predictions.drop(axis="columns", labels=["name_y", "api_name"])
    predictions = predictions.rename(columns={"name_x": "name"})
    predictions.to_csv("predictions_clean.csv", index=False)



def match_goodreads_export_with_clean_predictions():
    export = pd.read_csv("my_goodreads_library_export.csv")
    predictions = pd.read_csv("predictions_clean.csv")
    predictions["Author"] = predictions["name"]
    read = export.loc[export["Exclusive Shelf"] == "read", ["Book Id", "Author", "Title"]]
    read["Author"] = read["Author"].str.replace(".", "_")
    read["Author"] = read["Author"].str.replace(" ", "_")
    read["Author"] = read["Author"].str.replace("__", "_")
    join = pd.merge(read, predictions, how="left", on="Author")
    join = join[join["count"] > 0]


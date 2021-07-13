import requests
import csv
from urllib.parse import urljoin

from bs4 import BeautifulSoup

base_url = "https://www.goodreads.com"

# lists from https://www.goodreads.com/list/tag/most-ratings
# hopefully enough to cover the majority of most people's bookshelves
list_urls = [
    # "https://www.goodreads.com/list/show/35857.The_Most_Popular_Fantasy_on_Goodreads",
    "https://www.goodreads.com/list/show/35776.Most_Popular_Science_Fiction_on_goodreads",
    "https://www.goodreads.com/list/show/36384.The_Most_Popular_Non_Fiction_on_Goodreads",
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
    

for list_url in list_urls:
    scrape_list_pages(list_url)


# with open('test.html') as file:
#     content = file.read()
#     soup = BeautifulSoup(content, "lxml")
#     links = soup.find_all("a", {"class": "authorName"})
#     hrefs = [link["href"] for link in links]

#     def get_id_and_name(href):
#         return href.split("/show/")[1].split(".")
    
#     rows = [get_id_and_name(href) for href in hrefs]

#     with open('output.csv', 'a') as csvfile:
#         csvwriter = csv.writer(csvfile) 
#         csvwriter.writerows(rows)
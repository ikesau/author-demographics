import requests
import csv

from bs4 import BeautifulSoup

# # Specifying website url
# base_site = "https://www.goodreads.com/list/show/35857.The_Most_Popular_Fantasy_on_Goodreads" 

# # Make http request
# response = requests.get(base_site)

# # Get the html from webpage
# html = response.content

# # Creating a BeautifulSoup object with the use of a parser
# soup = BeautifulSoup(html, "lxml")

# # Exporting html file
# with open('The_Most_Popular_Fantasy_on_Goodreads.html', 'wb') as file:
#     file.write(soup.prettify('utf-8'))

# scraping ^^^

with open('test.html') as file:
    content = file.read()
    soup = BeautifulSoup(content, "lxml")
    links = soup.find_all("a", {"class": "authorName"})
    hrefs = [link["href"] for link in links]

    def get_id_and_name(href):
        return href.split("/show/")[1].split(".")
    
    authors = {}

    for href in hrefs:
        id, name = get_id_and_name(href)
        authors[id] = {"id": id, "name": name}


    fields = ["id", "name"]
    rows = [author.values() for author in authors.values()]

    with open('output.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)
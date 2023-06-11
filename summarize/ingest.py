# Given an ArXiv HTML page such as https://ar5iv.labs.arxiv.org/html/2302.13971, download the HTML and strip out the raw text content.

import json
import requests
from bs4 import BeautifulSoup
import summarize.summarize as summarize

# URL of the ArXiv HTML page to download
url = "https://ar5iv.labs.arxiv.org/html/2302.04761"

# Send a GET request to the URL and store the response
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Get the title of the page which has class ltx_title
page_title = soup.find("h1", class_="ltx_title").get_text()
# Strip out newlintes and extra spaces
page_title = page_title.replace("\n", "").strip()

# Split the page into sections based on top-level `section` tags, using the
# raw text in first header of the section as the title.
sections = []
for article in soup.find_all("article"):
    for section in article.find_all("section", recursive=False):
        # Title of the section, which could be any header from h1 to h6
        section_title = section.find(["h1", "h2", "h3", "h4", "h5", "h6"]).get_text()
        # Strip out newlintes and extra spaces
        section_title = section_title.replace("\n", "").strip()
        # Raw text content of the section
        text = section.get_text()
        # Add the section title and text to the list of sections
        sections.append((section_title, text))


# Strip out sections such as acknowledgments, references and appendices
words = ["acknowledgment", "acknowledgement", "references", "appendix", "appendice"]
# Lambda to check if the title contains any of the following words
contains = lambda words, title: any(word in title.lower() for word in words)
# Use filter to filter out sections that contain any of the words
sections = list(filter(lambda section: not contains(words, section[0]), sections))

section_summaries = []
for title, text in sections:
    print("Title:", title, "\nText:", len(text), "\n\n")
    summary = summarize.get_summary_recursive(page_title, title, text)
    section_summaries.append((title, summary))

# Generate a file name based on the page title
file_name = page_title.replace(" ", "_").replace(":", "").replace("?", "").replace("/", "_")
# Convert file name to lowercase
file_name = file_name.lower()
# Write section summaries to file in JSON format
with open(f"{file_name}.json", "w", encoding='utf8') as f:
    json.dump(section_summaries, f)

# Genererate a final summary for the entire paper
all_summaries = "\n".join(f"{title}\n{text}" for title, text in section_summaries)
print(all_summaries)
final_summary = summarize.get_summary_recursive(page_title, "", all_summaries)
section_summaries.append(("Summary", final_summary))

# Generate markdown page based on the title and section summaries
# strip away any non-file-system friendly characters
with open(f"{file_name}.md", "w", encoding='utf8') as f:
    f.write(f"# {page_title}\n")
    for title, summary in section_summaries:
        f.write(f"## {title}\n")
        f.write(summary)
        f.write("\n\n")

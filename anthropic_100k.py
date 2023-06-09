import anthropic
from bs4 import BeautifulSoup
import os
import requests
import sys
from termcolor import colored
import tiktoken
import time

USE_STREAMING = True
SAMPLE_URL = "https://ar5iv.labs.arxiv.org/html/2305.10403"
claude = anthropic.Client(os.environ["ANTHROPIC_API_KEY"])

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_completion(text: str, prompt: str, max_tokens_to_sample: int = 1000) -> str:
    """Calls Anthropic for completion.""" 
    response = claude.completion(
        prompt=f"""{anthropic.HUMAN_PROMPT} You are an expert summarizer and ML researcher.
You are provided a full paper below:
```
{text}
```
Given the paper contents, answer the following prompt or question:
{prompt}

{anthropic.AI_PROMPT}
""",
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-instant-v1-100k",
        max_tokens_to_sample=max_tokens_to_sample,
        temperature=0.0,
    )
    completion = response["completion"]
    return completion

def get_completion_streaming(text: str, prompt: str, max_tokens_to_sample: int = 1000) -> str:
    response = claude.completion_stream(
        prompt=f"""{anthropic.HUMAN_PROMPT} You are an expert summarizer and ML researcher.
You are provided a full paper below:
```
{text}
```
Given the paper contents, answer the following prompt or question:
{prompt}

{anthropic.AI_PROMPT}
""",
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-instant-v1-100k",
        max_tokens_to_sample=max_tokens_to_sample,
        temperature=0.0,
        stream=True,
    )
    prev_string = ""
    for data in response:
        # Take only the diff from the prev_string
        diff = data["completion"][len(prev_string):]
        prev_string = data["completion"]
        print(diff, end="", flush=True)
    print()
    return prev_string

def main():
    # Ask user for URL, or use default. Use bold text.
    paper_url = input(colored("arxiv or ar5iv URL: ", attrs=["bold"]))

    if paper_url == "":
        paper_url = SAMPLE_URL

    # Validate that it is a ar5iv URL
    while not paper_url.startswith("https://ar5iv.labs.arxiv.org/html/"):
        # See if it is an arxiv URL or document ID
        if paper_url.startswith("https://arxiv.org/abs/"):
            # Convert to ar5iv URL
            paper_url = paper_url.replace("https://arxiv.org/abs/", "https://ar5iv.labs.arxiv.org/html/")
            break
        elif paper_url.startswith("https://arxiv.org/pdf/"):
            # Convert to ar5iv URL
            paper_url = paper_url.replace("https://arxiv.org/pdf/", "https://ar5iv.labs.arxiv.org/html/")
            # Remove .pdf extension
            paper_url = paper_url[:-4]
            break

        print(colored("Please enter a valid arxiv or ar5iv URL.", "red"))
        paper_url = input(colored("arxiv or ar5iv URL: ", attrs=["bold"]))

    print(colored(f"ar5iv URL: {paper_url}", "green"))

    # Send a GET request to the URL and store the response
    response = requests.get(paper_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Print out the title of the paper
    print(colored(f"Title: {soup.title.string}", "green"))

    # Get string from HTML
    text = soup.get_text()

    print(colored(f"Number of tokens: {num_tokens_from_string(text)}", "green"))

    # Loop until the user quits. Ask for question and print completion
    while(True):
        prompt = input(colored("Question: ", attrs=["bold"]))
        if prompt == "":
            print(colored("Please enter a valid question or 'quit' to exit.", "red"))
        elif prompt == "quit":
            break

        # Time the completion
        start = time.time()
        
        print(colored("Generating completion...", "yellow"))
        if USE_STREAMING:
            print(colored("Completion:", attrs=["bold"]))
            completion = get_completion_streaming(text, prompt)
        else:
            completion = get_completion(text, prompt)
            print(colored("Completion:\n", attrs=["bold"]), completion.strip())

        end = time.time()
        print(colored(f"Completion time: {end - start}", "green"))
        # Print token count
        num_completion_tokens = num_tokens_from_string(completion)
        print(colored(f"Number of completion tokens: {num_completion_tokens}", "green"))

        # Given the following info, price the completion
        # Prompt: $1.63/million tokens Completion: $5.51/million tokens
        prompt_cost = 1.63 * num_tokens_from_string(prompt) / 1000000
        completion_cost = 5.51 * num_tokens_from_string(completion) / 1000000
        total_cost = prompt_cost + completion_cost
        print(colored(f"Approximate Cost: ${round(prompt_cost, 5)} + ${round(completion_cost, 5)} = ${round(total_cost, 5)}", "green"))


if __name__ == "__main__":
    main()
import anthropic
from bs4 import BeautifulSoup
import ingest
import os
import requests
from termcolor import colored
import tiktoken
import time

USE_STREAMING = True
SAMPLE_URL = "https://ar5iv.labs.arxiv.org/html/2305.10403"
# Max number of individual messages to keep
MAX_MESSAGE_HISTORY_LENGTH = 10


class Role:
    """Enum for role, either human or assistant."""
    HUMAN = "human"
    ASSISTANT = "assistant"

class Message:
    """Holds previous chat messages to Claude."""
    def __init__(self, role: Role, content: str):
        self.role = role
        self.content = content

    def _prompt(self) -> str:
        """Returns the prompt for the message."""
        if self.role == Role.HUMAN:
            return anthropic.HUMAN_PROMPT
        elif self.role == Role.ASSISTANT:
            return anthropic.AI_PROMPT
        else:
            raise ValueError("Invalid role")
    
    def __str__(self) -> str:
        """Returns the message as a string."""
        return f"{self._prompt()} {self.content}"

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def messages_to_string(messages: list[Message]) -> str:
    """Converts a list of messages to a string."""
    result = ""
    for message in messages:
        result += str(message)
    return result

def get_completion(
        text: str,
        prompt: str,
        messages: list[Message] = None,
        max_tokens_to_sample: int = 2000
    ) -> str:
    """Calls Anthropic for completion.""" 
    claude = anthropic.Client(os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""{anthropic.HUMAN_PROMPT}
System: You are an expert researcher and summarizer.
You are provided a full paper below scraped from HTML format:
```
{text}
```

If provided, the most recent messages are provided below:
```{messages_to_string(messages)}
```

Given the paper contents, answer the user's prompt or question.
Use a format suitable for a terminal or command line interface.
If you quote the paper directly, remove any HTML artifacts.
{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}"""
    response = claude.completion(
        prompt=prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-instant-v1-100k",
        max_tokens_to_sample=max_tokens_to_sample,
        temperature=0.0,
    )
    completion = response["completion"]
    return completion

def get_completion_streaming(
    text: str,
    prompt: str,
    messages: list[Message] = None,
    max_tokens_to_sample: int = 2000
) -> str:
    """Calls Anthropic for completion using streaming."""
    claude = anthropic.Client(os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""{anthropic.HUMAN_PROMPT}
System: You are an expert researcher and summarizer.
You are provided a full paper below scraped from HTML format:
```
{text}
```

If provided, the most recent messages are provided below:
```{messages_to_string(messages)}
```

Given the paper contents, answer the user's prompt or question.
Use a format suitable for a terminal or command line interface.
If you quote the paper directly, remove any HTML artifacts.
{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}"""
    print(colored(f"Prompt:\n{prompt}", attrs=["bold"]))
    response = claude.completion_stream(
        prompt=prompt,
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
    return prev_string, prompt

def main():
    # Ask user for URL, or use default. Use bold text.
    paper_url = input(colored("arxiv or ar5iv URL: ", attrs=["bold"])).strip()

    if paper_url == "":
        paper_url = SAMPLE_URL

    # Validate that it is a ar5iv URL
    while not paper_url.startswith("https://ar5iv.labs.arxiv.org/html/"):
        if paper_url.startswith("https://arxiv.org/abs/"):
            # Convert to ar5iv URL
            paper_url = paper_url.replace("https://arxiv.org/abs/", "https://ar5iv.labs.arxiv.org/html/")
            break
        elif paper_url.startswith("https://arxiv.org/pdf/"):
            # Convert to ar5iv URL
            paper_url = paper_url.replace("https://arxiv.org/pdf/", "https://ar5iv.labs.arxiv.org/html/")
            paper_url = paper_url[:-4]
            break

        print(colored("Please enter a valid arxiv or ar5iv URL.", "red"))
        paper_url = input(colored("arxiv or ar5iv URL: ", attrs=["bold"])).strip()

    print(colored(f"ar5iv URL: {paper_url}", "green"))

    # Send a GET request to the URL and store the response
    response = requests.get(paper_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

    # Check for redirect to arxiv
    if response.url.startswith("https://arxiv.org/abs/"):
        print(colored("Redirected to arxiv.org. Falling back to PDF import.", "red"))
        # Convert to arxiv PDF URL
        paper_url = paper_url.replace("https://ar5iv.labs.arxiv.org/html/", "https://arxiv.org/pdf/")
        paper_url += ".pdf"
        text = ingest.download_pdf(paper_url)
    else:
        print(colored("HTML content retrieved.", "green"))
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Print out the title of the paper
        print(colored(f"Title: {soup.title.string}", "green"))

        # Get string from HTML
        text = soup.get_text()

    total_num_tokens = num_tokens_from_string(text)
    print(colored(f"Number of tokens: {total_num_tokens}", "green"))

    messages: list[Message] = []

    # Loop until the user quits.
    while(True):
        user_prompt = input(colored("Question: ", attrs=["bold"]))
        if user_prompt == "":
            print(colored("Please enter a valid question or 'quit' to exit.", "red"))
            continue
        elif user_prompt == "quit":
            break

        # Time the completion
        start = time.time()
        
        print(colored("Generating completion...", "yellow"))
        if USE_STREAMING:
            print(colored("Completion:", attrs=["bold"]))
            completion, full_prompt = get_completion_streaming(
                text, user_prompt, messages=messages)
        else:
            completion = get_completion(text, user_prompt)
            print(colored("Completion:\n", attrs=["bold"]), completion.strip())

        # Add the user_prompt and completion to messages
        messages.append(Message(role=Role.HUMAN, content=user_prompt))
        messages.append(Message(role=Role.ASSISTANT, content=completion))

        # Pop from front until less than N messages
        while len(messages) > MAX_MESSAGE_HISTORY_LENGTH:
            messages.pop(0)

        ## Generate time and cost metadata
        end = time.time()
        print(colored(f"Completion time: {end - start:.2f} seconds", "green"))
        # Print token count
        num_prompt_tokens = num_tokens_from_string(full_prompt)
        num_completion_tokens = num_tokens_from_string(completion)
        print(colored(f"Number of prompt tokens: {num_prompt_tokens}", "green"))
        print(colored(f"Number of completion tokens: {num_completion_tokens}", "green"))

        # Given the following info, price the completion
        # Prompt: $1.63/million tokens Completion: $5.51/million tokens
        prompt_cost = 1.63 * num_prompt_tokens / 1000000
        completion_cost = 5.51 * num_tokens_from_string(completion) / 1000000
        total_cost = prompt_cost + completion_cost
        print(colored(
            f"Approximate Cost: ${prompt_cost:.6f} + ${completion_cost:.6f} = ${total_cost:.6f}",
            "green"
        ))


if __name__ == "__main__":
    main()

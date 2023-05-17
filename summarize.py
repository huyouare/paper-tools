from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import openai

summarize_prompt = """
You are an expert summarizer. Your goal is to summarize the provided text as truthfully and concisely as possible.
DO NOT HALLUCINATE ANY FACTS.

You will provide a 1-paragraph summary up to 100 words, followed by a list 3-5 bullet points for the most important facts and takeaways of the article.

The user will provide a title for the paper and a title of the section, followed by the raw text of the entire webpage.
The main article will be an academic paper.

Within your summary and takeways, emphasize or bold key words and phrases using markdown format.
Bold text is formatted as follows: `I just love **bold text**.`
Italic text is formatted as follows: `Italicized text is the *cat's meow*.`

Output format (unless empty):
```
<1-paragraph summary>

Key takeaways:
* <bullet point 1>
* <bullet point 2>
* <bullet point 3>
```
"""

reduce_prompt = """
You are an expert summarizer. Your goal is to summarize existing summaries as truthfully and concisely as possible.
DO NOT HALLUCINATE ANY FACTS. Add context as needed, but do not make up any facts.

Within your summary and takeways, emphasize or bold key words and phrases using markdown format.
Bold text is formatted as follows: `I just love **bold text**.`
Italic text is formatted as follows: `Italicized text is the *cat's meow*.`

The user will provide the paper title and section title, followed by generated summaries of successive chunks of the section.
If there is no section title provided, then the summaries are from the entire paper.
Given multiple summaries and key takeaways, merge these into a 1-paragraph summary up to 100 words, followed by a list of up to 3-5 bullet points for the most important facts and takeaways of the article.

Output format (if summary available):
```
<1-paragraph summary>

Key takeaways:
* <bullet point 1>
* <bullet point 2>
* <bullet point 3>
```
"""


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_summary(article_title, section_title, text, prompt=summarize_prompt):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": f"Paper title: {article_title}"},
                  {"role": "user", "content": f"Section title: {section_title}"},
                  {"role": "user", "content": f"Raw Text: ```{text}```"},
                  ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def reduce_summary(article_title, section_title, text):
    return get_summary(article_title, section_title, text, prompt=reduce_prompt)


def get_summary_recursive(article_title, section_title, text):
    print("Calling get_summary_recursive")

    # Define the chunk size and the overlap size
    # Assuming 4 chars per token, we aim for 2500 tokens.
    chunk_size = 10000
    overlap_size = 100

    # Split the text content into chunks at the end of a sentence or line with a window overlap
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            end = len(text)
            chunks.append(text[start:end])
            break
        else:
            # Search for the last period, exclamation point, or question mark character before the end position,
            # or for the last newline character
            end = max(text.rfind(".", start, end), text.rfind("!", start, end), text.rfind(
                "?", start, end), text.rfind("\n", start, end))
            if end < start + overlap_size:
                # If the last sentence or line is within the overlap size of the start position,
                # set the end position to the chunk size to avoid overlapping with the previous chunk
                end = start + chunk_size
            else:
                # Include the period, exclamation point, question mark, or newline character in the chunk
                end += 1
        chunks.append(text[start:end])
        start = end - overlap_size

    # Use GPT-3 to summarize each chunk of text
    summaries = []
    # Only summarize the first 5 chunks
    for index, chunk in enumerate(chunks[:5]):
        print(f"\nSummarizing chunk #{index}")
        summaries.append(get_summary(article_title, section_title, chunk))

    print("\nSUMMARIES:", summaries)
    all_summaries = '\n'.join(summaries)
    if len(all_summaries) < chunk_size:
        return reduce_summary(article_title, section_title, all_summaries)
    else:
        return get_summary_recursive(article_title, section_title, all_summaries)

from groq import Groq
from coursesScraping import fetch_trusted_search_links
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

client = Groq(api_key="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")

TRUSTED_SITES = [
    "coursera.org",
    "edx.org",
    "udemy.com",
    "khanacademy.org",
    "codecademy.com",
    "udacity.com",
    "futurelearn.com",
    "skillshare.com",
    "pluralsight.com",
    "lynda.com",
    "datacamp.com",
    "alison.com",
    "linkedin.com/learning",
    "open.edu",
    "w3schools.com",
    "sololearn.com",
    "freecodecamp.org",
    "mit.edu",
    "harvard.edu",
    "stanford.edu",
    "nptel.ac.in",
    "swayam.gov.in",
]


def fetch_trusted_search_links(query, num_results=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={num_results}"

    try:
        html = requests.get(url, headers=headers, timeout=10)
        html.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search results: {e}")
        return [], []

    soup = BeautifulSoup(html.text, "html.parser")
    allData = soup.find_all("div", {"class": "g"})
    trusted_links = []
    untrusted_links = []

    for i in range(len(allData)):
        link = allData[i].find("a").get("href")
        if link is not None:
            parsed_domain = urlparse(link).netloc.lower()
            if any(trusted_site in parsed_domain for trusted_site in TRUSTED_SITES):
                trusted_links.append(link)
            else:
                untrusted_links.append(link)

    return trusted_links, untrusted_links


def get_bot_response(current, end_goal):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You Are A Roadmap Generator"},
            {
                "role": "user",
                "content": f"{current} - this is the current status of the user, {end_goal} - this is what the user wants to achieve. Now find the user's weakness and create a roadmap for the user to reach their goal. To deal with each weakness, create a checkpoint.",
            },
        ],
        model="llama3-8b-8192",
        max_tokens=1000,
    )
    return chat_completion.choices[0].message.content


def find_courses(response):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a course name generator. You only generate course names and nothing else.",
            },
            {
                "role": "user",
                "content": f"{response} - For each checkpoint, suggest a course. In the output, only mention course names separated by commas do not write anything other than that write them in correct order in order of easy to advanced strictly follow the output format",
            },
        ],
        model="llama3-8b-8192",
        max_tokens=1000,
    )
    return chat_completion.choices[0].message.content


response = get_bot_response(
    current="i am currently persuing a computer science degree",
    end_goal="I want to master machine learning",
)


course_names_response = find_courses(response=response)


course_names = [course.strip() for course in course_names_response.split(",")]
for i in course_names:
    if len(i) < 5:
        course_names.remove(i)

course = {}
for i in course_names:
    trusted, untrusted = fetch_trusted_search_links(
        f"{i} coursera course or edx course or stanford course", num_results=1
    )
    if len(trusted) == 1:
        course[i] = trusted

print(course)

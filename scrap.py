import os
import requests
from bs4 import BeautifulSoup
import cohere

import streamlit as st
import streamlit.components.v1 as coms

from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("API_KEY_COHERE")

co = cohere.Client(API_KEY)


def generate(prompt, max_tokens):
    response = co.generate(
        model='xlarge',
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.5,
        k=0,
        p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop_sequences=["--"],
        return_likelihoods='NONE')
    return response.generations[0].text.replace("--", "")


def read_online(filename):
    with open(filename, "r") as file:
        data = file.read()
    return data


input = st.text_area(
    label="Enter text",
    placeholder="Enter something"
).strip()
btn = st.button("Submit")
if btn:
    max_tokens = len(input.split(" "))
    file = read_online("./data.txt").replace("<<USER_INPUT>>", input)
    text_output = generate(file, max_tokens)
    st.text_area(label="Summarization",
                 value=text_output,
                 height=200)
    text_output = '+'.join(text_output.split(" "))
    url = f"https://google.com/search?q={text_output}&tbm=nws"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # get top 5 title and date

    title = soup.findAll("h3")[:5]
    time = soup.findAll("span", class_="r0bn4c rQMQod")[:5]
    links = [div.a['href'].replace(
        "/url?q=", "") for div in soup.findAll("div")[27:60] if div.a is not None][:5]

    for title, time, link in zip(title, time, links):
        st.write(f"Title: {title.text.strip()}, {time.text}")
        st.write(f"{link.strip()}")

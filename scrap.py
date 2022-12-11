import os

import requests
import re
from bs4 import BeautifulSoup
import cohere
import time
import streamlit as st

from dotenv import load_dotenv

load_dotenv()


API_KEY_COHERE = os.getenv("API_KEY_COHERE")

co = cohere.Client(API_KEY_COHERE)

API_KEY_ASSEMBLY = os.getenv("API_KEY_ASSEMBLY")


# def download_youtube(youtube_url):
#     yt = YouTube(str(youtube_url))
#     video = yt.streams.filter(only_audio=True).first()
#     out_file = video.download(output_path=".")
#     base, _ = os.path.splitext(out_file)
#     new_file = base + ".mp3"
#     os.rename(out_file, new_file)
#     return new_file


def upload(filename: str):
    endpoint = "https://api.assemblyai.com/v2/upload"
    json = {
        "language_code": "en",
    }
    headers = {"authorization": API_KEY_ASSEMBLY}
    response = requests.post(
        endpoint, json=json, headers=headers, data=filename)
    return response.json()["upload_url"]


def transcript(url: str):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {
        "audio_url": url,
        "language_code": "en",
    }
    headers = {"authorization": API_KEY_ASSEMBLY,
               "content-type": "application/json"}
    response = requests.post(endpoint, json=json, headers=headers)
    return response.json()["id"]


def get_transcript(id: str):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{id}"
    headers = {"authorization": API_KEY_ASSEMBLY}
    response = requests.get(endpoint, headers=headers)
    return response.json()


# url_link = "https://www.youtube.com/watch?v=pJo-qmgEv7U"
# filename = "id.txt"


# def check_if(filename):
#     if os.path.exists(filename):
#         with open(filename, "r") as file:
#             id = file.read()
#             return id
#     return "False"


# if check_if(filename) != "False":
#     id = check_if(filename)
#     print(transcribe(id))
# else:
#     with open(filename, "w") as file:
#         id = process(url_link)
#         file.write(id)

# filename = st.file_uploader("Choose a file: ")
# print(filename)
# btn = st.button("Submit")
# if btn:
#     with st.spinner("Wait for it...."):
#         url = upload(filename)
#         id = transcript(url)
#         text = get_transcript(id)
#         while text["status"] != "completed":
#             time.sleep(2)
#             text = get_transcript(id)

#     get_output(text)


def generate(prompt, max_tokens):
    response = co.generate(
        model="xlarge",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.5,
        k=0,
        p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop_sequences=["--"],
        return_likelihoods="NONE",
    )
    return response.generations[0].text.replace("--", "")


def read_online(filename):
    with open(filename, "r") as file:
        data = file.read()
    return data


def get_output(text_output):
    text_output = "+".join(text_output.split(" "))
    url = f"https://google.com/search?q={text_output}&tbm=nws"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # get top 5 title and date

    title = soup.findAll("h3")[:10]
    time = soup.findAll("span", class_="r0bn4c rQMQod")[:10]
    links = [
        div.a["href"].replace("/url?q=", "")
        for div in soup.findAll("div")[27:60]
        if div.a is not None
    ][:10]

    pattern = r"&.*$"
    for title, time, link in zip(title, time, links):
        st.write(f"Title: {title.text.strip()}, {time.text.strip()}")
        link = re.sub(pattern, "", link)
        st.write(f"{link}")


st.title("AssemblyAIHackathon")
st.write(
    "A simple web app that tests whether the information is publicly available or made up."
)

tab1, tab2 = st.tabs(["TextInput", "AudioInput"])

with tab1:
    input = st.text_area(
        label="Enter text", placeholder="Enter something", height=500
    ).strip()
    btn = st.button("Submit")
    if btn:
        max_tokens = len(input.split(" "))
        file = read_online("./data.txt").replace("<<USER_INPUT>>", input)
        text_output = generate(file, max_tokens)
        st.text_area(label="Summarization", value=text_output, height=200)
        get_output(text_output)

with tab2:
    filename = st.file_uploader("Choose a file: ")
    btn = st.button("Submit", key="1")
    if btn:
        with st.spinner("Wait for it...."):
            url = upload(filename)
            id = transcript(url)
            text = get_transcript(id)
            while text["status"] != "completed":
                time.sleep(2)
                text = get_transcript(id)
        print(text["text"])
        max_tokens = len(text["text"].split(" "))
        file = read_online("./data.txt").replace("<<USER_INPUT>>", input)
        text_output = generate(file, max_tokens)
        if text_output.strip() == "":
            print("Nothing")
            st.text_area(label="Audio Output", value=text["text"], height=200)
            get_output(text["text"])
        else:
            st.text_area(label="Summarization", value=text_output, height=200)
            get_output(text["text"])

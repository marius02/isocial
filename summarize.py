import openai
import requests
import json
from bs4 import BeautifulSoup


openai.api_key = "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"


def summarize(video_id: str) -> str:
    comments = getComments(video_id)

    prompt = assemblePrompt(comments)

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt[:12000]}],
                                            max_tokens=800,
                                            temperature=0)

    return response


def getComments(video_id: str) -> list:
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key=AIzaSyBdvZRjQd6VEAM32nnQLThmx7ARvcvTKrY&maxResults=500&textFormat=plainText"
    response = requests.get(url)

    comments = response.json()["items"]

    commentTexts = [comments[i]['snippet']['topLevelComment']
                    ['snippet']['textDisplay'] for i in range(len(comments))]

    commentTexts = [BeautifulSoup(c, "html.parser") for c in commentTexts]

    commentTexts = [c.text for c in commentTexts]

    return commentTexts


def assemblePrompt(comments: str) -> str:
    prompt = "The following are user comments of a YouTube video, with each commeent separated by a ;. Please provide a summary of what users thought about the video."

    comment_prompt = ';'.join(comments)
    return prompt+" " + "\n"+comment_prompt

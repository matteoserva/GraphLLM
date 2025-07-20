#!/usr/bin/python3

import requests
import xml.etree.ElementTree as ET
import sys
import tempfile
from youtube_transcript_api import YouTubeTranscriptApi
import re


videoUrl="https://www.youtube.com/watch?v=Ic-7n8tIpPw"
if len(sys.argv) > 1:
  videoUrl = sys.argv[1]
print("opening video " + videoUrl, file=sys.stderr)
r = requests.get(videoUrl)
with open(tempfile.gettempdir() + "/w2.txt","w") as f:
    f.write(r.text)

import json
with open(tempfile.gettempdir() + "/w2.txt") as f:
    data = f.read()

val = ""

print("extracting title and author", file=sys.stderr)

# add title and author to transcript
cdata = data[data.find('"videoDetails"')+15:]
decoder = json.JSONDecoder()
obj,idx = decoder.raw_decode(cdata)
#print (obj)
val = "Title: " + obj["title"] + "\nAuthor: " + obj["author"] + "\n\nTranscription:\n" + val

print("fetching trascripts", file=sys.stderr)
video_id = obj['videoId']
ytt_api = YouTubeTranscriptApi()
transcript_list = ytt_api.list(video_id)
try:
    transcript_info = transcript_list.find_manually_created_transcript(['it', 'en'])
except:
    transcript_info = [el for el in transcript_list][0]
    
transcript = transcript_info.fetch().to_raw_data()

for el in transcript:
    start_s = int(el["start"])
    seconds = start_s % 60
    minutes = start_s // 60
    res = "[{:02d}:{:02d}]".format(minutes,seconds)
    val += res + "\n" + el["text"] + "\n"

# save

with open(tempfile.gettempdir() + "/yt_transcript.txt","w") as f:
    _ = f.write(val)
print(val)

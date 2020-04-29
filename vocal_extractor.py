#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pytube import YouTube
import subprocess
import pandas as pd
import numpy as np
from datetime import timedelta

def download_video(source):
    video = YouTube(source)
    video.streams.first().download(filename='video')


def video_attrs():
    seconds = get_ipython().getoutput('ffprobe -v error -select_streams v:0 -show_entries stream=duration     -of default=noprint_wrappers=1:nokey=1 video.mp4')
    seconds = int(float(seconds[0]))
    duration_of_video = timedelta(seconds=seconds)
    if seconds>=3600 and seconds<36000:
        duration_of_video = '0' + str(duration_of_video)
    elif seconds>=36000:
        duration_of_video = str(duration_of_video)[-8:]
    else:
        duration_of_video = str(duration_of_video)[-5:]
    nr_of_parts = int(seconds/600) + 1
    return nr_of_parts, duration_of_video


def cutting_points(nr_of_parts,duration_of_video):
    beginning = []
    end = []
    if nr_of_parts< 6:
        parts = [str('part_')+str(i+1)+str('.mp4') for i in range(nr_of_parts)]
        beginning = [str(i)+'0:00' for i in range(nr_of_parts)]
        end = [str(i+1)+'0:00' for i in range(nr_of_parts-1)]
        end.append(duration_of_video)
    else:
        for i in range(int(nr_of_parts/6)):
            beginning = beginning + ['0' + str(i) + ':' + str(j)+'0:00' for j in range(6)]
            end = end +['0' + str(i) + ':' + str(j)+'0:00' for j in range(6)]
        end = end[1:]
        beginning = beginning + ['0' + str(int(nr_of_parts/6)) + ':' + str(j)+'0:00' for j in range(nr_of_parts%6)]
        end = end + ['0' + str(int(nr_of_parts/6)) + ':' + str(j)+'0:00' for j in range(nr_of_parts%6)]
        end.append(duration_of_video)
        parts = [str('part_')+str(i+1)+str('.mp4') for i in range(nr_of_parts+1)]
    return beginning, end, parts

def extract_vocals(link, filename='merged_video'):
    download_video(link)
    nr_of_parts , duration_of_video = video_attrs()
    beginning, end, parts = cutting_points(nr_of_parts,duration_of_video)

    for i in range(len(parts)):
        parts_ = parts[i]
        beginning_ = beginning[i]
        end_ = end[i]
        cmds = [["ffmpeg", "-i", "video.mp4", "-ss", beginning_, "-to", end_, "-c", "copy", parts_],
       ["ffmpeg", "-i", parts_, "-codec", "copy", "-an", str("silent_video_" + str(i+1) + ".mp4")],
       ["ffmpeg", "-i", parts_ , "-vn", "-f", "wav", "audio_" + str(i+1) + ".wav"],
       ["spleeter", "separate", "-i", "audio_" + str(i+1) + ".wav", "-p", "spleeter:2stems", "-o", "myoutput"+str(i+1)],
       ["ffmpeg", "-i", "silent_video_" + str(i+1) + ".mp4", "-i", "myoutput"+ str(i+1) +"/audio_"+str(i+1)+"/vocals.wav", "-c:v", "copy", "-c:a", "aac", "vocals_"+str(i+1)+"_video.mp4"]]
        for cmd in cmds:
            subprocess.run(cmd, stderr=subprocess.STDOUT)

    concat = ["file" + " 'vocals_"+str(i+1)+"_video.mp4'" for i in range(len(parts))]

    f=open('files.txt','w')
    s1='\n'.join(concat)
    f.write(s1)
    f.close()
  
    cmd = ["ffmpeg", "-f", "concat" , "-safe", "0", "-i", "files.txt" , "-c", "copy", filename+".mp4"]
    subprocess.run(cmd, stderr=subprocess.STDOUT)
    print('Done!')
  


#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pytube import YouTube
from pytube import YouTube
import subprocess
import pandas as pd
import numpy as np
from datetime import timedelta

def GetTime(seconds):
  sec = timedelta(seconds=int(seconds))
  if int(seconds)>=3600 and int(seconds)<36000:
    return '0' + str(sec)
  elif int(seconds)>=36000:
    return str(sec)[-8:]
  else:
    return str(sec)[-5:]
    
def VoiceVideo(my_link):
  video = YouTube(my_link)
  video.streams.first().download(filename='video')

  duration = get_ipython().getoutput('ffprobe -v error -select_streams v:0 -show_entries stream=duration     -of default=noprint_wrappers=1:nokey=1 video.mp4')
  length = int(float(duration[0])/600)
  time = GetTime(float(duration[0]))

  beginning = []
  end = []
  if int(float(duration[0])/600)< 6:
    filename = [str('part_')+str(i+1)+str('.mp4') for i in range(length+1)]
    beginning = [str(i)+'0:00' for i in range(length+1)]
    end = [str(i+1)+'0:00' for i in range(length)]
    end.append(time)
  else:
    for i in range(int(length/6)):
      beginning = beginning + ['0' + str(i) + ':' + str(j)+'0:00' for j in range(6)]
      end = end +['0' + str(i) + ':' + str(j)+'0:00' for j in range(6)]
    end = end[1:]

    beginning = beginning + ['0' + str(length%6) + ':' + str(j)+'0:00' for j in range(length%6+1)]
    end = end + ['0' + str(length%6) + ':' + str(j)+'0:00' for j in range(length%6+1)]
    end.append(time)
    filename = [str('part_')+str(i+1)+str('.mp4') for i in range(length+1)]
  
  for i in range(len(filename)):
    filename_ = filename[i]
    beginning_ = beginning[i]
    end_ = end[i]
    cmd = ["ffmpeg", "-i", "video.mp4", "-ss", beginning_, "-to", end_, "-c", "copy", filename_]
    subprocess.run(cmd, stderr=subprocess.STDOUT)
    cmd = ["ffmpeg", "-i", filename_, "-codec", "copy", "-an", str("silent_video_" + str(i+1) + ".mp4")]
    subprocess.run(cmd, stderr=subprocess.STDOUT)
    cmd = ["ffmpeg", "-i", filename_ , "-vn", "-f", "wav", "audio_" + str(i+1) + ".wav"]
    subprocess.run(cmd, stderr=subprocess.STDOUT)
    cmd = ["spleeter", "separate", "-i", "audio_" + str(i+1) + ".wav", "-p", "spleeter:2stems", "-o", "myoutput"+str(i+1)]
    subprocess.run(cmd, stderr=subprocess.STDOUT)
    cmd = ["ffmpeg", "-i", "silent_video_" + str(i+1) + ".mp4", "-i", "myoutput"+ str(i+1) +"/audio_"+str(i+1)+"/vocals.wav", "-c:v", "copy", "-c:a", "aac", "vocals_"+str(i+1)+"_video.mp4"]
    subprocess.run(cmd, stderr=subprocess.STDOUT)

  concat = ["file" + " 'vocals_"+str(i+1)+"_video.mp4'" for i in range(len(filename))]
  f=open('files.txt','w')
  s1='\n'.join(concat)
  f.write(s1)
  f.close()
  get_ipython().system('ffmpeg -f concat -safe 0 -i files.txt -c copy mergedfile.mp4')


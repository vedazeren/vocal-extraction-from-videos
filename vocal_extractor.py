# -*- coding: utf-8 -*-
from pytube import YouTube
import subprocess
import pandas as pd
import numpy as np
from datetime import timedelta
import ffmpeg 
import argparse


def download_video(source):
    
    """
    Gets a YouTube link as source and downloads it to the current directory as video.mp4
    """
    
    video = YouTube(source)
    video.streams.first().download(filename='video')


def video_attrs():
    
    """    
    Spleeter library can only process audio up to 10 minutes, the function calculates the duration
    of the video and # of 10 minue parts to be processed seperately later.
    
    Returns:
        nr_of_parts (int): # of 10 minute parts of the video
        duration_of_video (str): The duration of the video in hh:mm:ss format proper for 
        a command line call    
    """
    seconds = int(VideoFileClip("video.mp4").duration)
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
    
    """    
    Function define the cutting points of the video for each 10 minute.    
    
    Args:
        nr_of_parts (int): # of 10 minute parts of the video
        duration_of_video (str): The duration of the video in hh:mm:ss format
        
    Returns:
        beginning(list): Beginning time of each 10 minute part
        end(list): Ending time of each 10 minute part
        parts(list): Filename of each 10 minute part.
        
    Examples:
        >>> nr_of_parts = 4
        >>> duration_of_video = '00:38:26'
        >>> cutting_points(nr_of_parts,duration_of_video))
        (['00:00', '10:00', '20:00', '30:00'],
        ['10:00', '20:00', '30:00', '00:38:26'],
        ['part_1.mp4', 'part_2.mp4', 'part_3.mp4', 'part_4.mp4'])     
        
    """
    
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
    
    """
    After downloading the video and defining the cutting points, function processes each 10 minute
    part of the video in an iterable fashion.
    
    cmds:
        1) Creates a copy of the video by cutting it according to the defined beginning and end points.
        2) Converts the 10 minute parts of the video to silent.
        3) Creates audio files from 10 minute parts.
        4) Splits audio files to 2 parts: vocals.wav and accompaniment.wav. Stores both audio files.
        vocals.wav includes only the human voice while all the other audio is stored in the 
        accompaniment.wav file.
        5) Output is silent video parts with vocals reunited.
        
    Lastly, the function combines the 10 minute parts of vocal-only videos to into one video and saves it 
    with the filename defined as the second argument.
    
    Args:
        link(str): YouTube link of the video to extract the vocals from.
        filename(str): Optional argument for the name of the vocal-only video. 
        Default is merged_video(.mp4)
        
    """
    
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
       ["python","-m","spleeter", "separate", "-i", "audio_" + str(i+1) + ".wav", "-p", "spleeter:2stems", "-o", "myoutput"+str(i+1)],
       ["ffmpeg", "-i", "silent_video_" + str(i+1) + ".mp4", "-i", "myoutput"+ str(i+1) +"/audio_"+str(i+1)+"/vocals.wav",
        "-c:v", "copy", "-c:a", "aac", "vocals_"+str(i+1)+"_video.mp4"]]
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

from pydub import AudioSegment
from pprint import pprint
import youtube_dl
#import eyed3
import sys
import os
import datetime
import time
import re
import argparse

py3k = False
try:
    from urlparse import urlparse, parse_qs
except:
    py3k = True
    from urllib.parse import urlparse, parse_qs


# youtube_dl configuration
class ytdl_logger(object):
    def debug(self, msg):
        sys.stdout.write('\r\033[K')
        sys.stdout.write(msg)
        sys.stdout.flush()

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def ytdl_hook(d):
    if d['status'] == 'downloading':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownloading video | ETA: ' 
                            + str(d["eta"]) + " seconds")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownload complete\n\tConverting video to mp3')
        sys.stdout.flush()

ytdl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '0',
    }],
    #'logger': ytdl_logger(),
    #'progress_hooks': [ytdl_hook],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download a YouTube video and split into mp3 tracks')
    #parser.add_argument()

    in_yt_url = 'XZaU-Oqo-qs'
    in_folder = './tracks_test/'
    in_album_filename = None
    in_track_file_name = 'XZaU-Oqo-qs List.txt'
    in_length = None


    if in_album_filename:
        album_filename = in_album_filename

    if in_yt_url:
        try:
            url_data = urlparse(in_yt_url)
            query = parse_qs(url_data.query)
            video_id = query['v'][0]
        except:
            video_id = in_yt_url
        # TODO: os.path
        album_filename = video_id + '.mp3'
        # opts=['--extract-audio','--audio-format', 'mp3', '--audio-quality', '0', in_yt_url.decode('utf-8'), '-o', FILENAME.decode('utf-8')]
        print("Downloading video from YouTube")
        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            ydl_info = ydl.extract_info('http://www.youtube.com/watch?v=' + video_id)
            #ydl.download(['http://www.youtube.com/watch?v=' + video_id])
            # ydl_info.thumbnail
        print("\nConversion to mp3 complete")

    pprint(ydl_info)
    if in_folder:
        path = in_folder
    else:
        path = ydl_info[title]
    # Only workable with v3.2+
    # TODO: make compatible for Python 2
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    exit()
    album = AudioSegment.from_mp3(album_filename)
    total_length = album.duration_seconds  # milliseconds
    track_regex = re.compile("^(.+)\s+\((.+)\)")
    track_list = []
    if in_length:
        time_index = 'length'
    else:
        time_index = 'start'

    with open(in_track_file_name, 'r') as f:
        for line in f:
            if line == "\n":
                next
            m = track_regex.match(line)
            track_str = m.group(1)
            time_str = m.group(2)

            if len(time_str.split(':')) == 2:
                time_format_str = '%M:%S'
            elif len(time_str.split(':')) == 3:
                time_format_str = '%H:%M:%S'

            x = time.strptime(time_str, time_format_str)
            total_seconds = datetime.timedelta(hours=x.tm_hour,
                                               minutes=x.tm_min,
                                               seconds=x.tm_sec
                                               ).total_seconds()
            track_list.append({'title': track_str, time_index: total_seconds})

    # Calculate the other variable needed (length for start, start for length).
    for i, track in enumerate(track_list):
        if 'start' not in track:
            # Calculate start
            if i == 0:
                track['start'] = 0
            else:
                track['start'] = track_list[i-1]['start'] + \
                    track_list[i-1]['length']
        if 'length' not in track:
            if i + 1 == len(track_list):
                track['length'] = total_length - track['start']
            else:
                track['length'] = track_list[i+1]['start'] - track['start']

    #import logging
    #l = logging.getLogger("pydub.converter")
    #l.setLevel(logging.DEBUG)
    #l.addHandler(logging.StreamHandler())

    for t in track_list:
        print('Processing track: ' + t['title'])
        t_start = t['start']*1000
        t_dur = t['length']*1000
        track_path = os.path.join(path, t['title'] + '.mp3')
        album[t_start:][:t_dur].export(track_path, format='mp3', parameters=['-write_xing', '0'])

        #track_file = eyed3.load(track_path)
        #track_file.title = track
        #track_file.save()

    #if in_yt_url:
    #    Download image: http://img.youtube.com/vi/VIDEOID/0.jpg
    #    os.remove(album_filename)

    #pprint(track_list)

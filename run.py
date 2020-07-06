# !./.env/bin/python
"""
Run python module
"""
import concurrent.futures
from scraptube import vedit
from scraptube import tubedown
from scraptube import search


def download_videos(youtube_id):
    try:
        video = tubedown.SourceVideo(youtube_id)
        video.download(path=PATH)
        print(f'Downloaded video with id {youtube_id}')
    except:
        print(f'Unable to download {youtube_id}')


EXERCISE = 'deadlift'
QUERY = EXERCISE + ' ,+exercise +routine +fitness'
PATH = './output/' + EXERCISE
youtube_ids = search.YoutubeSearch(QUERY).to_list()

number_of_videos = len(youtube_ids)

print(f'Found {number_of_videos} youtube videos, starting download...')

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(download_videos, youtube_ids)

# video = tubedown.SourceVideo('rJzIcgVqLvU')
# print(video.title)
# video.download()
# for start, end in zip(video.subs_starts, video.subs_ends):
#     vedit.VideoSubClip(video.download_path, start, end)

#!/venv/bin/python3
import youtube_search
from scraptube import tubedown
import json

results = youtube_search.YoutubeSearch(
    'workout videos', max_results=2).to_json()

results_dict = json.loads(results)
video_id = results_dict['videos'][1]['id']
video1 = tubedown.SourceVideo(video_id)
print(video1)

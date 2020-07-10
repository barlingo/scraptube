# !./.env/bin/python
"""
Run python module
"""
import argparse
from scraptube import vedit
from scraptube import search
from scraptube import tubedown

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--search", type=str,
                    help="Performs search on yt")
parser.add_argument("-a", "--added_search", type=str,
                    help="Added arguments to main search query add + for each")
parser.add_argument("-d", "--download", action="store_true",
                    help="Downloads videos from query result ")
parser.add_argument("-f", "--format", type=int,
                    help="Format videos into chucks of N seconds")
parser.add_argument("-c", "--clean", action="store_true",
                    help="Performs data clean of ./output folders")

args = parser.parse_args()


if args.search is not None:
    PATH = './output/' + args.search
    query = args.search + ", " + args.added_search
    yt_search = search.YoutubeSearch(query)
    youtube_ids = yt_search.to_list()
    print(f'Found {yt_search.count} youtube videos for {args.search}, \
          {args.added_search}')

if args.download:
    print("Starting download...")
    extractor = tubedown.extractVideos(PATH, youtube_ids)
    extractor.parallel_download()
    extractor.merge_logs(args.search)
    extractor.purge_logs()

if args.format:
    print(f"Trimming videos on {args.format} seconds chunks")
    PATH = "./output/push up"
    processor = vedit.SubFolderProcessing(PATH)
    processor.process_files(args.format)

if args.clean:
    pass

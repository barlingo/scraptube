# !./.env/bin/python
"""
Run python module
"""
import argparse
import scraptube
import pathlib


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--search", type=str,
                    help="performs search on yt")
parser.add_argument("-a", "--added_search", type=str,
                    help="added arguments to main search query add + for each")
parser.add_argument("-d", "--download", action="store_true",
                    help="downloads videos from query result ")
parser.add_argument("-c", "--clean", action="store_true",
                    help="performs data clean of specified folder")
parser.add_argument("-l", "--label", type=str,
                    help="start labeling videos of specified folder")
parser.add_argument("-n", "--number", action="store_true",
                    help="count the number of entries in all json files")
parser.add_argument("-r", "--review", type=str,
                    help="review the current datasets")
args = parser.parse_args()

MAIN_PATH = './output'

if args.search is None and args.download:
    print("Search required prior to download")

if args.search is not None:
    PATH = MAIN_PATH + '\\' + args.search
    query = args.search + ", " + args.added_search
    yt_search = scraptube.search.YoutubeSearch(query)
    youtube_ids = yt_search.to_list()

    if args.download:
        extractor = scraptube.down.extractVideos(PATH, youtube_ids)
        extractor.parallel_download()
        extractor.merge_logs(args.search)
        extractor.purge_logs()

elif args.clean:
    repeated_files = scraptube.clean.find_repeated_files(MAIN_PATH)
    scraptube.clean.delete_duplicated(repeated_files)

elif args.label:
    processor = scraptube.label.SubFolderProcessing(args.label)
    processor.label_videos()

elif args.number:
    import matplotlib.pyplot as plt
    sum_entries = scraptube.review.count_all_labels(MAIN_PATH, "exercise")
    plt.bar(list(sum_entries.keys()), sum_entries.values())
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.302, top=0.98, right=0.98, left=0.06)
    plt.show()

elif args.review:
    scraptube.review.json_review(args.review)

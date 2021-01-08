"""
Make a dizqueTV channel for a particular movie studio, TV network or streaming platform
(i.e. Sony Pictures, Columbia Pictures, NBC, Comedy Central, Netflix, Apple TV+).
Grabs all items from your Plex library associated with that studio/network/platform.
Creates a dizqueTV channel with all the items.
dizqueTV channel will be named after the studio/network/platform
"""

from typing import List, Union

from plexapi import server, media, library, playlist, myplex
from dizqueTV import API
import argparse
from urllib.parse import quote

parser = argparse.ArgumentParser()
parser.add_argument('--studio',
                    nargs="+",
                    type=str,
                    required=True,
                    help="name of studios, networks or platforms to find items from")
parser.add_argument('--plex-token', type=str, required=True)
parser.add_argument('--plex-url', type=str, required=True)
parser.add_argument('--dizquetv-url', type=str, required=True)
parser.add_argument("-s", "--shuffle", action="store_true", help="Shuffle items once channel is completed.")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose (for debugging)")
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

channel_name = ", ".join(name for name in args.studio)

plex_server = server.PlexServer(args.plex_url, args.plex_token)

all_items = []
for studio in args.studio:
    print(f"Looking up content from {studio}...")
    studio_items = plex_server.library.search(studio=f"{quote(studio)}")
    if studio_items:
        print("Matching items:")
        for item in studio_items:
            if item.studio == studio:
                print(f"{item.studio} - {item.title}")
                all_items.append(item)

if all_items:
    if not args.dry_run:
        dtv = API(url=args.dizquetv_url, verbose=args.verbose)
        if len(dtv.channel_numbers):
            new_channel_number = max(dtv.channel_numbers) + 1
        else:
            new_channel_number = 1
        final_programs = []
        for item in all_items:
            if item.type == 'movie':
                final_programs.append(item)
            elif item.type == 'show':
                print(f"Grabbing episodes of {item.title}...")
                for episode in item.episodes():
                    if (hasattr(episode, "originallyAvailableAt") and episode.originallyAvailableAt) and \
                            (hasattr(episode, "duration") and episode.duration):
                        final_programs.append(episode)
        new_channel = dtv.add_channel(programs=final_programs,
                                      plex_server=plex_server,
                                      number=new_channel_number,
                                      name=f"{channel_name}",
                                      handle_errors=True)
        if new_channel:
            print(f"Channel {new_channel_number} '{channel_name}' successfully created.")
            if args.shuffle:
                new_channel.sort_programs_randomly()
        else:
             print("Something went wrong.")
    else:
            exit(0)
else:
    print(f"Could not find any media items from studio(s)")

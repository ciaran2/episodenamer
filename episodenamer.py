#!/usr/bin/python3

import sys
import os
import shutil
import argparse

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dest-dir", "-d", nargs=1, required=True, help="Destination directory.")
  parser.add_argument("--title", "-t", nargs=1, required=True, help="Title of the show.")
  parser.add_argument("--season", "-s", nargs=1, required=True, help="Season number.")
  parser.add_argument("--min-size", "-m", nargs=1, default="0", help="Minimum size of an episode. Other files will be assumed to be extras")
  parser.add_argument("dirs", nargs="+")

  return parser.parse_args()

def apply_suffix(suffixed_size):
  suffix_table = { 'B': 1,
                   'K': 1024,
                   'M': 1048576,
                   'G': 1073741824}
  suffix = suffixed_size[-1]
  if suffix.isdigit():
    return int(suffixed_size)
  else:
    if suffix in suffix_table:
      return int(suffixed_table[:-1]) * suffix_table[suffix]
    else:
      raise Exception("Invalid size suffix")

def collect_episodes(dirs, min_size):
  episodes = []
  extras = []

  for dir in dirs:
    files = sorted(os.listdir(dir))

    for file in files:
      file = "{}/{}".format(dir, file)
      if os.path.getsize(file) > min_size:
        episodes.append(file)
      else:
        extras.append(file)

  return episodes, extras

def main():
  args = parse_args()

  episodes, extras = collect_episodes(args.dirs, apply_suffix(args.min_size))

  print(episodes, extras)

if __name__ == "__main__":
  main()

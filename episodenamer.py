#!/usr/bin/python3

import sys
import argparse
import re
import functools
import os
import glob
import shutil

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dest-dir", "-d", required=True, help="Destination directory.")
  parser.add_argument("--title", "-t", required=True, help="Title of the show.")
  parser.add_argument("--season", "-s", required=True, help="Season number.")
  parser.add_argument("--min-size", "-m", nargs='?', default="0", help="Minimum size of an episode. Other files will be assumed to be extras")
  parser.add_argument("--extras-dir", "-e", nargs='?', help="Directory where extras are to be placed. Mandatory if --min-size specified.")
  parser.add_argument("--missing-episodes", nargs="*", help="Ranges of episodes that are not present in the source directories.")
  parser.add_argument("--dry-run", action='store_true', help="Dry run mode. Print intended file moves without executing.")
  parser.add_argument("dirs", nargs="+")

  args = parser.parse_args()
  args.min_size = apply_suffix(args.min_size)

  if args.min_size > 0 and not args.extras_dir:
    print("Extras directory must be specified if a minimum size is defined.", file=sys.stderr)
    parser.print_help()
    exit(1)

  ep_ranges = []
  if args.missing_episodes:
    for ep_range_string in args.missing_episodes:
      ep_range = parse_range(ep_range_string)
      if ep_range:
        ep_ranges.append(ep_range)
      else:
        print("Invalid format for missing episode range.", file=sys.stderr)
        parser.print_help()
        exit(1)

  args.missing_episodes = ep_ranges

  return args


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
      return int(suffixed_size[:-1]) * suffix_table[suffix]
    else:
      raise Exception("Invalid size suffix")

def parse_range(range_string):
  if re.fullmatch('\d+-\d+', range_string):
    range_split = range_string.split('-')
    return range(int(range_split[0]), int(range_split[1])+1)
  if re.fullmatch('\d+', range_string):
    return range(int(range_string), int(range_string)+1)
  else:
    return None

def ensure_dirs(dest_dir, extras_dir=None, dry_run=False):
  if dry_run:
    if not os.path.exists(dest_dir):
      print("Creating path {}".format(dest_dir))
    if extras_dir and not os.path.exists(extras_dir):
      print("Creating path {}".format(extras_dir))
  else:
    os.makedirs(dest_dir, mode=0o770, exist_ok=True)

    if extras_dir:
      os.makedirs(extras_dir, mode=0o770, exist_ok=True)


def collect_episodes(dirs, min_size, missing_eps):
  episodes = []
  extras = []
  episode_num = 1

  for dir in dirs:
    files = sorted(os.listdir(dir))

    for file in files:
      while functools.reduce(lambda x, y: x or y, [episode_num in r for r in missing_eps], False):
        episode_num += 1
      file = "{}/{}".format(dir, file)
      if os.path.getsize(file) > min_size:
        episodes.append((episode_num, file))
        episode_num += 1
      else:
        extras.append(file)

  return episodes, extras

def move_episodes(dest_dir, title, season, episodes, dry_run=False):
  for i, episode in episodes:
    _, extension = os.path.splitext(episode)
    dest_path = "{}/{} S{}E{}{}".format(dest_dir, title, season, i, extension)
    if dry_run:
      print("{} -> {}".format(episode, dest_path))
    else:
      shutil.move(episode, dest_path)

def move_extras(extras_dir, title, extras, dry_run=False):
  extra_number = 1

  for extra in extras:
    while len(glob.glob("{}/{} Extra {}.*".format(extras_dir, title, extra_number))) > 0:
      extra_number += 1
    _, extension = os.path.splitext(extra)
    dest_path = "{}/{} Extra {}{}".format(extras_dir, title, extra_number, extension)
    if dry_run:
      print("{} -> {}".format(extra, dest_path))
    else:
      shutil.move(extra, dest_path)
      pass
    extra_number += 1

def main():
  args = parse_args()

  episodes, extras = collect_episodes(args.dirs, args.min_size, args.missing_episodes)

  ensure_dirs(args.dest_dir, args.extras_dir, args.dry_run)
  move_episodes(args.dest_dir, args.title, args.season, episodes, args.dry_run)
  move_extras(args.extras_dir, args.title, extras, args.dry_run)

if __name__ == "__main__":
  main()

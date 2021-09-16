"""
Simple and reusable util functions that can be used in different part of
the project (and in other projects too).
"""

import os
import time
import math
import random
import datetime

import numpy
import torch


def is_power_of_two(n):
    """
    Return True if n is a power of 2
    """
    return (n & (n - 1) == 0) and n != 0


def previous_power_of_2(n):
    """
    Return the biggest power of 2 which is smaller than n
    """
    return 2 ** math.floor(math.log2(n))


def next_power_of_2(n):
    """
    Return the smallest power of 2 which is bigger than n
    """
    return 2 ** math.ceil(math.log2(n))


def add_dict_prefix(d_in, prefix):
    """
    Add prefix sub string to a dictionary string keys
    """
    d_out = {prefix + '_' + k: v for k, v in d_in.items()}
    return d_out


def maybe_makedirs(path_to_create):
    """
    This function will create a directory, unless it exists already.

    Parameters
    ----------
    path_to_create : string
        A string path to a directory you'd like created.
    """
    if not os.path.isdir(path_to_create):
        os.makedirs(path_to_create)


def formatted_time(elapsed_time):
    """
    Given an elapsed time in seconds, return a string with a nice format
    """
    if elapsed_time >= 3600:
        return str(datetime.timedelta(seconds=int(elapsed_time)))
    elif elapsed_time >= 60:
        minutes, seconds = elapsed_time // 60, elapsed_time % 60
        return f"{minutes:.0f} minutes and {seconds:.0f} seconds"
    else:
        return f"{elapsed_time:.2f} seconds"


def formatted_bytes(bytes_number):
    """
    Given a number of bytes, return a string with a nice format
    """
    if bytes_number >= 1024 ** 4:
        return f"{bytes_number / 1024 ** 4:.1f} TB"
    if bytes_number >= 1024 ** 3:
        return f"{bytes_number / 1024 ** 3:.1f} GB"
    if bytes_number >= 1024 ** 2:
        return f"{bytes_number / 1024 ** 2:.1f} MB"
    if bytes_number >= 1024:
        return f"{bytes_number / 1024:.1f} kB"
    else:
        return f"{bytes_number:.0f} bytes"


def print_git_information(repo_base_dir='.'):
    """
    To know where you are in git and print branch and last commit to screen
    """
    try:
        import git
        repo = git.Repo(repo_base_dir)
        branch = repo.active_branch
        commit = repo.head.commit
        print("Git info. Current branch:", branch)
        print("Last commit:", commit, commit.message)
    except:
        print("An exception occurred while printing git information")


def timed_main(use_git=True):
    """
    Decorator for main function. Start/end date-times and elapsed time.
    Accepts an argument use_git to print or not git information.
    """
    def decorator(function):
        def timed_func(*args, **kw):
            start = time.time()
            now = datetime.datetime.now().strftime("%d %B %Y at %H:%M")
            print('Program started', now)
            if use_git:
                print_git_information()
            result = function(*args, **kw)
            now = datetime.datetime.now().strftime("%d %B %Y at %H:%M")
            elapsed_time = time.time() - start
            print('\nProgram finished {}. Elapsed time: {}'
                  .format(now, formatted_time(elapsed_time)))
            return result
        return timed_func
    return decorator


def timed(method):
    """
    Use this decorator if you want to time a method or function.
    """
    def timed_func(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('Function', method.__name__, 'time:',
              round((te - ts) * 1000, 1), 'ms\n')
        return result
    return timed_func


def set_seed(seed_value, use_cuda):
    """
    Set random, numpy, torch and cuda seeds for reproducibility
    """
    random.seed(seed_value)
    numpy.random.seed(seed_value)
    torch.manual_seed(seed_value)
    if use_cuda:
        torch.cuda.manual_seed_all(seed_value)
        torch.cuda.manual_seed(seed_value)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


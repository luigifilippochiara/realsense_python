import sys

sys.path.append('.')  # needed lo launch from root directory
sys.path.append('..')  # needed lo launch from root/scripts
from src.utils import timed_main


@timed_main(use_git=False)
def main():
    print("Hi, I am an empty script!")


if __name__ == '__main__':
    main()

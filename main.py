from src.utils import timed_main, set_seed


@timed_main(use_git=True)
def main():
    # Set seed for reproducibility
    set_seed(seed_value=12345, use_cuda=False)

    print("Hello world!")


if __name__ == '__main__':
    main()

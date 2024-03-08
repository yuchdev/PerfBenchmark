def main():
    """
    Main function to run the CLI version of CPUWatcher
    :return: sys.exit() code
    """
    parser = argparse.ArgumentParser(description="Watch CPU usage of specified processes")
    parser.add_argument('--processes', '-p',
                        metavar='ProcessName',
                        type=str,
                        nargs='+',
                        help='Name of the processes to monitor')
    parser.add_argument('--interval', '-i',
                        type=int,
                        default=5,
                        help='Interval in seconds between each check (default: 5)')
    args = parser.parse_args()

    watcher = CPUWatcher(args.processes, args.interval)
    watcher.watch()
    return 0


if __name__ == "__main__":
    sys.exit(main())

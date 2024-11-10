import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("echo", help="echo the string you use here")
    args = parser.parse_args()
    print(args.echo)

if __name__ == '__main__':
    main()
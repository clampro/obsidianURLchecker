# A simple script that scans your Obsidian vault and checks the status of the URLs in your notes.
# If a URL is not reachable, it will output a log note (URLCheckLog.md) at the root of your vault

# Imports
import sys
import os
import re
import requests
from datetime import datetime

# Exclude these directories from search. You can add more if needed
excludes = {'.obsidian', '.trash'}


def findurl(line):
    # regex found on: https://stackoverflow.com/questions/23394608/python-regex-fails-to-identify-markdown-links

    # Anything that isn't a square closing bracket
    name_regex = "[^]]+"
    # http:// or https:// followed by anything but a closing paren
    url_regex = "http[s]?://[^)]+"

    markup_regex = '\\[({0})]\\(\\s*({1})\\s*\\)'.format(name_regex, url_regex)

    url_list = re.findall(markup_regex, line)
    return url_list


def checkurl(url):

    try:
        r = requests.head(url)
    except requests.exceptions.RequestException:
        return False
    else:
        if str(r.status_code)[0] == '2' or str(r.status_code)[0] == '3':
            return True
        else:
            return False


def main():

    output = []

    # Check command line arguments.
    args = sys.argv[1:]
    path_to_vault = args[0]

    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print("Usage: ", sys.argv[0], "[path to your Obsidian Vault]")
        sys.exit(2)

    # Check if argument passed is a valid path
    if not os.path.isdir(path_to_vault):
        print("Argument entered is not a valid path. Sorry...")
        sys.exit(2)
    else:
        print("Path to Vault set: ", path_to_vault)

    # Scan Obsidian Vault for md files
    print("Now scanning Vault for .md files:")
    print("---------------------------------")

    for dirpath, dirnames, files in os.walk(path_to_vault):
        # Exclude directories from scan
        dirnames[:] = [dirname for dirname in dirnames if dirname not in excludes]
        for filename in files:
            if filename.endswith(".md"):
                path_to_file = os.path.join(dirpath, filename)
                with open(path_to_file, encoding="utf8") as readfile:
                    filelines = readfile.readlines()
                    for line in filelines:
                        urls = findurl(line)
                        if urls:
                            for url in urls:
                                if not checkurl(url[1]):
                                    # append lines to list for logging
                                    output_line = '- ' + '[[' + filename + ']]' + ' : ' + url[0] + ' ' + url[1]
                                    output.append(output_line)

    if output:
        for output_line in output:
            print(output_line)

            output_file_path = os.path.join(path_to_vault, 'URLCheckLog.md')
            with open(output_file_path, "w") as output_file:
                output_line = '# URL Checker Log\n'
                output_file.write(output_line)
                output_line = '---\n'
                output_file.write(output_line)
                output_line = '\n'
                output_file.write(output_line)

                for output_line in output:
                    output_file.write(output_line)
                output_line = '\n'
                output_file.write(output_line)
                output_line = '---\n'
                output_file.write(output_line)
                output_line = 'Log File Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                output_file.write(output_line)
    else:
        print("No problematic urls detected")


if __name__ == "__main__":
    main()

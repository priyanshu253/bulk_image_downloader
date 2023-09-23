import argparse
import os, sys
import shutil
from pathlib import Path
import urllib.request
import urllib.parse
import imghdr
import posixpath
import re
from concurrent.futures import ThreadPoolExecutor


class Download:
    def __init__(self, query, limit, output_dir, adult_filter_off, timeout, max_workers, filter, verbose):
        self.download_count = 0
        self.page_counter = 0

        self.query = query
        assert type(limit) == int, "limit must be an integer"
        self.limit = limit
        self.output_dir = output_dir
        self.adult_filter_off = adult_filter_off
        assert type(timeout) == int, "timeout must be an integer"
        self.timeout = timeout
        assert type(max_workers) == int, "max_workers must be an integer"
        self.max_workers = max_workers
        self.filter = filter
        self.verbose = verbose
        self.seen = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }

    def get_filter(self, shorthand):
        if shorthand == "line" or shorthand == "linedrawing":
            return "+filterui:photo-linedrawing"
        elif shorthand == "photo":
            return "+filterui:photo-photo"
        elif shorthand == "clipart":
            return "+filterui:photo-clipart"
        elif shorthand == "gif" or shorthand == "animatedgif":
            return "+filterui:photo-animatedgif"
        elif shorthand == "transparent":
            return "+filterui:photo-transparent"
        else:
            return ""

    def save_image(self, link, file_path):
        request = urllib.request.Request(link, None, self.headers)
        image = urllib.request.urlopen(request, timeout=self.timeout).read()
        if not imghdr.what(None, image):
            print('[Error] Invalid image, not saving {}\n'.format(link))
            raise ValueError('Invalid image, not saving {}\n'.format(link))
        with open(str(file_path), 'wb') as f:
            f.write(image)

    def download_image(self, link):
        try:
            if self.download_count < self.limit:
                self.download_count += 1
                path = urllib.parse.urlsplit(link).path
                filename = posixpath.basename(path).split('?')[0]
                file_type = filename.split(".")[-1]
                if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                    file_type = "jpg"

                if self.verbose:
                    print("[%] Downloading Image #{} from {}".format(self.download_count, link))

                self.save_image(link, self.output_dir.joinpath("Image_{}.{}".format(
                    str(self.download_count+1), file_type)))
                if self.verbose:
                    print("[%] File Downloaded !\n")

        except Exception as e:
            self.download_count -= 1
            print("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while self.download_count < self.limit:
                if self.verbose:
                    print('\n\n[!!] Indexing page: {}\n'.format(self.page_counter + 1))
                request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.query) \
                              + '&first=' + str(self.page_counter) + '&count=' + str(self.limit) \
                              + '&adlt=' + self.adult_filter_off + '&qft=' + (
                                  '' if self.filter is None else self.get_filter(self.filter))
                request = urllib.request.Request(request_url, None, headers=self.headers)
                response = urllib.request.urlopen(request)
                html = response.read().decode('utf8')
                if html == "":
                    print("[%] No more images are available")
                    break
                links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
                if self.verbose:
                    print("[%] Indexed {} Images on Page {}.".format(len(links), self.page_counter + 1))
                    print("\n===============================================\n")

                for link in links:
                    if link not in self.seen:
                        self.seen.add(link)
                        executor.submit(self.download_image, link)

                self.page_counter += 1
        print("\n\n[%] Done. Downloaded {} images.".format(self.download_count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bulk Image Downloader')
    parser.add_argument('-s', '--search', default='Nature', type=str, help='Search term for images')
    parser.add_argument('-n', '--num_images', default=10, type=int, help='Number of images to download')
    parser.add_argument('-d', '--directory', default='dataset', type=str, help='Directory to save files')
    parser.add_argument('-af', '--adult_filter_off', default=True, help='Turn off adult content filter')
    parser.add_argument('-fr', '--force_replace', default=True, help='Force replace existing files')
    parser.add_argument('-t', '--timeout', default=60, type=int, help='Timeout for each image download')
    parser.add_argument('-w', '--max_workers', default=5, type=int, help='Maximum number of download workers')
    parser.add_argument('-f', '--filter', default='', type=str, help='Image filter such as photo | gif etc.')
    parser.add_argument('-v', '--verbose', default=True, help='Enable verbose mode')

    args = parser.parse_args()

    query = args.search
    limit = args.num_images
    directory = args.directory
    adult_filter_off = args.adult_filter_off
    force_replace = args.force_replace
    timeout = args.timeout
    max_workers = args.max_workers
    filter = args.filter
    verbose = args.verbose

    if adult_filter_off:
        adult_filter_off = 'off'
    else:
        adult_filter_off = 'on'

    output_dir = Path(directory).joinpath(query).absolute()
    if force_replace:
        if Path.is_dir(output_dir):
            shutil.rmtree(output_dir)

    try:
        if not Path.is_dir(output_dir):
            Path.mkdir(output_dir, parents=True)
    except Exception as e:
        print('[Error] Failed to create directory.', e)
        sys.exit(1)

    print("[%] Downloading Images to {}".format(str(output_dir.absolute())))
    download = Download(query, limit, output_dir, adult_filter_off, timeout, max_workers, filter, verbose)
    download.run()

#!/usr/bin/env python
'''
Download the photo of the day from the National Geographic site and set is as
background image.
'''

import os
import subprocess
from collections import namedtuple
from datetime import datetime
from six.moves import urllib
from lxml import etree  # offers Xpath expressions

MAX_KEEP_DAYS = 30
DEFAULT_SITE = 'NG'
IMAGES_DIRECTORY = os.path.expanduser('~/.backgrounds')

UriPair = namedtuple('UriPair', ['url', 'xpath'])

SITES_DICT = {
    'NG': UriPair(url='http://photography.nationalgeographic.com/'
                  'photography/photo-of-the-day/?source=NavPhoPOD',
                  xpath='//div[@class="primary_photo"]//img/@src'),
}


def get_image_url(site):
    '''Find the URI of the image of the day'''

    html_parser = etree.HTMLParser()
    doc = etree.parse(SITES_DICT[site].url, html_parser)
    image_url = doc.xpath(SITES_DICT[site].xpath)[0]
    if not image_url.startswith('http:'):
        image_url = 'http:' + image_url

    return image_url


def save_image(remote_image_uri):
    '''Save the image in the user home directory in a special folder'''

    raw_rem_image = urllib.request.urlopen(remote_image_uri)
    if not os.path.isdir(IMAGES_DIRECTORY):
        os.mkdir(IMAGES_DIRECTORY)
    image_name = os.path.split(remote_image_uri)[-1]
    image_path = os.path.join(IMAGES_DIRECTORY, image_name)
    with open(image_path, 'wb') as local_image:
        local_image.write(raw_rem_image.read())

    return image_path


def clean_up_old_images():
    '''Remove old images'''
    for root, _, files in os.walk(IMAGES_DIRECTORY):
        for img in files:
            img_path = os.path.join(root, img)
            image_atime = datetime.utcfromtimestamp(os.path.getatime(img_path))
            now = datetime.utcnow()
            if (now - image_atime).days > MAX_KEEP_DAYS:
                os.remove(img_path)
                print("Removing %s" % img_path)


def set_background(image_path):
    '''Set the background'''
    subprocess.call(['feh', '--bg-max', image_path])


def main():
    '''Main function'''
    clean_up_old_images()
    local_image = save_image(get_image_url(DEFAULT_SITE))
    set_background(local_image)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2018 Trung Dong Huynh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import csv
import logging
import requests
from pathlib import Path


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import argparse

    base_url = 'https://provenance.ecs.soton.ac.uk'

    parser = argparse.ArgumentParser(
        description='Download a local backup of all your provenance documents on ProvStore. '
                    'Get the API Key for your account at %s/store/account/developer/' % base_url
    )
    parser.add_argument('username', help='your ProvStore username')
    parser.add_argument('api_key', help='your API Key')
    parser.add_argument('-p', '--path', help='the location for the downloaded documents',
                        action='store', default='.')
    parser.add_argument('-d', '--debug', help='enable debug logging',
                        action='store_true', default=False)
    args = parser.parse_args()

    username = args.username
    api_key = args.api_key
    base_path = Path(args.path)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    headers = {
        'Accept': 'application/json',
        'Authorization': 'ApiKey %s:%s' % (username, api_key)
    }

    r = requests.get(base_url + '/store/api/v0/documents/?owner=%s' % username, headers=headers)
    if not r.ok:
        raise SystemExit(
            '[ERROR] Could not list your documents using username <%s> and API Key <%s>: %s - %s' %
            (username, api_key, r.status_code, r.reason)
        )

    response = r.json()
    meta = response['meta']
    logger.debug('Response Meta: %s', meta)
    objects = response['objects']

    print("Backing up %d documents..." % meta['total_count'])

    count_success = count_failed = count_skipped = 0

    meta_filepath = base_path / 'meta.csv'

    with meta_filepath.open('w') as meta_file:
        meta_writer = csv.DictWriter(
            meta_file,
            fieldnames=['id', 'document_name', 'created_at', 'public', 'views_count', 'filename', 'backup_status'],
            extrasaction='ignore'
        )
        meta_writer.writeheader()
        while True:
            for doc in objects:
                print(' - Downloading document #%d [%s]...' % (doc['id'], doc['document_name']))
                filename = '%d.json' % doc['id']
                doc['filename'] = filename
                path = base_path / filename
                if path.exists():
                    print('   [WARNING] <%s> already exists; skipping.' % path)
                    doc['backup_status'] = 'skipped'
                    count_skipped += 1
                else:
                    r = requests.get(base_url + '/store/api/v0/documents/' + filename, headers=headers, stream=True)
                    if r.ok:
                        with path.open('wb') as fd:
                            for chunk in r.iter_content(chunk_size=4096):
                                fd.write(chunk)
                        print('   Saved to: %s' % filename)
                        doc['backup_status'] = 'success'
                        count_success += 1
                    else:
                        print('   [ERROR] ' + r.reason)
                        doc['backup_status'] = 'error'
                        count_failed += 1
                # writing the status
                meta_writer.writerow(doc)

            # check for more documents
            if meta['next']:
                logger.debug('Checking for more documents: %s', meta['next'])
                r = requests.get(base_url + meta['next'], headers=headers)
                if r.ok:
                    response = r.json()
                    meta = response['meta']
                    logger.debug('Response Meta: %s', meta)
                    objects = response['objects']
                else:
                    logger.debug('Response: %s', r.content)
                    break
            else:
                break

    if count_success:
        print('Downloaded and saved %d documents.' % count_success)
    if count_skipped:
        print('Skipped %d documents.' % count_skipped)
    if count_failed:
        print('Failed to download %d documents.' % count_failed)
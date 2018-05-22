# ProvStore Backup and Upload Scripts

## Overview

We are migrating the ProvStore service previously provided by University of
Southampton
[provenance.ecs.soton.ac.uk/store](https://provenance.ecs.soton.ac.uk/store/) to
a new home at [openprovenance.org/store](https://openprovenance.org/store/).

* [provstore-backup.py](provstore-backup.py) script: to download a copy of
your provenance documents on ProvStore.
* [provstore-upload.py](provstore-upload.py) script: to upload your backup
documents back to the new ProvStore.

Use the `--help` option to check the required parameters to use the above
scripts.

## Backup instructions

1. Find or create your API key at Southampton ProvStore: https://provenance.ecs.soton.ac.uk/store/account/developer/
2. Download your documents by running the [provstore-backup.py](provstore-backup.py) script with your username and API key.
    ```bash
    ./provstore-backup.py <username> <api_key>
    ```
    Your documents will be saved in the [PROV-JSON
representation](https://openprovenance.org/prov-json/).

Optionally, you can also specify the path where the downloaded documents will
be stored with `-p <path>`. The script will save a `meta.csv` file to store the
documents' metadata along with the documents.

## Restore instructions

1. Find or create your API key at the new ProvStore: https://openprovenance.org/store/account/developer/
2. Upload your documents by running the [provstore-upload.py](provstore-upload.py) script with your username and API key.
    ```bash
    ./provstore-upload.py <username> <api_key>
    ```
    The script expects to find the `meta.csv` file previously created by the backup script above in the current working folder. You can also specify a different path to the folder containing the downloaded documents with `-p <path>`.

You can interrupt the upload script at any time. The script keeps the status of the current upload in a `status.csv` file so it can resume the uploading from where it was stopped.

## Issues

If you encounter an issue using the scripts above, try to rerun them with the debug option `-d` to see what the issue is.

Please check if someone has already got a [similar issue](https://github.com/trungdong/provstore-backup/issues) before [creating a new issue](https://github.com/trungdong/provstore-backup/issues/new).


Copyright &copy; 2018 Trung Dong Huynh.

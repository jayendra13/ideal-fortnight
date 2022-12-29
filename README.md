# ideal-fortnight

Asynchronously download a large file by splitting it into multiple chunks and downloading each chunk concurrently.

# Usage
```
python src/download.py -h
usage: download.py [-h] [-n NUM_CONNECTIONS] url

positional arguments:
  url                   The url of the file to be downloaded

optional arguments:
  -h, --help            show this help message and exit
  -n NUM_CONNECTIONS, --num_connections NUM_CONNECTIONS
                        Number of concurrent connections to download
```
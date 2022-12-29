"""
Asynchronously download a large file by splitting it into 
multiple chunks and downloading each chunk concurrently.

Server must support range header, to understand what is range header
you can go through 
https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Range
"""

import argparse
import asyncio
import logging
import os
from typing import Tuple
from urllib.parse import urlparse

import aiohttp
import tqdm
import math

#TODO Add Chunksize as argument
parser = argparse.ArgumentParser()
parser.add_argument("url", help="The url of the file to be downloaded")
parser.add_argument("-n",
                    "--num_connections",
                    help="Number of concurrent connections to download",
                    type=int,
                    default=4)


async def download_file_range(url: str,
                              range_: Tuple[int, int],
                              session: aiohttp.ClientSession,
                              pbar: tqdm.tqdm,
                              chunk_size=1024 * 1024) -> bytes:
  """
    Asynchronously download a range of bytes from a file hosted at the given URL.
  """
  start, end = range_
  chunks = []
  async with session.get(url,
                         headers={'Range': f'bytes={start}-{end}'}) as response:
    # Ensure the request was successful
    response.raise_for_status()
    
    while True:
      chunk = await response.content.read(chunk_size)
      if not chunk:
        break
      chunks.append(chunk)
      pbar.update(len(chunk))

  pbar.close()
  return b''.join(chunks)


async def download_file(url: str, num_connections: int = 4):
  """
    Asynchronously download a large file by splitting it into 
    multiple chunks and downloading each chunk concurrently.
  """
  # Get the file size
  async with aiohttp.ClientSession() as session:
    async with session.head(url) as response:
      file_size = int(response.headers['Content-Length'])

    # Calculate the size of each chunk
    chunk_size = math.ceil(file_size / num_connections)

    # Create a progress bar for each task
    pbars = [
        tqdm.tqdm(total=chunk_size,
                  desc=f'Connection: {i+1}/{num_connections}',
                  unit='B',
                  unit_scale=True) for i in range(num_connections)
    ]

    # Create a list of tasks to download each chunk concurrently
    tasks = []
    
    for i,start in enumerate(range(0, file_size, chunk_size)):
      end = start + chunk_size - 1
      if i == num_connections - 1:
          # The last chunk may be smaller than the others, so set the end to the file size
          end = file_size - 1
      
      task = asyncio.create_task(
          download_file_range(url, (start, end), session, pbars[i]))
      tasks.append(task)

    # Wait for all tasks to complete
    chunks = []
    for i, task in enumerate(asyncio.as_completed(tasks)):
      chunk = await task
      chunks.append(chunk)

    # Concatenate the chunks to get the final file
    file_data = b''.join(chunks)
    return file_data


async def main():

  args = parser.parse_args()

  url_info = urlparse(args.url)
  fname = os.path.basename(url_info.path)

  logging.info("Downloading %s with %d connections", args.url,
               args.num_connections)

  file_data = await download_file(args.url, args.num_connections)
  # Do something with the file data
  with open(fname, 'wb') as f:
    f.write(file_data)


if __name__ == "__main__":
  logging.basicConfig()
  asyncio.run(main())

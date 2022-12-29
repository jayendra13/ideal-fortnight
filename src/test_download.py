import os
import tempfile
import aiohttp
from download import download_file

import aiohttp
from aioresponses import aioresponses
from download import download_file_range
import unittest
import tqdm


class TestDownloadFile(unittest.IsolatedAsyncioTestCase):
  """Tests for both async functions present in download.py"""

  async def test_download_file_range(self):
    """Set up a mock server that returns a known set of bytes for the specified range."""
    TEST_URL = "http://test_url/sample"
    TEST_DATA = b'dfddfdfdfdfd'
    async with aiohttp.ClientSession() as session:
      with aioresponses() as m:
        m.get(TEST_URL, headers={'Range': 'bytes 0-9'}, body=TEST_DATA)
        data = await download_file_range(TEST_URL, (0, 9), session,
                                          tqdm.tqdm(total=10))
        self.assertEqual(TEST_DATA, data)

  async def test_download_file(self):
    """Create temporary directory, Download file from url and store it to temporary directory."""
    
    # Create a temporary file to store the downloaded data
    fd, tmp_path = tempfile.mkstemp()

    # Download the file and write the data to the temporary file
    url = 'https://www.python.org/ftp/python/3.4.10/Python-3.4.10.tgz'
    num_connections = 4
    file_data = await download_file(url, num_connections)
    with open(tmp_path, 'wb') as f:
      f.write(file_data)

    expected_size = 19684498

    # Check that the file was downloaded correctly
    assert os.path.exists(tmp_path)
    assert os.path.getsize(tmp_path) == expected_size

    os.close(fd)

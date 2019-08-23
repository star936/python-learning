# coding: utf-8

import pytest
from utils.file import download_csv
import os

data = [(
    'https://raw.githubusercontent.com/realpython/materials/master/itertools-in-python3/SP500.csv',
    'data/SP500.csv')]


@pytest.mark.parametrize('path,filename', data)
def test_download_csv(path, filename):
    download_csv(path, filename)
    assert os.path.exists(filename)

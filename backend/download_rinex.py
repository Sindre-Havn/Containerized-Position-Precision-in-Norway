import requests
import gzip
import os
from pathlib import Path


def download_rinex(day: str, year: int) -> Path:
    """
       Downloads today's RINEX (ephemeris) file from the CDDIS server.
       Assumes .netrc file with correct loggin creditdentials in home directory.
    """
    FOLDER = Path('rinex_unpacking')
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)
    for file in os.listdir(FOLDER):
        os.remove(FOLDER / file)

    gzip_rinex = Path(f'BRD400DLR_S_{year}{day}0000_01D_MN.rnx.gz')
    gzip_path = FOLDER / gzip_rinex
    url = f'https://cddis.nasa.gov/archive/gnss/data/daily/{year}/brdc/{gzip_rinex}'
    r = requests.get(url)
    c = r.content
    with open(gzip_path, 'wb') as fd:
        fd.write(c)
    
    ONE_MB = 2**20
    file_size_bytes = None
    try:
        file_size_bytes = os.path.getsize(gzip_path)
    except Exception:
        raise # Let flask handle this
    
    if file_size_bytes < ONE_MB: # Rinex files is 10 MB+, bad request yield HTML site of ~17kB.
        print('gzipped size', file_size_bytes)
        print('Bad request, did not get RINEX.')
        raise requests.exceptions.RequestException
    
    with open(gzip_path,'rb') as fd:
        gzip_fd = gzip.GzipFile(fileobj=fd)
        gzip_fd = gzip_fd.read()
    print('gzip_path', gzip_path)
    print('gzip_path.stem', gzip_path.stem)
    rinex_path = FOLDER / gzip_rinex.stem
    with open(rinex_path, 'wb') as f:
        f.write(gzip_fd)
    print('rinex_path', rinex_path)
    return rinex_path

    

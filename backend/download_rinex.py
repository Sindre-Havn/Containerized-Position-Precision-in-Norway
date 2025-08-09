import requests
import gzip
import os
from pathlib import Path


def download_rinex(day: str, year: int) -> Path:
    """
       Downloads today's RINEX (ephemeris) file from the CDDIS server.
       Assumes .netrc file with correct loggin creditdentials in home directory.
    """
    gzip_rinex = Path(f'BRD400DLR_S_{year}{day}0000_01D_MN.rnx.gz')
    url = f'https://cddis.nasa.gov/archive/gnss/data/daily/{year}/brdc/{gzip_rinex}'
    r = requests.get(url)
    c = r.content
    with open(gzip_rinex, 'wb') as fd:
        fd.write(c)
    
    ONE_MB = 2**20
    file_size_bytes = None
    try:
        file_size_bytes = os.path.getsize(gzip_rinex)
    except Exception:
        os.remove(gzip_rinex)
        raise # Let flask handle this
    
    if file_size_bytes < ONE_MB: # Rinex files is 10 MB+, bad request yield HTML site of ~17kB.
        print('gzipped size', file_size_bytes)
        print('Bad request, did not get RINEX.')
        os.remove(gzip_rinex)
        raise requests.exceptions.RequestException
    
    rinex_path = gzip_rinex.stem
    with open(gzip_rinex,'rb') as fd:
        gzip_fd = gzip.GzipFile(fileobj=fd)
        gzip_fd = gzip_fd.read()
        
    with open(rinex_path, 'wb') as f:
        f.write(gzip_fd)
        
    os.remove(gzip_rinex)
    
    return rinex_path

    

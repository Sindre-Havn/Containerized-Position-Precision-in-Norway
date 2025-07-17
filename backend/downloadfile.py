import requests
import gzip
import os
from pathlib import Path

# Geth the Broadcast ephemeries file from the CDDIS server
def lastned(day, year):
    folder = Path('unzipped/')
    filename = Path(f'BRD400DLR_S_{year}{day}0000_01D_MN.rnx.gz')
    if Path(folder / filename.stem).is_file():
        #print('File Exists')
        return folder / filename.stem
    
    url = f'https://cddis.nasa.gov/archive/gnss/data/daily/{year}/brdc/{filename}'
    r = requests.get(url)
    c = r.content
    
    with open(filename, 'wb') as fd:
        fd.write(c)


    with open(filename,'rb') as fd:
        gzip_fd = gzip.GzipFile(fileobj=fd)
        gzip_fd = gzip_fd.read()
    
    os.remove(filename)
    
    with open(folder / filename.stem, 'wb') as f:
        f.write(gzip_fd)
    
    return folder / filename.stem




    

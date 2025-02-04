import requests
import gzip
import os
# day = 317
folder = 'unzipped/'

def lastned(day, year):
    print(day)
    filename = f'BRD400DLR_S_{year}{day}0000_01D_MN.rnx.gz'

    url = f'https://cddis.nasa.gov/archive/gnss/data/daily/{year}/brdc/{filename}'

    if not os.path.isfile(folder+filename[:-3]):
        r = requests.get(url)
        c = r.content
        #print(f"request: {r}, content:{c}")
        with open(filename, 'wb') as fd:
            fd.write(c)

        with open(filename,'rb') as fd:
            gzip_fd = gzip.GzipFile(fileobj=fd)
            gzip_fd = gzip_fd.read()
        
        os.remove(filename)

        with open(folder+filename[:-3],'wb') as f:
            f.write(gzip_fd)
    else:
        print('File Exists')

# lastned(day)
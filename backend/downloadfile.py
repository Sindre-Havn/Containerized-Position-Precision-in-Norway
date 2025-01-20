import requests
import gzip
import os
# day = 317
folder = 'backend/unzipped/'

def lastned(day):
    print(day)
    filename = f'BRD400DLR_S_2024{day}0000_01D_MN.rnx.gz'

    url = f'https://cddis.nasa.gov/archive/gnss/data/daily/2024/brdc/{filename}'

    if not os.path.isfile(folder+filename[:-3]):
        r = requests.get(url)
        c = r.content

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
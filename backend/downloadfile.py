import requests
import gzip
import os
import json
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
        
        return os.path.join(folder, filename[:-3]) 
    else:
        print('File Exists')
        return os.path.join(folder, filename[:-3]) 

# lastned(day)

def downloadRoad(roadname):
    url = f"https://nvdbapiles-v3.utv.atlas.vegvesen.no/vegnett/veglenkesekvenser?vegsystemreferanse={roadname}"
    header = {
        "Accept": "application/json",
        "X-Client": "Masteroppgave-vegnett"
        }
    response = requests.get(url, headers=header)

    if response.status_code == 200:
        data = response.json()
        return data
        #print(data)
        #create a file with the data as json data
        # print(len(data['objekter'][0]['veglenker']))

        # with open(f'{roadname}.json', 'w',  encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print("Error:", response)

    

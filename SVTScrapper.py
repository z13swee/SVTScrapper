from lxml import html
from bs4 import BeautifulSoup
import requests
import json
import re
from pathlib import Path


def DownloadFile(url,filename):
    local_filename = filename #url.split('/')[-1]
    r = requests.get(url)
    fil = Path("/"+filename)
    if fil.is_file():
        print("File already exists, skippin")
    else:
        f = open(local_filename, 'wb')
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
        f.close()

    return

def urlify(s):
     # Remove all non-word characters (everything except numbers and letters)
     s = re.sub(r"[^\w\s]", '', s)

     # Replace all runs of whitespace with a single dash
     s = re.sub(r"\s+", '_', s)
     return s

class menyObj:
    idd=0
    name=""
    grupp=""

    def __init__(self,name, grupp):
        self.name = name
        self.grupp = grupp
        menyObj.idd += 1


menyLista = []
loop = True

## Sida som listar alla karaktärer
page = requests.get('http://sverigesradio.se/sida/artikel.aspx?programid=2399&artikel=6119876')
print('Page Status_Code: ', page.status_code)

# Skapa BeautifulSoup objekt med våran sida
soup = BeautifulSoup(page.content, 'html.parser')

container = soup.find("div", class_="publication-body-text text-editor-content")
                                    

links = container.find_all("a")

#
for link in links:
    #print(link.get_text())
    #print("Länk: ",link.get('href'))

    grupp=link.get('href')[link.get('href').find("grupp=")+6:]
    #print("Grupp:",grupp,"\n")

    menyLista.append(menyObj(link.get_text(),grupp))

print("Välj karaktär neda:")
ctr=0
for item in menyLista:
    print(ctr,item.name)
    ctr += 1

val = input("Välj: ")
print(menyLista[int(val)].grupp)

#Behöver endast gruppid't för att skicka vidare till nerladdningen

sida=0
antalObj=0
while(loop):
    sida += 1
    page = requests.get('http://sverigesradio.se/sida/grupp/getGroupFlow?unitid=2399&page='+str(sida)+'&groupid='+menyLista[int(val)].grupp)

    # Skriv ut status koden vi får tillbaka från servern..
    print('Page Status_Code: ', page.status_code)
    if page.status_code == 200:
        print("Sida: ",sida)

        # Skapa BeautifulSoup objekt med våran sida
        soup = BeautifulSoup(page.content, 'html.parser')

        # Hitta "containern"
        #container = soup.find("ul", class_="puff-flow")
        #puffflow_item = container.find_all(class_="puff-flow__item")
        puffflow_item = soup.find_all(class_="puff-flow__item")

        if puffflow_item:
            for item in puffflow_item:
                print(item.find("abbr").get_text())
                print("id=",item.get('id')) # id här verkar också alltid vara samma som på data-audio-id variablen som skickas med länken
                audioId = item.get('id')
                audioUrl = requests.get('http://sverigesradio.se/sida/playerajax/getaudiourl?id='+audioId+'&type=publication&quality=high&format=iis')
                x=audioUrl.json()
                titel=item.find("abbr").get_text()


                print("Förslag till Titel: ",urlify(titel)+ x['audioUrl'][-4:])
                print("url:", x['audioUrl'])
                print("Downloading..\n")
                DownloadFile(x['audioUrl'],urlify(titel)+ x['audioUrl'][-4:])

                antalObj += 1
                #page = requests.get('http://sverigesradio.se/sida/grupp/getGroupFlow?unitid=2399&page='+str(sida)+'&groupid=2471')
        else:
            print("Inga fler sidor")
            loop=False
    else:
            print("Bad respone: ",page.status_code)
print("Antal objekt nedladdade ", antalObj)

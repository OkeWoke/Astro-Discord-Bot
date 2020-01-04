import time, asyncio, aiohttp, re
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET

async def resolve_img(objname, radii):
    """Takes astro object name as string, radius of fov float, and saves a jpg file, returns string filename"""
    url ="https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?Survey=dss2r&Position={0}&Size={1}&Pixels={2}&Return=PNG".format(objname,radii,500)

    filename = str(int(time.time()*1000000))+'.png'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            async with resp:
                if resp.status != 200:
                    return "Error: HTTP 200 not received (connection to survey unavailable )"

                if resp.content_type == 'text/html':
                    with open('dss_res_img_log.txt','a+') as f:
                        f.write(await resp.text())
                    return "Error: Invalid object name"
                data = await resp.read()
                
                with open(filename, "wb") as f:
                    f.write(data)
        
    return filename
    
    
async def resolve_object(objname):
    """Takes an object name, requests simbad and returns RA and DEC coordinate string tuple pair (ICRS j2k) """
    url = "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=VOtable&obj.bibsel=off&Ident={0}".format(objname)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            async with resp:
                if resp.status != 200:
                    return "Error: HTTP 200 not received (connection to simbad unavailable )"
                resp_text = await resp.text()

                root = ET.fromstring(resp_text)
                child = root.find(".{http://www.ivoa.net/xml/VOTable/v1.2}INFO")
                
                if child != None: #possible error
                    if child.attrib["name"] == 'Error':
                        return "Error: {0}".format(child.attrib['value'])
                        
                new_root = root.findall(".{http://www.ivoa.net/xml/VOTable/v1.2}RESOURCE/*{http://www.ivoa.net/xml/VOTable/v1.2}FIELD")
                for ra_i, child in enumerate(new_root, 0):
                    if child.attrib["ID"] == "RA_d":
                        break
                for dec_i, child in enumerate(new_root, 0):
                    if child.attrib["ID"] == "DEC_d":
                        break      

                data_root = root.findall(".{http://www.ivoa.net/xml/VOTable/v1.2}RESOURCE/*{http://www.ivoa.net/xml/VOTable/v1.2}DATA/{http://www.ivoa.net/xml/VOTable/v1.2}TABLEDATA/{http://www.ivoa.net/xml/VOTable/v1.2}TR/")

                RA_d = float(data_root[ra_i].text)
                DEC_d = float(data_root[dec_i].text)

                def degToHMS(angle):
                   
                   
                    h = int(angle/15)
                    angle-=h*15
                    m = int(angle/0.25)
                    angle-=m*0.25
                    s = int(angle/0.0041667)
              
                    return [h,m,s]
                    
                def degToDMS(angle):
                    d = int(angle)
                    angle -=d
                    if d<0:
                        angle*=-1
                    m = int(angle/0.016666667)
                    angle-=m*0.01666667
                    s = int(angle/0.00027777)
                    
                    return [d,m,s]
                    
                RA = degToHMS(RA_d)
                DEC = degToDMS(DEC_d)
                RA_s = "{0}h {1}m {2}s".format(RA[0], RA[1], RA[2])
                DEC_s = "{0}d {1}m {2}s".format(DEC[0], DEC[1], DEC[2])
              
                return (RA_s, DEC_s)                   

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        a= input()
        print(loop.run_until_complete(resolve_object(a)))
    loop.close()
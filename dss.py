import time, asyncio, aiohttp, re
from PIL import Image
import numpy as np

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
    url = "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=ASCII&obj.bibsel=off&Ident={0}".format(objname)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            async with resp:
                if resp.status != 200:
                    return "Error: HTTP 200 not received (connection to simbad unavailable )"
                resp_text = await resp.text()
                
                if "No known catalog could be found" or "this identifier has an incorrect format for catalog"  in resp_text:
                    with open('dss_res_obj_log.txt','a+') as f:
                        f.write(await resp.text())
                    return "Error: Invalid object name"
                    
                coord_i = re.search("Coordinates\(ICRS,ep=J2000,eq=2000\): \d\d \d\d \d\d\.?\d*  [+-]\d\d \d\d \d\d\.?\d*",resp_text)
               
                if(coord_i == None):
                    return "Error: Coordinates not found in response"

                resp_text = resp_text[coord_i.start():coord_i.end()]
                RA_i = re.search("\d\d \d\d \d\d\.?\d*",resp_text)
                RA = resp_text[RA_i.start():RA_i.end()].split(' ')
                
                DEC_i = re.search("[+-]\d\d \d\d \d\d\.?\d*",resp_text)
                DEC = resp_text[DEC_i.start():DEC_i.end()].split(' ')
                
                RA_s = "{0}h {1}m {2}s".format(RA[0], RA[1], RA[2][0:2])
                DEC_s = "{0}d {1}m {2}s".format(DEC[0], DEC[1], DEC[2][0:2])
              
                return (RA_s, DEC_s)                   

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        a= input()
        print(loop.run_until_complete(resolve_img(a,1)))
    loop.close()
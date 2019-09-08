import time, asyncio, aiohttp
from PIL import Image
import numpy as np

async def reqImg(objname, radii):
    """Takes astro object name as string, radius of fov float, and saves a jpg file, returns string filename"""
    url ="https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?Survey=dss2r&Position={0}&Size={1}&Pixels={2}&Return=PNG".format(objname,radii,500)

    filename = str(int(time.time()*1000000))+'.png'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            async with resp:
                if resp.status != 200:
                    return "Error: HTTP 200 not received (connection to survey unavailable )"

                if resp.content_type == 'text/html':
                    return "Error: Invalid object name"
                data = await resp.read()
                
                with open(filename, "wb") as f:
                    f.write(data)
        
    return filename
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reqImg("Eta Carina",1))
    loop.close()
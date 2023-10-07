# from obswebsocket import obsws, requests
# client = obsws("localhost", 4444, "123", legacy=True)
# client.connect()
# client.call(requests.GetVersion()).getObsStudioVersion()
# client.call(requests.SetFilenameFormatting())
# client.disconnect()
import asyncio
import simpleobsws

# class obstracker():
#     def __init__(self, host, port, password):
#         self.
#         self.host = host
#         self.port = port
#         self.password = password
#         self.ws = simpleobsws.obsws(host=self.host, port=self.port, password=self.password, loop=self.loop)
        
#     async def connect(self):
#             self.loop.run_until_complete(self.ws.connect())

#     async def disconnect(self):
#         await self.ws.disconnect()

#     def call(self, request):
#         return self.ws.call(request)
    
    
# 
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host='127.0.0.1', port=4444, password='123', loop=loop) # Every possible argument has been passed, but none are required. See lib code for defaults.

async def make_request():
    await ws.connect() # Make the connection to OBS-Websocket
    result = await ws.call('GetVersion') # We get the current OBS version. More request data is not required
    print(result) # Print the raw json output of the GetVersion request
    await asyncio.sleep(1)
    data = {'filename-formatting':"sad"}
    result = await ws.call('SetFilenameFormatting', data) # Make a request with the given data
    print(result)
    await asyncio.sleep(1)
    await ws.call('StartRecording') # StartRecording
    await asyncio.sleep(1)
    timecode = await ws.call('GetRecordingStatus') # GetTimecode
    print(timecode)
    await asyncio.sleep(15)
    await ws.call('StopRecording') # StopRecording
    
    await ws.disconnect() # Clean things up by disconnecting. Only really required in a few specific situations, but good practice if you are done making requests or listening to events.

loop.run_until_complete(make_request())
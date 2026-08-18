# Create a server instance
import asyncio
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("http://opcua-demo.wisdom")
    idx = await server.register_namespace("http://opcua-demo.wisdom")
    myobj = await server.noddes.objects.add_object(idx, "MyObject")
    myvar = await myobj.add_variable(idx, "MyVariable", 6.7)
    await myvar.set_writable()
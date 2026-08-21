# Create a server instance
import asyncio
import random
from asyncua import Server

async def main():
    server = Server()
    await server.init() # Initialize the server
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/") # Set the endpoint for the server
    idx = await server.register_namespace("http://opcua-demo.wisdom") # Register a new namespace for the server

    myobj = await server.nodes.objects.add_object(idx, "MyObject") # Add a new object to the server
    temperature = await myobj.add_variable(idx, "Temperature", 21.5) # 1st variable
    counter = await myobj.add_variable(idx, "Counter", 0) # 2nd variable
    await temperature.set_writable() # Set the variables to be writable
    await counter.set_writable() # Set the variables to be writable
    async with server: # Start the server
        # increment the counter every second
            while True:
                temp_value = await temperature.read_value() # Generate a random temperature value between 20.0 and 25.0
                await temperature.write_value(max(18.0, min(25.0, temp_value + random.uniform(-0.2, 0.2)))) # Write the random temperature value to "Temperature"
                counter_value = await counter.read_value() # Read the current value of "Counter"
                await counter.write_value(counter_value + 1) # Increment the value of "Counter" by 1
                await asyncio.sleep(1) # Sleep for 1 second before the next iteration

if __name__ == "__main__":
    asyncio.run(main())
    
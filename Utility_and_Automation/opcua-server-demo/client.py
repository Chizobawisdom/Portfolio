# Create a client instance
from asyncua import Client

async def main():
    async with Client("opc.tcp://localhost:4840/freeopcua/server/") as client: # Connect to the server
        objects = client.nodes.objects # Get the objects node of the server
        nsidx = await client.get_namespace_index("http://opcua-demo.wisdom") # Get the namespace index for the registered namespace
        myobj = await objects.get_child([f"{nsidx}:MyObject"]) # Get the "MyObject" node from the server

        temperature = await myobj.get_child([f"{nsidx}:Temperature"]) # Get the "Temperature" variable from "MyObject"
        counter = await myobj.get_child([f"{nsidx}:Counter"]) # Get the "Counter" variable from "MyObject"

        while True: # Run indefinitely
            temp_value = await temperature.read_value() # Read the value of "Temperature"
            counter_value = await counter.read_value() # Read the value of "Counter"
            print(f"Temperature: {temp_value}, Counter: {counter_value}") # Print the values
            await asyncio.sleep(1) # Sleep for 1 second before the next iteration

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) # Run the main function
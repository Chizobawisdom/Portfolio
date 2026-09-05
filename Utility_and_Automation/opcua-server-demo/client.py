# Create a client instance
from asyncua import Client, ua
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

async def main():
    client = Client(url="opc.tcp://localhost:4840/freeopcua/server/")
    client.application_uri = "urn:opcua-demo:client"
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate="client_cert.pem",
        private_key="client_key.pem",
        server_certificate="server_cert.pem",
        mode=ua.MessageSecurityMode.SignAndEncrypt
    )
    async with client as client: # Connect to the server
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
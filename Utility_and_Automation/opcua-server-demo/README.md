# OPC-UA Server & Client Demo

A minimal but fully secured OPC-UA server/client pair, built from scratch in Python with `asyncua` to understand the protocol that bridges shop-floor equipment to SCADA, MES, and cloud systems in modern manufacturing.

Where the [PLC-to-Cloud OEE Monitor](../plc-cloud-oee-monitor) project uses raw Modbus TCP; fast and simple, but plaintext and structureless, this project demonstrates the layer above it: a self-describing, encrypted, standards-based interface that any compliant OPC-UA client can browse and trust without prior knowledge of what's inside.

## What it does

- Runs an OPC-UA server exposing a simulated device (`MyObject`) with two live variables:
  - `Temperature` : drifts randomly within a realistic range each second
  - `Counter` : increments by 1 every second
- Runs an independent OPC-UA client that connects, resolves the server's namespace, browses its address space, and polls both values in real time
- Secures the connection end-to-end with **mutual X.509 certificate authentication** and the `Basic256Sha256` security policy in `SignAndEncrypt` mode: the same class of security used in real industrial OPC-UA deployments, not a toy simplification

## Why this matters

Most public OPC-UA tutorials stop at an unsecured "Hello World" server. Getting security working is where the protocol's actual complexity lives: certificate generation, Subject Alternative Name (SAN) matching, application URI alignment between code and certificate, and mutual trust between two independently-generated identities. This project deliberately builds through that complexity rather than skipping it, because an unsecured OPC-UA server in a real industrial network is a genuine liability, not just an incomplete demo.

## Architecture

```
┌─────────────────────┐         Encrypted (Basic256Sha256,          ┌─────────────────────┐
│   OPC-UA Server      │◄────── SignAndEncrypt) mutual-cert ───────►│   OPC-UA Client      │
│                      │              connection                    │                      │
│  MyObject            │                                             │  1. Connects         │
│   ├─ Temperature     │                                             │  2. Resolves the     │
│   └─ Counter         │                                             │     namespace index  │
│                      │                                             │  3. Browses to       │
│  Identified by:      │                                             │     MyObject         │
│  urn:opcua-demo:     │                                             │  4. Polls values     │
│  server              │                                             │     every second     │
└─────────────────────┘                                             └─────────────────────┘
     server_cert.pem                                                     client_cert.pem
     server_key.pem                                                      client_key.pem
```

Each side has its own certificate/key pair. The client verifies the server's certificate before trusting it, and vice versa — this is what "mutual" authentication means, as opposed to a typical HTTPS website where only the server proves its identity to the browser.

## Tech stack

- **Protocol implementation:** [asyncua](https://github.com/FreeOpcUa/opcua-asyncio): an async-native Python implementation of OPC-UA
- **Security:** self-signed X.509 certificates generated with OpenSSL, `Basic256Sha256` policy, `SignAndEncrypt` message mode

## Project structure

```
opcua-server-demo/
├── server.py           # OPC-UA server: exposes MyObject/Temperature/Counter
├── client.py           # OPC-UA client: connects, browses, polls values
├── requirements.txt
├── server_cert.pem     # generated locally, not committed
├── server_key.pem      # generated locally, not committed
├── client_cert.pem     # generated locally, not committed
└── client_key.pem      # generated locally, not committed
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Generate the server certificate. The Subject Alternative Name (SAN) **must** include the application URI used in `server.py`, plus every hostname the server might be reached at:
   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout server_key.pem -out server_cert.pem \
     -days 365 -nodes \
     -subj "/CN=opcua-demo-server" \
     -addext "subjectAltName=URI:urn:opcua-demo:server,DNS:localhost,DNS:$(hostname)"
   ```

4. Generate the client certificate the same way, with its own distinct URI:
   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout client_key.pem -out client_cert.pem \
     -days 365 -nodes \
     -subj "/CN=opcua-demo-client" \
     -addext "subjectAltName=URI:urn:opcua-demo:client,DNS:localhost,DNS:$(hostname)"
   ```

5. Verify each certificate's SAN embedded correctly:
   ```bash
   openssl x509 -in server_cert.pem -noout -text | grep -A1 "Subject Alternative Name"
   ```

## Usage

In one terminal, start the server:
```bash
python server.py
```

In a second terminal (same venv), run the client:
```bash
python client.py
```

You should see live, changing values printed roughly once per second:
```
Temperature: 21.63, Counter: 42
Temperature: 21.58, Counter: 43
Temperature: 21.71, Counter: 44
```

## Design notes

- **Namespace index vs. namespace URI:** the numeric namespace index assigned by `register_namespace()` is not guaranteed to be stable or predictable — the client resolves it at runtime via `get_namespace_index()` using the namespace's URI string, which is the actual stable identifier.
- **Application URI must match the certificate's SAN, on both ends independently.** This is the single most common cause of OPC-UA connection failures, and was hit twice during development of this project once for the server, once for the client before both were aligned correctly.
- **Security policy is intentionally restrictive:** the server only offers `Basic256Sha256_SignAndEncrypt`, meaning any client that doesn't support or request that exact policy simply cannot connect. This is a deliberate choice to force the secure path rather than allowing a silent fallback to an unencrypted connection.

## Known limitations / possible next steps

- Certificates are self-signed rather than issued by a trusted CA appropriate for a local demo, not for production without further certificate management infrastructure.
- Data is simulated rather than sourced from a real PLC. Kept intentionally separate from the [PLC-to-Cloud OEE Monitor](../plc-cloud-oee-monitor) project so each demonstrates its own layer of the stack independently.
- No historical data access or alarms/conditions, this demo covers the core read/subscribe pattern, not OPC-UA's full feature surface.

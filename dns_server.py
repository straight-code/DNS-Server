import socket
import json
from dnslib import *

# Load DNS records from the JSON file
try:
    with open("db.json", "r") as f:
        dns_records = json.load(f)
except json.decoder.JSONDecodeError:
    print("Error: Invalid JSON data in db.json file.")


# Function to add a DNS record to the dictionary
def add_dns_record(name, record_type, value):
    # Load existing DNS records from the JSON file
    with open("db.json", "r") as f:
        dns_records = json.load(f)

    # Add the new record to the dictionary
    if name not in dns_records:
        dns_records[name] = {}
    dns_records[name][record_type] = value

    # Save the updated DNS records to the JSON file
    with open("db.json", "w") as f:
        json.dump(dns_records, f)

    print(f"Added DNS record: {name} {record_type} {value}")

# Function to handle DNS queries and return a response
def handle_dns_query(data):
    request = DNSRecord.parse(data)

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = str(request.q.qname)
    qtype = request.q.qtype

    if qname in dns_records and qtype in dns_records[qname]:
        if qtype == QTYPE.NS:
            reply.add_answer(RR(rname=qname, rtype=qtype, rdata=NS(dns_records[qname][qtype])))
        else:
            reply.add_answer(RR(rname=qname, rtype=qtype, rdata=A(dns_records[qname][qtype])))
    else:
        reply.add_answer(RR(rname=qname, rtype=qtype, rdata=A('0.0.0.0')))

    return reply.pack()

# Function to start the DNS server and listen for requests
def start_dns_server():
    host = ''
    port = 53

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    print(f'DNS server listening on port {port}... \n \n' )

    while True:
        data, address = server_socket.recvfrom(1024)
        response = handle_dns_query(data)
        server_socket.sendto(response, address)

# User interface to add and lookup DNS records
while True:
    choice = input('\n \n \n - "1" to add a DNS record, \n \n - "2" to add a name server record, \n \n - "3" to lookup a DNS record: \n \n \n')

    if choice == '1':
        name = input('Enter the name of the DNS record: \n ')
        record_type = input('Enter the type of the DNS record (A, AAAA, MX, etc.): \n')
        value = input('Enter the value of the DNS record: \n')
        add_dns_record(name, record_type, value)
        print(f'DNS record added: {name} {record_type} {value} \n')

    elif choice == '2':
        name = input('Enter the name of the domain: \n')
        ns_value = input('Enter the name server value: \n')
        add_dns_record(name, QTYPE.NS, ns_value)
        print(f'NS record added for {name}: {ns_value} \n')

    elif choice == '3':
        name = input('Enter the name of the DNS record: \n')
        record_type = input('Enter the type of the DNS record (A, AAAA, MX, NS, etc.):\n ')

        if name in dns_records and record_type in dns_records[name]:
            print(f'{name} {record_type} {dns_records[name][record_type]}')
        else:
            print(f'DNS record not found: {name} {record_type} \n')

    else:
        print('Invalid choice. Please enter "1", "2", or "3". \n \n try again... \n \n')

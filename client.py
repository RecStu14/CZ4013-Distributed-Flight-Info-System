import socket
import sys
from helper_fxns import acknowledge_request
import marshalling.marshalling_logic as MARSHALLING

print("----------Welcome to the Flight Information System!----------")

#Instatiating important values
UDP_IP_ADDRESS = "172.20.10.3"
UDP_PORT_NUM = 6789

TIMEOUT_SECONDS = 5

encoded_client_message, request_id = MARSHALLING.marshall(sys.argv[1])

#Create a UDP socket at a client side
UDP_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


if sys.argv[1].split(",")[0] != "monitor_interval":
    UDP_client_socket.settimeout(TIMEOUT_SECONDS)

while True:
    try:
        #Send to server using created UDP socket
        UDP_client_socket.sendto(encoded_client_message, (UDP_IP_ADDRESS, UDP_PORT_NUM))
        
        #Listening from Server
        print("INFO: Receiving message from server...")
        message_from_server = UDP_client_socket.recvfrom(1024)
        message, address = message_from_server[0], message_from_server[1]

        decoded_message = MARSHALLING.unmarshall(message)

        # If message received from server is ack
        if decoded_message == f"ACK,{request_id}":
            print(f"Message from Server:\n{decoded_message}")
            message_from_server = UDP_client_socket.recvfrom(1024)
            message, address = message_from_server[0], message_from_server[1]
            response_message = MARSHALLING.unmarshall(message)
            
            # if ack is from monitor_interval, then keep listening for updates
            if sys.argv[1].split(",")[0] == "monitor_interval":
                while True:
                    message_from_server = UDP_client_socket.recvfrom(1024)
                    message, address = message_from_server[0], message_from_server[1]
                    response_message = MARSHALLING.unmarshall(message)
            # if ack is from anything else, then break
            else:
                break

        # If message received from server, reply with ack
        ack = acknowledge_request(decoded_message)
        UDP_client_socket.sendto(ack, address)
        print("Sent acknowledgement to server {}".format(address))

    except socket.timeout:
        # At least once semantics by resending message if timeout reached
        print("INFO: Timeout exceeded. Resending message...")

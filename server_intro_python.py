#SOCKET PROGRAMMING

#Imports
import socket
import flights_db as FLIGHTS
import helper_fxns as HELPER_FXNS
import time

#initialising the IP address, port number and buffer size
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NUM = 6789

# query flight identifier given source and destination by client and return flight id(s)
def query_flight(source, destination):
    print(f"INFO: Querying flight from {source} to {destination}...")
    #list of flight ids that match
    flight_id = []
    for flight in FLIGHTS.flights:
        if FLIGHTS.flights[flight]["source"] == source and FLIGHTS.flights[flight]["destination"] == destination:
            flight_id.append(flight)
    return flight_id

# query the departure time, airfare and seatavailability by specifying the flight identifier, else error
def query_flight_details(flight_id):
    print(f"INFO: Querying flight details for flight {flight_id}...")
    if flight_id in FLIGHTS.flights:
        return FLIGHTS.flights[flight_id]
    else:
        return "ERROR: Flight does not exist"

# reserve seats for a flight by specifying the flight identifier and number of seats to reserve, else error
def reserve_seats(flight_id, seats):
    print(f"INFO: Reserving {seats} seats for flight {flight_id}...")
    if flight_id in FLIGHTS.flights:
        if FLIGHTS.flights[flight_id]["seats_available"] >= seats:
            FLIGHTS.flights[flight_id]["seats_available"] -= seats
            print(f"INFO: Seats available for flight {flight_id}: {FLIGHTS.flights[flight_id]['seats_available']}")
            return f"{seats} Seats successfully reserved for Flight {flight_id}!"
        else:
            return "ERROR: Not enough seats available"
    else:
        return "ERROR: Flight does not exist"
    
#announcing delay of departure of flight
def add_delay(flight_id, delay):
    print(f"INFO: Adding {delay} hours delay to flight {flight_id}...")
    if flight_id in FLIGHTS.flights:
        FLIGHTS.flights[flight_id]["departure_time"]["hour"] += delay
        print(f"INFO: Flight {flight_id} delayed by {delay} hours")
        return "Flight delayed"
    else:
        return "ERROR: Flight does not exist"
    

def query_flight_from_source(source):
    print(f"INFO: Querying flights from {source}...")
    flight_id = []
    for flight in FLIGHTS.flights:
        if FLIGHTS.flights[flight]["source"] == source:
            flight_id.append(flight)
    return flight_id

#track the seat availability
def monitor_interval(interval, flight_id):
    interval = int(interval)
    flight_id = int(flight_id)

    org_seats = FLIGHTS.flights[flight_id]['seats_available']

    while interval:
        #Displaying the time
        mins, secs = divmod(interval, 1)
        current_seats = FLIGHTS.flights[flight_id]['seats_available']

        #when there is a change in the seats
        if (current_seats != org_seats):
            text = f"INFO: Change in Seat Availability from {org_seats} to {current_seats}!"
            text = str.encode(text)
            UDP_server_socket.sendto(text, address)
        time.sleep(60)
        interval -= 1

    return f"INFO: Final Seat Availability: {current_seats}"

#data to send to client
server_message = "Hello UDP Client!"

#encoded data to send to the client
encoded_server_message = str.encode(server_message)

#Create a datagram socket
UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Binding to the address and IP
UDP_server_socket.bind((UDP_IP_ADDRESS, UDP_PORT_NUM))

print("INFO: UDP Server up and listening...")

#Listen for incoming datagrams
while True:
    byte_address_pair = UDP_server_socket.recvfrom(1024)

    message, address = byte_address_pair[0], byte_address_pair[1]

    print("{}: {}".format(address,message))

    message = message.decode().split(",")
    if message[0] == "query_flight":
        encoded_server_message = str.encode(str(HELPER_FXNS.function_1(query_flight(message[1], message[2]), message[1], message[2])))
    elif message[0] == "query_flight_details":
        encoded_server_message = str.encode(str(HELPER_FXNS.function_2(query_flight_details(int(message[1])),message[1])))
    elif message[0] == "reserve_seats":
        encoded_server_message = str.encode(str(reserve_seats(int(message[1]), int(message[2]))))
    elif message[0] == "add_delay":
        encoded_server_message = str.encode(str(add_delay(int(message[1]), int(message[2]))))
    elif message[0] == "query_flight_from_source":
        encoded_server_message = str.encode(str(query_flight_from_source(message[1])))
    elif message[0] == "monitor_interval":
        encoded_server_message = str.encode(str(monitor_interval(message[1], message[2])))
    else:
        encoded_server_message = str.encode("ERROR: Invalid request")

    #sending a reply to the client
    UDP_server_socket.sendto(encoded_server_message, address)
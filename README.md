# cs3251-PA2
Advanced TCP implementation
# FTA Server
● Command-line: FTA-server X

 	The command-line arguments are:

	X: the port number at which the FTA-server’s UDP socket should bind.

● Command: window W

	(only for projects that support pipelined and bi-directional transfers)

	W: the maximum receiver’s window-size at the FTA-Server (in segments).

● Command: terminate

	Shut-down FTA-Server gracefully.

# FTA Client

● Command-line: FTA-client A P

 	The command-line arguments are:

           	A: the IP address of FTA-server

 	     P: the UDP port number of FTA-server

● Command: connect

	The FTA-client connects to the FTA-server.

● Command: get F

	The FTA-client downloads file F from the server (if F exists in the same directory with the FTA-server program).

● Command: post F

	The FTA-client uploads file F to the server (if F exists in the same directory with the FTA-client program).

	This feature will be treated as extra credit for up to 20 project points.

● Command: window W

	(only for projects that support configurable flow window)

	W: the maximum receiver’s window-size at the FTA-Client (in segments).

● Command: disconnect

	The FTA-client terminates gracefully from the FTA-server.

# API

* **class CRPSocket**
	* **__init__(port=None, server=False, initial_window_size=65485, debug=False)**
		* **port (int)**: if initializing a server socket, needed to bind the udp socket. Optional if initializing a client socket.
		* **server (bool)**: optional boolean that indicates whether we initialize a server or client socket.
		* **initial_window_size**: initial receiving window size in packets of 4 bytes. Default value is 65485.
		* **debug**: boolean indicating whether the debug mode is on or off.
		Initializing the socket.
	* **connect(dst_ip, dst_port)**: intended to be called by client only; invoked in order to connect to a server; returns a **Connection** object if successful.
		* **dst_ip (str)**: ip address of the server we are connecting to.
		* **dst_port (int)**: port of the server we are connecting to.
	* **accept()**: intended to be invoked by server only; waits for a connection request from client, returns a **Connection** object if successful.
	* **close()**: called by either server or client, performs different function depending on who calls it; if server, it gracefully closes all connections and terminates; if client, closes the connection to the server, but doesn't terminate the socket.
* **class Connection**
	* **recv()**: called by either client or server when ready to receive data; returns a **bytes** object containing received data.
	* **send_data(data)**: sends data to a server/client specified when creating this **Connection** object.
		* **data (bytes)**: data converted to bytes that we are sending.
* **class Packet**
	* **from_bytes(b)**: creates a Packet object using bytes.
		* **b (bytes)**: CRP packet represented as a **bytes** object.
	* **from_arguments(src_port, dst_port, syn=False, ack=False, fin=False, lst=False, seq_num=None, ack_num=None, window=None, data=0)**: creates a Packet object from arguments.
		* **src_port (int)**: source port.
		* **dst_port (int)**: destination port.
		* **syn (bool)**: SYN flag; default is False.
		* **ack (bool)**: ACK flag; default is False.
		* **fin (bool)**: FIN flag; default is False.
		* **lst (bool)**: LST flag; default is False.
		* **seq_num (int)**: sequence number.
		* **ack_num (int)**: acknowledgement number.
		* **window (int)**: sliding window size.
		* **data (bytes)**: data packet into a packet.
	* **additional properties**:
		* **raw (bytes)**: formed packet represented as bytes.
    * **type (str)**: one of SYN/ACK/FIN/LST/DATA, self-explanatory.
    * **is_valid (bool)**: determined by an internal function; indicates whether the packet is corrupt or not.


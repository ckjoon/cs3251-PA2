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

#FTA Client

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



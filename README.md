# SecureDrop
## Objective
The objective of this project is to introduce you to cryptographic tools via the implementation of a secure
file transfer protocol. Your implementation will be similar to and a subset of a very popular tool used in
Apple devices, called AirDrop. During the process, you will practice many cryptographic and cybersecurity
concepts such as symmetric and asymmetric cryptography, digital certificates, public key infrastructure,
mutual authentication, non-repudiation, confidentiality, integrity protection and password security.
## Overview
Secure file transfer can be useful in many different scenarios, e.g., uploading source code, transmitting
configuration files, transmitting sensitive banking information. For this project, we’ll focus on one scenario —
how can we securely transfer a file to another person’s computer who is in our contact list and on the same
local network (wired or wireless)?  

The project will be implemented as a command-line tool. We'll call the application SecureDrop and the executable secure_drop. For the sake of simplicity, the focus will be on the Linux ecosystem. The Linux VM will be used for all the tests.
## Instructions
### 1. Changing file permissions
In order the run the files from the repository we need to make sure basic_cert.sh and network.py can be run as executables. Run the following commands:
chmod +x basic_cert.sh
chmod +x network.py

### 2. Run and fill out basic_cert.sh
$ ./basic_cert.sh
-----
Country Name (2 letter code) [AU]:US
State or Province Name (full name) [Some-State]:Massachusetts
Locality Name (eg, city) []:Lowell
Organization Name (eg, company) [Internet Widgits Pty Ltd]:UML
Organizational Unit Name (eg, section) []:100
Common Name (e.g. server FQDN or YOUR name) []:test.server
Email Address []:server@gmail.com

### 3. Run secure_drop.py
python3 secure_drop.py

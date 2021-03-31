# <H1 align="center">VPN Server installation tool for Ubuntu server</h1>

<h4 align="center">A Script that handles the installation and configuration of OpenVpn on Ubuntu server distributions (together with CA/server certs ...) and the generation of clients config files containing ca/ta/key/cert.</h4>

<h5 align="center">Project 6 of OpenClassrooms Admin Sys/Cloud<h5>

## Warning
 * this module has been developped for a study project, for demo purposes only, <b>it does not guarantee a satisfying security level allowing it to be used outside lab projects</b> : the main reason (among others) beeing that the CA signing authority is located on the live vpn server !

## Prerequisites

* Ubuntu server distribution

* Python3.X (should already be installed)

* shell python package should be installed on server via pip

## Using

* copy all this folder on your home directory

* modify config.py as required

* use sudo ./vpn.py to execute

* install openvpn package on the client

* copy the ~/client-config/files/clientX.conf of the server side to the client /etc/openvpn/

* start the clientX connection [sudo systemctl start openvpn@clientx]

* if everything went well (eg : you were able to ping your distant lan from the client) : enable the client at startup if needed [sudo systemctl enable openvpn@clientX]

## Credits

original procedure by :
[Mark Drake](https://www.digitalocean.com/community/users/mdrake)

<h3>Many thanks to all contributors from the Python community.</h3>

## Author

**Paul Girmes** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

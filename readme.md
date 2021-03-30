# <H1 align="center">VPN Server installation tool for Ubuntu server</h1>

<h4 align="center">A Script that handles the installation and configuration of OpenVpn on Ubuntu server distributions (together with CA/server certs ...) .</h4>

<h5 align="center">Project 6 of OpenClassrooms Admin Sys/Cloud<h5>

## Prerequisites

* Ubuntu server distribution

* Python3.X (should already be installed)

* shell python package

## Using

* copy all this folder on your home directory

* modify config.py as required

* use sudo ./vpn.py to execute

* please note that the client side of OpenVpn configuration is not yet handled by this script
please follow this link to generate your clients certs [procedure](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-18-04). Don't forget to update the server.conf file if you need clients lan routes to be accessed.

## Credits

original procedure by :
[Mark Drake](https://www.digitalocean.com/community/users/mdrake)

<h3>Many thanks to all contributors from the Python community.</h3>

## Author

**Paul Girmes** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

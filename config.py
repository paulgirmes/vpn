class Config():
    RSA = [
        'set_var EASYRSA_REQ_COUNTRY "US"',
        'set_var EASYRSA_REQ_PROVINCE "NewYork"',
        'set_var EASYRSA_REQ_CITY "New York City"',
        'set_var EASYRSA_REQ_ORG "DigitalOcean"',
        'set_var EASYRSA_REQ_EMAIL "admin@example.com"',
        'set_var EASYRSA_REQ_OU "Community"',
    ]
    VPN = [
        "port 1194",
        "proto udp",
        "dev tun",
        "ca ca.crt",
        "cert server.crt",
        "key server.key",
        "server 10.8.0.0 255.255.255.0",
        "ifconfig-pool-persist /var/log/openvpn/ipp.txt",
        "keepalive 10 120",
        "tls-auth ta.key 0",
        "cipher AES-256-CBC",
        "user nobody",
        "group nogroup",
        "persist-key",
        "persist-tun",
        "status /var/log/openvpn/openvpn-status.log",
        "verb",
        "explicit-exit-notify 1",
    ]

#!/usr/bin/python3
"""
install and configure an vpn server + server certs/CA, enables it at startup
on a new install of Ubuntu server, use [[ sudo python ./vpn.py ]]
after having copied all the files in the server admin local home
prerequisites : python3.x, shell
"""
import os
import subprocess
import logging

from config import Config
from shell import Shell, CommandError


# logger conf
logging.basicConfig(format="%(message)s", level=logging.DEBUG)
# setting the path of this file execution for future reference
exec_path = os.path.abspath(os.path.dirname(__file__))


def command(list):
    """
    execute an os command,
    take a list of strings ex :
    ["sudo", "cp", "/etc/systemctl.conf", "/home/administrateur/system.conf"]
    returns [0, standard output] if OK
    raises an exception if either the cmd fails or if it exeeds 20sec to finish
    """
    try:
        a = subprocess.run(
            list,
            check=True,
            capture_output=True,
            timeout=100,
        )
        return [0, str(a.stdout)]
    except subprocess.CalledProcessError as e:
        raise e
    except subprocess.TimeoutExpired as e:
        raise e


def open_vpn_install():
    logging.info("Installing OpenVPN")
    try:
        install_result = subprocess.run(
            ["sudo", "apt", "install", "openvpn", "-y"],
            check=True, capture_output=True, timeout=300
        )
        return [0, install_result]
    except subprocess.CalledProcessError as e:
        return [1, str(e)]
    except subprocess.TimeoutExpired as e:
        return [1, str(e)]


def certificates_gen():
    logging.info("Downloading/extracting EasyRsa")
    cmd_list = [
        [
            "wget",
            "https://github.com/OpenVPN/easy-rsa/releases"
            + "/download/v3.0.8/EasyRSA-3.0.8.tgz",
        ],
        ["tar", "xvf", "EasyRSA-3.0.8.tgz"],
        ["cp", "EasyRSA-3.0.8/vars.example", "EasyRSA-3.0.8/vars"],
    ]
    [command(cmd) for cmd in cmd_list]
    # writing vars config file for easy rsa
    with open(exec_path + "/EasyRSA-3.0.8/vars", "a") as f:
        [f.write("\n" + option) for option in Config.RSA]
    logging.info("initialising Easy RSA")
    if not os.path.exists(exec_path + "/pki"):
        command(["EasyRSA-3.0.8/./easyrsa", "init-pki"])
    # buiding CA certificate
    if not os.path.exists(exec_path + "/pki/ca.crt"):
        try:
            build_ca = Shell(has_input=True)
            build_ca.run("EasyRSA-3.0.8/./easyrsa build-ca nopass")
            build_ca.write("\n")
            logging.info("CA certificate generated")
        except CommandError as e:
            return [1, str(e)]
    # generating server certificate request + signing
    if not os.path.exists(exec_path + "/pki/reqs/server.req"):
        try:
            serv_certificate = Shell(has_input=True)
            serv_certificate.run(
                "EasyRSA-3.0.8/./easyrsa gen-req server nopass")
            serv_certificate.write("\n")
            logging.info("request for server cert generated")
        except CommandError as e:
            return [1, str(e)]
        try:
            sign_serv_cert = Shell(has_input=True)
            sign_serv_cert.run(
                "EasyRSA-3.0.8/./easyrsa sign-req server server")
            sign_serv_cert.write("yes\n")
            logging.info("server cert signed")
        except CommandError as e:
            return [1, str(e)]
    # generating Diffie Hellman Key + HMAC signature
    if not os.path.exists(exec_path + "/pki/dh.pem"):
        command(["sudo", exec_path + "/EasyRSA-3.0.8/./easyrsa", "gen-dh"])
    if not os.path.exists(exec_path + "/ta.key"):
        command(["openvpn", "--genkey", "--secret", "ta.key"]),
    # moving the certs/keys into the openvpn dir
    cmd_list2 = [
        ["sudo", "cp", exec_path + "/pki/private/server.key", "/etc/openvpn/"],
        ["sudo", "cp", exec_path + "/pki/issued/server.crt", "/etc/openvpn"],
        ["sudo", "cp", exec_path + "/pki/ca.crt", "/etc/openvpn"],
        ["sudo", "cp", exec_path + "/ta.key", "/etc/openvpn/"],
        ["sudo", "cp", exec_path + "/pki/dh.pem", "/etc/openvpn/"],
    ]
    [command(cmd) for cmd in cmd_list2]
    return [0, "changed"]


def open_vpn_config():
    # create conf file for Ovpn moving the old one if needed
    if not os.path.exists("/etc/openvpn/server.conf"):
        with open("/etc/openvpn/server.conf", "w") as f:
            [f.write(option + "\n") for option in Config.VPN]
    else:
        command(["sudo", "cp", "/etc/openvpn/server.conf",
                "/etc/openvpn/server.conf.old"])
        logging.info("server.conf file moved to server.conf.old")
        with open("/etc/openvpn/server.conf", "w") as f:
            [f.write(option + "\n") for option in Config.VPN]
    # adding ipv4 routing to sysctl.con
    command(["sudo", "cp", "/etc/sysctl.conf",
            "/etc/sysctl.conf.old"])
    logging.info("/etc/sysctl.conf file moved to /etc/sysctl.conf.old")
    with open("/etc/sysctl.conf", "r") as f:
        lines = f.readlines()
        done = False
        for line in lines:
            if line.strip() == "net.ipv4.ip_forward=1":
                done = True
    if not done:
        with open("/etc/sysctl.conf", "a") as f:
            f.write("net.ipv4.ip_forward=1\n")
    # configuring NAT + UFW / starting and enabling ovpn at next startup
    command(["sudo", "cp", "/etc/ufw/before.rules",
            "/etc/ufw/before.rules.old"])
    logging.info(
        "/etc/ufw/before.rules file moved to /etc/ufw/before.rules.old")
    with open("/etc/ufw/before.rules", "r") as old:
        saved_file_data = old.read()
        with open("/etc/ufw/before.rules", "w") as new:
            [new.write(option + "\n") for option in Config.UFW_BEFORE]
            new.write(saved_file_data)
    cmd_list = [
        ["sudo", "ufw", "default", "allow", "routed"],
        ["sudo", "ufw", "allow", "1194/udp"],
        ["sudo", "ufw", "allow", "22/tcp"],
        ["sudo", "systemctl", "start", "openvpn@server"],
        ["sudo", "systemctl", "enable", "openvpn@server"],
    ]
    [command(cmd) for cmd in cmd_list]
    return [0, "changed"]


def clients_config_gen(name="client"):
    cmd_list = [
        ["mkdir", "-p", exec_path + "/client-config/keys"],
    ]
    [command(cmd) for cmd in cmd_list]
# generating server certificate request + signing
    if not os.path.exists(exec_path + "/pki/reqs/{}.req".format(name)):
        try:
            serv_certificate = Shell(has_input=True)
            serv_certificate.run(
                "EasyRSA-3.0.8/./easyrsa gen-req {} nopass".format(name))
            serv_certificate.write("\n")
            logging.info("request for {} cert generated".format(name))
        except CommandError as e:
            return [1, str(e)]
        try:
            sign_serv_cert = Shell(has_input=True)
            sign_serv_cert.run(
                "EasyRSA-3.0.8/./easyrsa sign-req client {}".format(name))
            sign_serv_cert.write("yes\n")
            logging.info("{} cert signed".format(name))
        except CommandError as e:
            return [1, str(e)]
    # copying files + creating client config template file
    cmd_list = [
        ["sudo", "cp", exec_path + "/pki/private/{}.key".format(name), exec_path + "/client-config/keys/"],
        ["cp", exec_path + "/pki/issued/client1.crt", exec_path + "/client-config/keys/"],
        ["cp", exec_path + "/ta.key", exec_path + "/client-config/keys/"],
        ["cp", exec_path + "/pki/ca.crt", exec_path + "/client-config/keys/"],
        ["mkdir", "-p", exec_path + "/client-config/files"],
    ]
    [command(cmd) for cmd in cmd_list]
    with open(exec_path + "/client-config/files/{}.conf".format(name), "w") as f:
        [f.write(option + "\n") for option in Config.VPN_CLIENT]
    with open(exec_path + "/client-config/files/{}.conf".format(name), "a") as conf_file:
        with open(exec_path + "/client-config/keys/ca.crt", "r") as ca_cert:
            ca = ca_cert.read()
            conf_file.write("<ca>\n")
            conf_file.write(ca)
            conf_file.write("</ca>\n")
        with open(exec_path + "/client-config/keys/{}.crt".format(name), "r") as client_cert:
            cc = client_cert.read()
            conf_file.write("<cert>\n")
            conf_file.write(cc)
            conf_file.write("</cert>\n")
        with open(exec_path + "/client-config/keys/{}.key".format(name), "r") as client_key:
            ck = client_key.read()
            conf_file.write("<key>\n")
            conf_file.write(ck)
            conf_file.write("</key>\n")
        with open(exec_path + "/client-config/keys/ta.key", "r") as ta_key:
            ta = ta_key.read()
            conf_file.write("<tls-auth>\n")
            conf_file.write(ta)
            conf_file.write("</tls-auth>\n")


def main():
    ovpn_install = open_vpn_install()
    if ovpn_install[0] == 0:
        logging.info("VPN properly installed")
    else:
        logging.info("VPN not installed")
        return 1
    certificates = certificates_gen()
    if certificates[0] == 0:
        logging.info("server certificates properly installed")
    else:
        logging.info("VPN not installed")
        return 1
    ovpn_conf = open_vpn_config()
    if ovpn_conf[0] == 0:
        logging.info("VPN properly configured")
    else:
        logging.info("VPN not configured")
        return 1
    i = 1
    for client in Config.CLIENTS_IP:
        clients_config_gen(name="client{}".format(i))
        i += 1


if __name__ == "__main__":
    main()

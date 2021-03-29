#!/usr/bin/python3
"""
"""
import platform
import os
import traceback
import shutil
import tempfile
from subprocess import Popen, PIPE
import subprocess
import logging
from config import Config
from shell import Shell, CommandError

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

exec_path = os.path.abspath(os.path.dirname(__file__))


def command(list):
    try:
        subprocess.run(
            list,
            check=True,
            capture_output=True,
            timeout=10,
        )
        return 0
    except subprocess.CalledProcessError as e:
        raise e
    except subprocess.TimeoutExpired as e:
        raise e


def open_vpn_install():
    logging.info("Installing OpenVPN")
    try:
        install_result = subprocess.run(
            ["apt", "install", "openvpn"], check=True, capture_output=True, timeout=300
        )
        if b"already" in install_result.stdout.split():
            return [0, True]
    except subprocess.CalledProcessError as e:
        return [1, str(e)]
    except subprocess.TimeoutExpired as e:
        return [1, str(e)]


def certificates_gen():
    logging.info("Downloading/extracting EasyRsa")
    cmd_list = [
        [
            "wget",
            "-P",
            "~/",
            "https://github.com/OpenVPN/easy-rsa/releases"
            + "/download/v3.0.8/EasyRSA-3.0.8.tgz",
        ],
        ["tar", "xvf", "EasyRSA-3.0.8.tgz"],
        ["cp", "EasyRSA-3.0.8/vars.example", "EasyRSA-3.0.8/vars"],
    ]
    [command(cmd) for cmd in cmd_list]
    with open(exec_path + "/EasyRSA-3.0.8/vars", "a") as f:
        (f.write("\n" + option) for option in Config.RSA)
    logging.info("initialising Easy RSA")
    if not os.path.exists(exec_path + "/pki"):
        command(["EasyRSA-3.0.8/./easyrsa", "init-pki"])
    if not os.path.exists(exec_path + "/pki/ca.crt"):
        try:
            build_ca = Shell(has_input=True)
            build_ca.run("EasyRSA-3.0.8/./easyrsa build-ca nopass")
            build_ca.write("\n")
            logging.info("CA certificate generated")
        except CommandError as e:
            return [1, str(e)]
    if not os.path.exists(exec_path + "/pki/reqs/server.req"):
        try:
            serv_certificate = Shell(has_input=True)
            serv_certificate.run("EasyRSA-3.0.8/./easyrsa gen-req server nopass")
            serv_certificate.write("yes\n")
            logging.info("request for server cert generated")
        except CommandError as e:
            return [1, str(e)]
        try:
            sign_serv_cert = Shell(has_input=True)
            sign_serv_cert.run("EasyRSA-3.0.8/./easyrsa sign-req server server")
            sign_serv_cert.write("yes\n")
            logging.info("server cert signed")
        except CommandError as e:
            return [1, str(e)]
    if not os.path.exists(exec_path + "/pki/dh.pem"):
        command(["EasyRSA-3.0.8/./easyrsa", "gen-dh"])
    if not os.path.exists(exec_path + "/ta.key"):
        command(["openvpn", "--genkey", "--secret", "ta.key"]),
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
    # create conf file and parses options
    cmd_list = [
        ["sudo", "cp", "/usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz", "/etc/openvpn/server.conf.gz"],
        ["sudo", "gzip", "-d", "/etc/openvpn/server.conf.gz"],
    ]
    [command(cmd) for cmd in cmd_list]
    return [0, "changed"]


def main():
    ovpn_install = open_vpn_install()
    if ovpn_install[0] == 0:
        logging.info("VPN properly installed")
    else:
        logging.info("VPN not installed : {}".format(str(ovpn_install[1])))
    certificates = certificates_gen()
    if certificates[0] == 0:
        logging.info("server certificates properly installed")
    else:
        logging.info("VPN not installed : {}".format(str(certificates[1])))
    ovpn_conf = open_vpn_config()
    if ovpn_conf[0] == 0:
        logging.info("VPN properly configured")
    else:
        logging.info("VPN not configured : {}".format(str(certificates[1])))


if __name__ == "__main__":
    main()

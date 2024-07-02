import socket

from portobello.internal.utils import ask_for_input_or_list_choice


def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((host, port))
            return True
        except (socket.timeout, socket.error):
            return False


def main(cli_strings: list, portobello_config: dict):
    saved_hostnames = portobello_config['netstat']['hostnames']
    hostname, return_clargs = ask_for_input_or_list_choice(saved_hostnames, 'hostname', 'hostnames', cli_strings=cli_strings)

    if len(cli_strings) >= 2:
        port_number = int(cli_strings[1])
    else:
        port_number = int(input('Please enter a port number to check:\n'))

    print(f"####\nThe port you checked is{[' not', ''][check_port(hostname, port_number)]} open.\n####\n")
    return return_clargs + [str(port_number)]

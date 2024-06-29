import socket


def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((host, port))
            return True
        except (socket.timeout, socket.error):
            return False


def main(cli_strings: list, portobello_config: dict):
    newline = '\n'
    saved_hostnames = portobello_config['netstat']['hostnames']
    if len(cli_strings) >= 1:
        hostname = cli_strings[0]
    else:
        if saved_hostnames:
            saved_hostname_strings = [f"[{index}]: {hostname}" for index, hostname in enumerate(saved_hostnames)]
            print(f"Saved hostnames are: \n{newline.join(saved_hostname_strings)}\n\n"
                  "To choose one of these, start with a # and type its reference number.")
        hostname = input('Please enter a hostname:')
    if hostname[0] == '#':
        ind = int(hostname[1:])
        if not ind < len(saved_hostnames):
            raise IndexError("You're attempting to use a saved hostname that does not exist.")
        hostname = saved_hostnames[ind]
    else:
        if input('Do you want to save this hostname for the future? Type y for yes.') == 'y':
            portobello_config['netstat']['hostnames'].append(hostname)

    if len(cli_strings) >= 2:
        port_number = int(cli_strings[1])
    else:
        port_number = int(input('Please enter a port number to check.'))

    print(f"####\nThe port you checked is{[' not', ''][check_port(hostname, port_number)]} open.\n####\n")
    return [hostname, str(port_number)]

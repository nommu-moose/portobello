import os
import psutil


def ldap():
    pass


def netstat():
    pass


def cli_help():
    pass


def edit_config():
    pass


def main():
    """
    if keepass not in config, ask for keepass path to be entered
    give list of ldap, netstat, help, or config
    :return:
    """
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    command_line = ' '.join(current_process.cmdline())
    print("Full command-line invocation string:")
    print(command_line)


main()

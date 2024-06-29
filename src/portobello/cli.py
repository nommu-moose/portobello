import os
import psutil

from portobello.internal.utils import split_quoted_string, load_portobello_config, save_portobello_config, edit_config
from portobello.netstat.main import main as netstat_main


def ldap(cli_strings):
    pass


def cli_help(cli_strings):
    pass


def main():
    """
    if keepass not in config, ask for keepass path to be entered
    give list of ldap, netstat, help, or config
    :return:
    """
    portobello_config = load_portobello_config()
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    cli_string = ' '.join(current_process.cmdline())
    print(cli_string)
    cli_strings = split_quoted_string(cli_string)[2:]
    if not cli_strings:
        question_text = "Would you like to use: \nldap\nnetstat\nns (short name for netstat)\nhelp\nconfig (edit)"
        cli_strings = [input(question_text)]
    {
        'ldap': ldap,
        'netstat': netstat_main,
        'ns': netstat_main,
        'help': cli_help,
        'config': edit_config
    }[cli_strings[0]](cli_strings[1:], portobello_config)

    save_portobello_config(portobello_config)

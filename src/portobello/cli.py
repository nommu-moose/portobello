import os
import psutil

from portobello.internal.utils import split_quoted_string, load_portobello_config, save_portobello_config, edit_config
from portobello.netstat.main import main as netstat_main
from portobello.ldap.main import main as ldap_main


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
        question_text = "Would you like to use: \nldap\nnetstat\nns (short name for netstat)\nhelp\nconfig (edit)\n"
        cli_strings = [input(question_text)]
    listed_clargs = {
        'ldap': ldap_main,
        'netstat': netstat_main,
        'ns': netstat_main,
        'help': cli_help,
        'config': edit_config
    }[cli_strings[0]](cli_strings[1:], portobello_config)

    saveable_clarg_str = f"{' '.join(['pbo', cli_strings[0]] +
                                     [f'"{arg}"' if ' ' in arg else arg for arg in listed_clargs])}"

    print(f"The complete command line for future reuse is: \n{saveable_clarg_str}")
    if saveable_clarg_str not in portobello_config['saved_commands'] and \
            input("Do you want to save this command line for future use? y for yes:\n"):
        portobello_config['saved_commands'].append(saveable_clarg_str)

    save_portobello_config(portobello_config)

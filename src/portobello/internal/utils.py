import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from pykeepass import PyKeePass
import platform


class PlatformError(Exception):
    def __init__(self):
        super().__init__('You are on an unsupported platform for portobello.')


class UninitialisedError(Exception):
    def __init__(self, filepath):
        txt = f"""
        \n\n\n\n
        You have not used portobello before on this system, or the data for your user is empty.
        Please initialise this package's behaviour by filling in information into the following json file:
         \n{filepath}.\n\n\n\n'
        """
        super().__init__(txt)


class JsonLoadError(Exception):
    pass


class JsonSaveError(Exception):
    pass


def save_portobello_config(config):
    save_json(PORTOBELLO_CONFIG_PATH, config)
    save_backup(config, Path(PORTOBELLO_CONFIG_PATH.parent, 'backups'), 25)


def save_backup(json_data, directory_path, n):
    if not directory_path.exists():
        directory_path.mkdir(exist_ok=True, parents=True)
    pattern = re.compile(r'^\d{12}_config_backup\.json$')

    matched_files = []

    for filename in os.listdir(directory_path):
        if pattern.match(filename):
            matched_files.append(filename)

    if len(matched_files) > n:
        matched_files.sort()

        oldest_file = matched_files[0]

        os.remove(os.path.join(directory_path, oldest_file))
        # for later logging print(f"Deleted the oldest backup file: {oldest_file}")

    backup_path_now = Path(directory_path, f"{datetime.now().strftime('%y%m%d%H%M%S')}_config_backup.json")
    save_json(backup_path_now, json_data)


def pw_from_keepass(search_string: str, fp: Path = None, pw: str = None):
    kp = PyKeePass(fp, password=pw)
    return kp.find_entries(title=search_string, first=True).password


def load_portobello_config():
    template_config = load_template_config()
    config = standardise_portobello_config(template_config)
    return config


def load_template_config():
    template_config_fp = Path(Path(__file__).parent, 'template_config.json')
    template_config = load_json(template_config_fp)
    return template_config


def load_json(path, raise_exception=True):
    try:
        with open(path, 'r') as json_file:
            json_data = json.load(json_file)
    except IOError as e:
        error_txt = f"An error occurred whilst trying to read the template config for portobello: {e}"
        if raise_exception:
            raise JsonLoadError(error_txt)
        else:
            print(error_txt)
            return {}
    return json_data


def save_json(path, json_data, raise_exception=True):
    try:
        with open(path, 'w') as json_file:
            json.dump(json_data, json_file, indent=2)
        # for later logging print(f"Configuration saved successfully to {path}")
    except IOError as e:
        error_txt = f"An error occurred while writing to the file: {e}"
        if raise_exception:
            raise JsonSaveError(error_txt)
        else:
            print(error_txt)


def standardise_portobello_config(template_config):
    if not PORTOBELLO_CONFIG_PATH.exists():
        PORTOBELLO_CONFIG_PATH.parent.mkdir(exist_ok=True, parents=True)
        portobello_config = {}
    else:
        portobello_config = load_json(PORTOBELLO_CONFIG_PATH)
    standardised_portobello_config = combine_config_fields(portobello_config, template_config)
    save_json(PORTOBELLO_CONFIG_PATH, standardised_portobello_config)
    return standardised_portobello_config


def combine_config_fields(target_dict: dict, addition_dict: dict) -> dict:
    """
    Recursively merges addition_dict into target_dict following the specified rules:
    1. If it's an element of a list, the addition_dict data (and anything deeper) is only added to target_dict
       if the target_dict's data is empty.
    2. If it's an item in a dict, the addition_dict data is added if that field doesn't exist at all in the target_dict.

    :param target_dict: The dictionary to which data is to be added.
    :param addition_dict: The dictionary from which data is to be added.
    :return: The combined dictionary.
    """
    if not isinstance(target_dict, dict) or not isinstance(addition_dict, dict):
        return target_dict

    for key, value in addition_dict.items():
        if key not in target_dict:
            target_dict[key] = value
        else:
            # Key exists in target_dict, need to merge based on type
            if isinstance(value, dict) and isinstance(target_dict[key], dict):
                # Both are dictionaries, merge recursively
                combine_config_fields(target_dict[key], value)
            elif isinstance(value, list) and isinstance(target_dict[key], list):
                # Both are lists, add only if target_dict's list is empty
                if not target_dict[key]:
                    target_dict[key] = value
            else:
                # For other types, don't override existing target_dict values
                pass

    return target_dict


def get_portobello_data_path():
    os_type = platform.system()
    return {
        'Windows': windows_get_local_appdata_path,
        'Linux': linux_get_data_dir,
    }.get(os_type, PlatformError)()


def windows_get_local_appdata_path():
    return Path(os.getenv('LOCALAPPDATA'), 'portobello')


def linux_get_data_dir():
    return Path(os.getenv('XDG_DATA_HOME', Path('~/.local/share/portobello/').expanduser()))


def manual_debug_log(*args, **kwargs):
    log_name = kwargs.get('log_name', 'default_log') + '.txt'
    log_path = Path(get_portobello_data_path(), 'logs', log_name)
    del kwargs['log_name']

    txt = f'[{str(datetime.now().replace(second=0, microsecond=0))}]: '

    for ele in args:
        txt += str(ele) + ',  '
    for key in kwargs:
        txt += f"{key}: {str(kwargs[key])}" + ',  '
    if args or kwargs:
        txt = txt[:-3]
    txt += "\n"
    with open(log_path, 'a') as file:
        file.write(txt)


###################
# Config  Editing #
###################


def edit_config(_, portobello_config):
    open_editor(PORTOBELLO_CONFIG_PATH)


def get_default_editor():
    """
    Determine the default text editor to use based.
    """
    if platform.system() == 'Windows':
        return 'notepad'
    else:
        for editor in ['nano', 'vim', 'vi']:
            if subprocess.call(['which', editor], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                return editor
        raise EnvironmentError("No suitable text editor found on this system.")


def open_editor(file_path):
    """
    Open the default text editor with the file provided.
    """
    editor = get_default_editor()

    subprocess.call([editor, file_path])

    return []


###################
#  Command  Line  #
###################


def split_quoted_string(input_string):
    """
    Splits the input string by spaces, but preserves substrings within quotes.

    :param input_string: The string to be split.
    :return: A list of substrings.
    """
    # Regex to match substrings within quotes or individual words
    regex = r'\"(.*?)\"|\'(.*?)\'|(\S+)'

    # Find all matches using the regex
    matches = re.findall(regex, input_string)

    # Extract the captured groups from the matches
    result = []
    for match in matches:
        # Match is a tuple of 3 elements, one of which will be non-empty
        result.append(next(item for item in match if item))

    return result


PORTOBELLO_CONFIG_PATH = Path(get_portobello_data_path(), 'conf.json')

import re
from pathlib import Path

from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, NTLM

from portobello.internal.utils import manual_debug_log, pw_from_keepass, ask_for_input_or_list_choice, \
    ImproperSelectionError
from getpass import getpass


def main(cli_strings, portobello_config):
    saved_bind_users = portobello_config['ldap']['bind_users']
    bind_user, return_clargs = ask_for_input_or_list_choice(saved_bind_users, 'bind user',
                                                            'bind users', cli_strings=cli_strings)
    if type(bind_user) is str:
        bind_user = {'bind_user': bind_user}

    pw = get_bind_user_password(cli_strings, bind_user, portobello_config)

    server_uri, clargs = ask_for_input_or_list_choice([], 'server uri', 'server uris',
                                                      cli_strings=cli_strings, cli_ind=2)
    return_clargs += clargs
    conn = ldap_connect(server_uri, bind_user, pw)
    print(f"Connection has{[' not', ''][bool(conn.bind())]} bound successfully. ")

    if cli_strings >= 4:
        user_input = cli_strings[3]
    else:
        user_input = input("Do you want to conduct an ldap search? y or n:\n")
    if user_input == 'y':
        return_clargs += ['y']

    else:
        return_clargs += ['n']

    return_clargs = ldap_search(conn, portobello_config, cli_strings)

    return return_clargs


def get_bind_user_password(cli_strings, bind_user, portobello_config):
    if len(cli_strings) >= 2:
        user_input = cli_strings[1]
    else:
        user_input = input("Type 'k' if you want to use the keepass, p for directly supplying password:\n")
    if user_input == 'k':
        kp_password = getpass("Please enter the keepass password:\n")
        kp_search_string = bind_user.get('kp_search_string', input("Please enter users keepass search string:\n"))
        bind_user['kp_search_string'] = kp_search_string
        pw = pw_from_keepass(bind_user['kp_search_string'], Path(portobello_config['keepass_location']), kp_password)
    elif user_input == 'p':
        pw = getpass("Please enter the bind user password:\n")
    else:
        raise ImproperSelectionError("Please only type k or p.")
    return pw


def str_from_obj(obj, attr_lst):
    output_separator_list = {'short': [', ', '\n'], 'long': ['\n', '\n\n\n']}
    output_separators = output_separator_list['long']
    if 'all' in attr_lst:
        return str(obj)
    txt = ''
    for attr in attr_lst:
        if hasattr(obj, attr):
            txt += f"{attr}:{str(getattr(obj, attr))}" + output_separators[0]
    if txt != '':
        txt = txt[:-len(output_separators[0])] + output_separators[1]
    return txt


def expand_out_args(args, keys):
    for key in keys:
        lst = []
        attr = getattr(args, key)
        if attr is not None:
            for ele in attr:
                if type(ele) is list:
                    lst += ele
                else:
                    lst.append(ele)
        setattr(args, key, lst)


def ldap_connect(uri, bind_user, bind_pw):
    bind_dn = bind_user['bind_user']
    server = Server(uri, get_info=ALL, allowed_referral_hosts=[('*', True)])
    conn = Connection(
        server,
        bind_dn,
        bind_pw,
        authentication=NTLM,
        auto_referrals=True,
        auto_encode=True,
        auto_escape=True
    )
    return conn


def ldap_search(conn, portobello_config, cli_strings, attr_list='all'):
    return_clargs = []
    saved_dcs = portobello_config['ldap']['domain_components']
    domain_components, clargs = ask_for_input_or_list_choice(saved_dcs, 'bind user', 'bind users',
                                                             cli_strings=cli_strings, cli_ind=4)
    return_clargs += clargs
    saved_queries = portobello_config['ldap']['queries']
    search_query, clargs = ask_for_input_or_list_choice(saved_queries, 'bind user', 'bind users',
                                                        cli_strings=cli_strings, cli_ind=5)
    return_clargs += clargs

    conn.search(
        domain_components,
        search_query,
        search_scope='SUBTREE',
        attributes=ALL_ATTRIBUTES
    )
    output_txt = ''
    log_name = domain_components + re.sub('[&()]', '', search_query)
    for entry in conn.entries:
        user_txt = str_from_obj(entry, attr_list)
        output_txt += user_txt
        manual_debug_log(user=user_txt, log_name=log_name, log_path=['ldap', 'output'])


def check_ldap_membership():
    pass

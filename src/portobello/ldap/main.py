import re
from pathlib import Path

from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, NTLM

from portobello.internal.utils import manual_debug_log, pw_from_keepass, ask_for_input_or_list_choice, \
    ImproperSelectionError
from getpass import getpass


def main(cli_strings, portobello_config):
    saved_bind_users = portobello_config['ldap']['bind_users']
    bind_user = ask_for_input_or_list_choice(saved_bind_users, 'bind user', 'bind users', cli_strings=cli_strings)
    if type(bind_user) is str:
        bind_user = {'bind_user': bind_user}

    pw = get_bind_user_password(cli_strings, bind_user, portobello_config)

    server_uri = input("Please input the server uri:\n")
    conn = ldap_connect(server_uri, bind_user, pw)
    print(f"Connection has{[' not', ''][bool(conn.bind())]} bound successfully. ")
    return []


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


def ldap_search(conn, domain_components, search_query, attr_list):
    conn.search(
        domain_components,
        search_query,
        search_scope='SUBTREE',
        attributes=ALL_ATTRIBUTES
    )
    output_txt = ''
    log_name = re.sub('[&()]', '', search_query)
    for entry in conn.entries:
        user_txt = str_from_obj(entry, attr_list)
        output_txt += user_txt
        manual_debug_log(user=user_txt, log_name=log_name, log_path=['ldap', 'output'])


def ldap_authenticate():
    pass


def check_ldap_membership():
    pass


def retrieve_ldap_attributes():
    pass

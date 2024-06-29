import re
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, NTLM

from portobello.internal.utils import manual_debug_log
from getpass import getpass


def main(cli_strings, portobello_config):
    print(f"If your bind user is listed here, please use its reference number:")

    newline = '\n'
    saved_bind_users = portobello_config['ldap']['bind_users']
    saved_bind_user_strings = [f"[{index}]: {bind_user}" for index, bind_user in enumerate(saved_bind_users)]
    print(f"Saved bind users are: \n{newline.join(saved_bind_user_strings)}\n\n"
          "To choose one of these, start with a # and type its reference number.")
    bind_user = input(f"Please enter a bind_user:\n")
    if bind_user[0] == '#':
        ind = int(bind_user[1:])
        bind_user = saved_bind_users[ind]
    else:
        bind_user = {'bind_user': bind_user, 'kp_search_string': input("Please enter users keepass search string:\n")}
    password = getpass("Please enter the keepass password:\n")
    bind_user['password'] = password
    server_uri = input("Please input the server uri:\n")
    conn = ldap_connect(server_uri, bind_user)
    print("Connection has bound?: ", bool(conn.bind()))


def deliver_request_for_entry(var_name, readable_name, portobello_config):
    # if portobello_config['ldap'][var_name]
    # input(f"Please enter ")
    pass


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


def ldap_connect(uri, bind_user):
    bind_dn = bind_user['bind_user']
    bind_pw = bind_user['password']
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

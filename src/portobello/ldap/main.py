import re
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES

from portobello.internal.utils import manual_debug_log


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


def ldap_connect(uri, bind_dn, bind_pw):
    server = Server(uri, get_info=ALL, allowed_referral_hosts=[('*', True)])
    conn = Connection(
        server,
        bind_dn,
        bind_pw,
        auto_bind='DEFAULT',
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


def retrieve_ldap_attribute():
    pass

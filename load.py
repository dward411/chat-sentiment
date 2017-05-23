#!/usr/bin/env python
import pandas as pd
import re
from HTMLParser import HTMLParser
import random
import os
import errno


def create_dirs(relative_path):
    print("Creating directories '{0}'...".format(relative_path))
    try:
        os.makedirs(relative_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def load_messages(relative_path):
    print("Loading '{0}'...".format(relative_path))
    return pd.read_excel(relative_path)


def remove_operator_chats(df):
    print('Removing operator chats...')
    df['isLibrarian'] = df.apply(lambda row: 1 if row['toRecipient'] == "LIBRARIAN" else 0, axis=1)
    df['messageCount'] = df.groupby('conversationID')['conversationID'].transform('count')
    df['libMessageCount'] = df.groupby('conversationID')['isLibrarian'].transform('sum')
    df = df[df['libMessageCount'] != df['messageCount']]
    df = df.drop('isLibrarian', 1)
    df = df.drop('messageCount', 1)
    df = df.drop('libMessageCount', 1)
    return df


def remove_short_chats(df):
    print('Removing short chats...')
    df['messageCount'] = df.groupby('conversationID')['conversationID'].transform('count')
    df = df[df['messageCount'] > 6]
    df = df.drop('messageCount', 1)
    return df


def get_link_pattern_one():
    link_p = "<a[\S\s]*?<\/a>"
    return link_p


def get_link_pattern_two():
    link_p = ("bhttp://[^s]+")
    return link_p


def replace_links(link_pattern, df):
    print('Replacing Links...')
    df['body'].replace({link_pattern: 'LINK_REPLACE'}, regex=True, inplace=True)
    return df


def replace_emails(df):
    print('Replacing E-Mails...')
    email_p = (
        "(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*"
        "|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")"
        "@LINK_REPLACE"
    )
    df['body'].replace({email_p: 'EMAIL_ADDRESS'}, regex=True, inplace=True)
    return df


def save_messages(df, relative_path):
    print("Saving messages to '{0}'...".format(relative_path))
    with pd.ExcelWriter(relative_path) as writer:
        df.to_excel(writer, sheet_name='sheet1', engine='xlsxwriter')


def is_not_only_a_link(row):
    return bool(row.replace("LINK_REPLACE", "").replace("EMAIL_ADDRESS", "").strip())


def remove_link_messages(df):
    print('Removing link-messages...')
    mask = df['body'].apply(is_not_only_a_link)
    df = df[mask]
    return df


def decode_html_entities(df):
    print('Decoding HTML entities...')
    h = HTMLParser()
    df['body'] = df['body'].apply(lambda row: h.unescape(row))
    return df


def load_canned_msgs(relative_path):
    cms = set()
    raw_canned_msgs = load_messages(relative_path)
    for index, row in raw_canned_msgs.iterrows():
        cms.add(row['cannedMessage'].strip())
    return cms


def is_canned_msg(row, cms):
    return row['toRecipient'] == "LIBRARIAN" and row['body'].strip() in cms


def remove_canned_msgs(df, relative_path):
    print('Removing canned messages...')
    canned_msgs = load_canned_msgs(relative_path)
    mask = df.apply(lambda row: not is_canned_msg(row, canned_msgs), axis=1)
    df = df[mask]
    return df


def random_sample(df, sample_size):
    print('Getting utterances sample...')
    mask = random.sample(set(df.index), sample_size)
    df = df.loc[mask]
    return df


def regex_search(re_exp, s, neg=False):
    found = bool(re.search(re_exp, s, re.IGNORECASE))
    if neg:
        found = not found
    return found


def load_blacklist(relative_path):
    print('Loading blacklist...')
    bl = []
    raw_blacklist = load_messages(relative_path)
    for index, row in raw_blacklist.iterrows():
        bl.append(row['blackListed'].strip())
    return bl


def is_blacklisted(body, blacklist):
    for blacklisted in blacklist:
        if regex_search(blacklisted, body):
            return True
    return False


def remove_blacklisted(df):
    print('Removing blacklisted messages...')
    loaded_blacklist = load_blacklist('data/lookup/blacklist.xlsx')
    mask = df['body'].apply(lambda row: not is_blacklisted(row, loaded_blacklist))
    df = df[mask]
    return df


def create_search_mask(re_exp, df, neg=False):
    return df['body'].apply(lambda row: regex_search(re_exp, row, neg))


def short_print(df):
    print(df.head()[['ID', 'conversationID', 'body']])


def remove_librarians(df):
    print('Removing librarian messages...')
    mask = df.apply(lambda row: not row['toRecipient'] == "LIBRARIAN", axis=1)
    df = df[mask]
    return df


def random_sample_split(df, sample_size):
    print('Getting utterances sample with 50/50 composition...')
    half_size = sample_size / 2
    librarian_mask = df['toRecipient'].apply(lambda row: row == "LIBRARIAN")
    librarian_idxs = random.sample(set(df[librarian_mask].index), half_size)
    patron_mask = df['toRecipient'].apply(lambda row: row != "LIBRARIAN")
    patron_idxs = random.sample(set(df[patron_mask].index), half_size)
    sample_idxs = list(set().union(librarian_idxs, patron_idxs))
    df = df.loc[sample_idxs]
    return df


if __name__ == '__main__':
    messages = load_messages('data/raw/chats.xlsx')
    create_dirs('data/processed')

    messages = remove_operator_chats(messages)
    save_messages(messages, 'data/processed/1_chats_without_operators.xlsx')

    messages = remove_short_chats(messages)
    save_messages(messages, 'data/processed/2_long_chats.xlsx')

    messages = decode_html_entities(messages)
    save_messages(messages, 'data/processed/3_unescaped.xlsx')

    messages = remove_canned_msgs(messages, 'data/lookup/canned_msgs.xlsx')
    save_messages(messages, 'data/processed/4_without_canned.xlsx')

    messages = replace_links(get_link_pattern_one(), messages)
    save_messages(messages, 'data/processed/5_replaced_type1_links.xlsx')

    messages = replace_links(get_link_pattern_two(), messages)
    save_messages(messages, 'data/processed/6_replaced_type2_links.xlsx')

    messages = replace_emails(messages)
    save_messages(messages, 'data/processed/7_labeled_emails.xlsx')

    messages = remove_link_messages(messages)
    save_messages(messages, 'data/processed/8_removed_link_msgs.xlsx')

    messages = remove_blacklisted(messages)
    save_messages(messages, 'data/processed/9_removed_blacklisted.xlsx')

    messages = random_sample_split(messages, 2700)
    save_messages(messages, 'data/processed/10_random_sample_2700.xlsx')

    print('Finished data processing...')

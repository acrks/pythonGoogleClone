from bs4 import BeautifulSoup
import requests

import re

from urllib.parse import urljoin

def link_fisher(url, depth=0, reg_ex=""):
    res = _link_fisher(url, depth, reg_ex)
    res.append(url)
    return list(set(res))


def _link_fisher(url, depth, reg_ex):
    link_list = []
    if depth == 0:
        return link_list
    headers = {
        'User-Agent': ''}
    try:
        page = requests.get(url, headers=headers)
    except:
        print("Cannot retrieve", url)
        return link_list
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")
    for link in soup.find_all('a', attrs={'href': re.compile(reg_ex)}):
        link_list.append(urljoin(url, link.get('href')))
    for i in range(len(link_list)):
        link_list.extend(_link_fisher(link_list[i], depth - 1, reg_ex))
    return link_list


if __name__ == "__main__":
    print((link_fisher("http://compsci.mrreed.com", depth=3)))
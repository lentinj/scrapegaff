"""GiffGaff API interface.

Usage:
    giffgaff USER balance
    giffgaff USER receipts
"""
import datetime
import getpass
import os
import os.path
import logging
import re

from http.client import HTTPConnection
from lxml import html, etree
import requests


class GiffGaff():
    base_url = "https://www.giffgaff.com"

    def _page(self, path, post_data=None, xhr=False, debug=False):
        HTTPConnection.debuglevel = 1 if debug else 0
        if not hasattr(self, '_s'):
            self._s = requests.Session()
            self._s.keep_alive = False
        url = self.base_url + path
        req_headers = {}
        if xhr:
            req_headers['X-Requested-With'] = 'XMLHttpRequest'
        if post_data:
            page = self._s.post(url, data=post_data, headers=req_headers)
        else:
            page = self._s.get(url, headers=req_headers)
        if page.headers['Content-Type'].startswith('text/html'):
            return html.fromstring(page.content)
        return page.content

    def __init__(self, user_nick, password):
        self.user_nick = user_nick

        # Fetch login form, fill it in and post
        p = self._page('/auth/login')
        post_data = dict()
        for el in p.xpath("//form[@id = 'login']//input"):
            post_data[el.attrib['name']] = el.attrib['value']
        post_data['nickname'] = self.user_nick
        post_data['password'] = password

        p = self._page(p.xpath("//form[@id = 'login']/@action")[0], post_data)

        if 'napaUser' not in self._s.cookies.keys():
            raise ValueError("Missing cookies, not logged in")

    def order_history(self):
        p = self._page('/orders/history/others')

        out = []
        for tr in p.xpath("//table[@id = 'ordersTable']/tbody/tr"):
            tds = tr.xpath('td')
            out.append(dict(
                date=datetime.datetime.strptime(tds[0].text_content().strip(), '%d-%b-%Y'),
                content=tds[1].text_content().strip(),
                amount=tds[2].text_content().strip(),
                status=tds[3].text_content().strip(),
                paid_with=tds[4].text_content().strip(),
                id=tds[5].xpath('a/@href')[0].replace('/orders/view/', ''),
            ))
        if len(out) == 0:
            raise ValueError("Cannot find orders table on page")
        return out

    def balance(self):
        def format_text(node):
            for l in node.text_content().split('\n'):
                l = l.strip()
                if not l:
                    continue
                yield l

        p = self._page('/dashboard/balance?a=bm&refresh=true&dbg=undefined', xhr=True)
        return dict(
            balance=list(format_text(p.xpath("//div[@id = 'balance-value']")[0])),
            goodybag=list(format_text(p.xpath("//div[contains(@class, 'goodybag-container')]")[0])),
        )

    def vat_receipt(self, order_id, out_path):
        with open(out_path, 'wb') as f:
            f.write(self._page('/orders/vat/%s.pdf' % order_id))

    def fetch_all_vat_receipts(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        for o in self.order_history():
            path = os.path.join(out_dir, '%s.%s.pdf' % (datetime.datetime.strftime(o['date'], '%Y-%m-%d'), o['id']))

            if not os.path.exists(path) and o['paid_with'] == 'VISA':
                print("Downloading to %s" % path)
                self.vat_receipt(o['id'], path)


def script():
    import docopt

    arguments = docopt.docopt(__doc__)
    g = GiffGaff(
        arguments['USER'],
        getpass.getpass('Password for %s: ' % arguments['USER'])
    )

    if arguments['balance']:
        for k, v in g.balance().items():
            print("%s: %s" % (k, v))
    elif arguments['receipts']:
        g.fetch_all_vat_receipts('receipts_%s' % arguments['USER'])

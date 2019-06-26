import logging
import time

import requests

# Logging setup
logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)

ENDPOINT = 'https://api.monobank.ua/'


# TODO: [6/26/2019 by Mykola] add more exceptions and move them into a separated file
class MonobankError(Exception):
    pass


class Monobank(object):
    def __init__(self, token):
        self.token = token
        # No need to refresh headers every time, so it's better to make it constant
        self.headers = self._get_headers()

    def _get_headers(self):
        return {
            'X-Token': self.token,
            'User-Agent': 'python-monobank (https://github.com/vitalik/python-monobank, contact: ppr.vitaly@gmail.com)',
        }

    def _make_request(self, path, n=1):
        response = requests.get(ENDPOINT + path, headers=self.headers)
        data = response.json()
        if response.status_code != 200:
            message = data.get('errorDescription', str(data))
            raise MonobankError(message)
        return data

    def get_currency_info(self):
        url = 'bank/currency'
        return self._make_request(url)

    def get_client_info(self):
        url = 'personal/client-info'
        return self._make_request(url)

    def get_personal_statement(self, account_id=0,
                               date_from=round(time.time()) - (31 * 24 * 60 * 60),
                               date_to=round(time.time())):
        if date_from > date_to:
            raise MonobankError('date_from is greater than date_to!')
        elif date_to - date_from > (31 * 24 * 60 * 60):
            raise MonobankError('The time span is too large')
        url = f'/personal/statement/{account_id}/{date_from}/{date_to}'
        return self._make_request(url)

    def get_full_personal_statement(self, account_id=0):
        statement = []
        timestamp = round(time.time())
        while True:
            new_statements = self.get_personal_statement(account_id=account_id,
                                                         date_from=timestamp - (31 * 24 * 60 * 60),
                                                         date_to=timestamp)
            if not new_statements:
                break
            statement.extend(new_statements)
            timestamp -= (31 * 24 * 60 * 60)

        return statement

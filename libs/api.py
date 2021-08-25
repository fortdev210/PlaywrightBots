import requests
import base64

import settings


class StlproAPI:
    def __init__(self):
        self._headers = {
            "Authorization": "Basic " + base64.b64encode(
                bytes('{}:{}'.format(
                    settings.BUYBOT_USERNAME,
                    settings.BUYBOT_PASSWORD),
                    encoding="raw_unicode_escape")
            ).decode()
        }

    def get_ds_orders(self, supplier_id):
        url = settings.GET_DS_ORDERS_URL.format(supplier_id=supplier_id)
        response = requests.get(
            url,
            headers=self._headers
        )
        return response.json()

    def update_ds_order(self, ds_order_id, data):
        url = settings.UPDATE_DS_ORDER_INFO_URL.format(ds_order_id=ds_order_id)
        response = requests.post(
            url,
            headers=self._headers,
            json={'data': data, 'confirmed_by': settings.CONFIRMED_BY}
        )
        return response.json()

    def put_email_in_prep(self, ds_order_id, email):
        url = settings.SET_ORDER_FLAG_URL.format(ds_order_id=ds_order_id)
        response = requests.put(
            url,
            headers=self._headers,
            json={'flag': 'Walmart Processing', 'buyer_email': email}
        )
        return response.json()

    def put_order_in_process(self, ds_order_id):
        url = settings.SET_ORDER_FLAG_URL.format(ds_order_id=ds_order_id)
        response = requests.put(
            url,
            headers=self._headers,
            json={'flag': 'Walmart Processing'}
        )
        return response.json()

    def remove_email_from_prep(self, ds_order_id):
        url = settings.SET_ORDER_FLAG_URL.format(ds_order_id=ds_order_id)
        response = requests.put(
            url,
            headers=self._headers,
            json={
                "note": "Preprocessed by Playwright Bot",
                "flag": "Walmart Processing", "buyer_email_prep": None
            }
        )
        return response.json()

    def put_order_in_rebuy(self, ds_order_id):
        url = settings.SET_ORDER_FLAG_URL.format(ds_order_id=ds_order_id)
        response = requests.put(
            url,
            headers=self._headers,
            json={
                "note": "Preprocessed by Playwright Bot",
                "flag": "Walmart Prcessing Rebuy"
            }
        )
        return response.json()

    def set_cant_ship_to_address(self, ds_order_id):
        url = settings.SET_ORDER_FLAG_URL.format(ds_order_id=ds_order_id)
        response = requests.put(
            url,
            headers=self._headers,
            json={
                "note": "Preprocessed by Playwright Bot",
                "flag": "Cant Ship to Address"
            }
        )
        return response.json()

    def get_proxy_ips(self, supplier_id):
        url = settings.GET_PROXIES_URL.format(supplier_id=supplier_id)
        response = requests.get(
            url,
            headers=self._headers
        )
        res = response.json()
        return res.get('results')

    def gift_card_send_total_price(self, ds_order_id, total_price):
        url = settings.GIFT_CARD_SEND_TOTAL_URL.format(ds_order_id=ds_order_id)
        response = requests.patch(
            url,
            headers=self._headers,
            json={'supplier_site_total': total_price}
        )
        return response.json()

    def gift_card_send_current_card_info(
            self, ds_order_id, card_number, amount):
        url = settings.GIFT_CARD_SEND_CURRENT_CARD_URL.format(
            ds_order_id=ds_order_id)
        response = requests.patch(
            url,
            headers=self._headers,
            json={'gift_cards': [
                {'card_number': card_number, 'amount': amount}]}
        )
        return response.json()

    def gift_card_get_next_card(self, ds_order_id):
        url = settings.GIFT_CARD_GET_NEXT_CARD_URL.format(
            ds_order_id=ds_order_id)
        response = requests.patch(
            url,
            headers=self._headers,
            json={}
        )
        data = response.json()
        card_info = {}
        card_info['cardNumber'] = data.gift_card.split(',')[0]
        card_info['amount'] = data.gift_card.split(',')[1]
        return card_info

    def get_email_supplier(self):
        url = settings.GET_EMAIL_SUPPLIER
        response = requests.get(
            url,
            headers=self._headers
        )
        res = response.json()
        return res.get('results')

    def update_email_status(self, id, status):
        url = settings.UPDATE_EMAIL_STATUS + str(id)
        response = requests.patch(
            url,
            headers=self._headers,
            data={'status': status}
        )
        return response.json()

    def get_account_supplier(self, last_used_date):
        url = settings.GET_ACCOUNT_SUPPLIER.format(
            last_used_at_from=last_used_date)

        response = requests.get(
            url,
            headers=self._headers
        )
        res = response.json()
        return res.get('results')

    def update_account_status(self, id, status, last_used_date):
        url = settings.UPDATE_ACCOUNT_STATUS + str(id)
        response = requests.patch(
            url,
            headers=self._headers,
            data={'status': status, 'last_used_at': last_used_date}
        )
        return response.json()

    def get_category_suppliers(self, supplier_id, limit, offset):
        url = settings.GET_CATEGORY_SUPPLIER_URL.format(
            supplier_id=supplier_id, limit=limit, offset=offset
        )
        response = requests.get(
            url,
            headers=self._headers
        )
        return response.json()['results']

    def update_product_count(self, category_supplier_id, product_count):
        url = settings.UPDATE_CATEGORY_SUPPLIER_URL.format(
            category_supplier_id=category_supplier_id
        )
        response = requests.patch(
            url,
            headers=self._headers,
            json={'product_count': product_count}
        )
        settings.LOGGER.info(response.json())
        return response.json()

    def get_current_products(self, supplier_id, active, offset=0, limit=100):
        url = settings.GET_CURRENT_PRODUCT_URL.format(
            supplier_id=supplier_id, active=active, limit=limit, offset=offset
        )
        response = requests.get(
            url,
            headers=self._headers
        )
        return response.json()['results']

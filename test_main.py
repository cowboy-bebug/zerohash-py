from main import compute_vwap, PRICES, QUANTITY

import copy
import pytest
import random


test_messages = [
    {
        "type": "match",
        "product_id": "BTC-USD",
        "price": 1.2,
    },
    {
        "type": "match",
        "product_id": "ETH-USD",
        "price": 3.45,
    },
    {
        "type": "match",
        "product_id": "ETH-BTC",
        "price": 67.8,
    },
]


def test_compute_vwap_ignores_unknown_pairs():
    before_prices = copy.deepcopy(PRICES)
    msg = {
        "type": "match",
        "product_id": "ABC-DEF",
        "price": 123_456,
    }
    compute_vwap(msg)
    after_prices = copy.deepcopy(PRICES)
    assert before_prices == after_prices


@pytest.mark.parametrize("msg", test_messages)
def test_compute_vwap_works_when_queue_size_is_smaller_than_quantity(msg):
    before_prices = copy.deepcopy(PRICES)
    compute_vwap(msg)
    after_prices = copy.deepcopy(PRICES)
    for pair in before_prices.keys() & after_prices.keys():
        before_prices_len = len(before_prices[pair]["prices"])
        before_sum = before_prices[pair]["prices_sum"]

        after_prices_len = len(after_prices[pair]["prices"])
        after_sum = after_prices[pair]["prices_sum"]

        if pair == msg["product_id"]:
            assert after_prices_len > before_prices_len
            assert after_prices_len == before_prices_len + 1

            assert after_sum > before_sum
            assert after_sum == before_sum + msg["price"]
        else:
            assert after_prices_len == before_prices_len
            assert after_sum == before_sum


@pytest.mark.parametrize("msg", test_messages)
def test_compute_vwap_works_when_queue_size_is_equal_to_quantity(msg):
    # prepopulate PRICES with random numbers
    for pair in PRICES.keys():
        for _ in range(QUANTITY):
            PRICES[pair]["prices"].append(random.random())
        PRICES[pair]["prices_sum"] = sum(PRICES[pair]["prices"])

    before_prices = copy.deepcopy(PRICES)
    compute_vwap(msg)
    after_prices = copy.deepcopy(PRICES)
    for pair in before_prices.keys() & after_prices.keys():
        before_prices_len = len(before_prices[pair]["prices"])
        before_sum = before_prices[pair]["prices_sum"]

        after_prices_len = len(after_prices[pair]["prices"])
        after_sum = after_prices[pair]["prices_sum"]

        assert after_prices_len == before_prices_len
        if pair == msg["product_id"]:
            before_first_price = before_prices[pair]["prices"].popleft()
            assert after_sum > before_sum
            assert after_sum == before_sum - before_first_price + msg["price"]
            before_prices[pair]["prices"].appendleft(before_first_price)
        else:
            assert after_sum == before_sum

import collections
import json
import logging
import websocket  # NOTE: if we want async + await style, websockets can be used instead


# NOTE: some of these constants could come from config / env var in future
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(levelname)s] %(asctime)s %(funcName)s: %(message)s"

WS_ADDR = "wss://ws-feed.exchange.coinbase.com"
WS_PAIRS = ["BTC-USD", "ETH-USD", "ETH-BTC"]
WS_DEFAULT_TIMEOUT_SECONDS = 5

QUANTITY = 200
PRICES = {
    pair: {
        "prices": collections.deque(maxlen=QUANTITY),
        "prices_sum": 0,
    }
    for pair in WS_PAIRS
}


# Computes volume-weighted average price from websocket messages
def compute_vwap(msg):
    if (
        "product_id" in msg
        and "price" in msg
        and msg["type"] == "match"
        and msg["product_id"] in WS_PAIRS
    ):
        pair = msg["product_id"]
        price = float(msg["price"])

        if len(PRICES[pair]["prices"]) >= QUANTITY:
            PRICES[pair]["prices_sum"] -= PRICES[pair]["prices"].popleft()

        PRICES[pair]["prices"].append(price)
        PRICES[pair]["prices_sum"] += price

        vwap = PRICES[pair]["prices_sum"] / len(PRICES[pair]["prices"])
        logging.info(f"[{pair}] vwap: {vwap}")
        # TODO: push to a queue for dependant consumer microservice


# Runs on websocket open event
def on_open(ws):
    logging.debug("subscribing ... ")
    ws.send(
        json.dumps(
            {
                "type": "subscribe",
                "product_ids": WS_PAIRS,
                "channels": ["matches"],
            }
        )
    )
    logging.debug("successfully subscribed!")


# Runs on websocket message event
def on_message(ws, msg):
    logging.debug("msg received")
    msg = json.loads(msg)
    if "type" in msg:
        if msg["type"] == "error":
            logging.error(f"something went wrong: {msg}")
            # TODO: push to DLQ for further processing / analysis
        else:
            try:
                compute_vwap(msg)
            except Exception as e:
                logging.error(f"something went wrong: {e}")
                # TODO: push to DLQ for further processing / analysis
        logging.debug("msg processed")


# Runs on websocket error event
def on_error(ws, err):
    logging.error(f"something went wrong: {err}")
    # TODO: push to DLQ for further processing / analysis


# Runs on websocket close event
def on_close(ws, close_status_code, close_msg):
    logging.info(f"websocket close with {close_status_code}: {close_msg}")


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
    websocket.setdefaulttimeout(WS_DEFAULT_TIMEOUT_SECONDS)
    ws = websocket.WebSocketApp(
        WS_ADDR,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
    )
    ws.run_forever()

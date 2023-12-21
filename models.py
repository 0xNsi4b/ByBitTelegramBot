from telethon import TelegramClient, events
from pybit.unified_trading import HTTP
import pandas as pd
import config


api_id = int(config.info.telegram_id.get_secret_value())
api_hash = config.info.telegram_hash.get_secret_value()
client = TelegramClient('anon', api_id, api_hash)

pump_dump_link = 'pump_screener_bot'
io_link = 'Open_Interest_screener_bot'
io_dict = {}

api_key = config.info.bybit_api.get_secret_value()
api_secret = config.info.bybit_secret.get_secret_value()
session = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)


def count_decimal(number: str) -> int:
    if '.' in number:
        decimal_part = number.split('.')[1]
        return len(decimal_part)
    else:
        return 0


def read_csv():
    return pd.read_csv('settings.csv').to_dict('records')[0]


def get_position(pair: str):
    return session.get_positions(category='linear', symbol=pair)['result']['list'][0]


def get_info(pair: str):
    return session.get_instruments_info(category="linear", symbol=pair)['result']['list'][0]


def create_order(pair: str, side: str):
    settings = read_csv()
    position = get_position(pair)
    info = get_info(pair)

    # Check leverage
    max_leverage = float(info['leverageFilter']['maxLeverage'])
    leverage = settings['leverage']

    if max_leverage < leverage:
        leverage = max_leverage

    if int(position['leverage']) != leverage:
        session.set_leverage(
            category="linear",
            symbol=pair,
            buyLeverage=str(leverage),
            sellLeverage=str(leverage),
        )
        print('set leverage')

    # Check trade mode
    if position['tradeMode'] != 1:
        session.switch_margin_mode(
            category="linear",
            symbol=pair,
            tradeMode=1,
        )
        print('set margin')

    # Set qty
    min_order = info['lotSizeFilter']['minOrderQty']
    precision = count_decimal(min_order)
    amount = settings['leverage'] * settings['value'] / float(position['markPrice'])
    trailing_stop_amount = float(position['markPrice']) * settings['stop'] / 100
    trailing_stop = round(trailing_stop_amount, 4)

    # Get precision
    if precision == 0:
        qty = int(amount)
    else:
        qty = round(amount, precision)

    if float(min_order) > qty:
        qty = min_order

    # Open position
    session.place_order(
        category='linear',
        symbol=pair,
        side=side,
        orderType='Market',
        qty=str(qty),
        isLeverage=1,
        reduceOnly=False,
        closeOnTrigger=False
    )

    # Set take profit
    if side == 'Buy':
        price = round(float(position['markPrice']) * (1 + settings['profit'] / 100), 4)
    else:
        price = round(float(position['markPrice']) * (1 - settings['profit'] / 100), 4)

    session.set_trading_stop(
        category='linear',
        symbol=pair,
        trailingStop=str(trailing_stop),
        takeProfit=str(price),
        positionIdx=0
    )


@client.on(events.NewMessage(chats=pump_dump_link))
async def my_event_handler(event):
    try:
        text = event.raw_text.split()
        if 'PUMP' in text:
            create_order(f'{text[5]}USDT', 'Buy')
        if 'DUMP' in text:
            create_order(f'{text[5]}USDT', 'Buy')
    except:
        print('Error')


@client.on(events.NewMessage(chats=io_link))
async def my_event_handler(event):
    try:
        token = event.raw_text.split()[5]
        if token not in io_dict:
            io_dict[token] = 1
        else:
            io_dict[token] += 1
        if io_dict[token] >= 3:
            create_order(f'{token}USDT', 'Buy')
            print('d')
            io_dict[token] = 0
        print(event.raw_text.split())
    except:
        print('Error')


with client:
    client.run_until_disconnected()


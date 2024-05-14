BASE_URL = "https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&offer_type=flat"

ROOM = "&room{}=1"
MIN_PRICE = "&minprice={}"
MAX_PRICE = "&maxprice={}"
OBJECT_TYPE = "&object_type[0]={}"
REGION = '&region={}'
PAGE = '&p={}'

MAX_RETRIES = 3
RETRY_SLEEP = 3
STATE_FILE_LINKS = 'links/state_links.json'
STATE_FILE_DATA = 'data/state_data.json'

CITIES = {
    "kazan": 4777,
    "ufa": 176245,
    "orenburg": 4915,
    "perm": 4927,
    "ulyanovsk": 5027,
    "samara": 4966,
    "novgorod": 4885
}

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Brave\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "\"Android\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "cookie": "_osm_totp_token=114327"
}

PRICE_RANGES = [
    ('', '2000000'),
    ('2000000', '4000000'),
    ('4000000', '6000000'),
    ('6000000', '8000000'),
    ('8000000', '10000000'),
    ('10000000', '12000000'),
    ('12000000', '14000000'),
    ('14000000', '18000000'),
    ('18000000', '25000000'),
    ('25000000', '')
]

ROOMS = [1, 2, 3, 4, 5, 6, 7, 9]

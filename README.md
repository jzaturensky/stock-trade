# Stock-Trader

## Python
- Use Python 3.7 or above (virtual environment recommended)
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Run `./trader.py --help` for CLI format
    - E.g. `./trader.py --brokerage dry_run --strategy vansh -d`
    - E.g. `./trader.py --brokerage dry_run --strategy vansh -e on_market_open`
- Add any credentials to the `config` directory

### Setting up Alpaca Brokerage

To use the Alpaca brokerage (paper money or real money), follow these steps:

1) Go to https://alpaca.markets/
2) Create a new account
3) Generate the Key ID and Secret Key
4) Go to the `/config` directory and run `touch alpaca.json`
5) Paste your key id and secret in the following format:

``` JSON
{
    "key_id": "<YOUR KEY HERE>",
    "secret_key": "<YOUR SECRET HERE>"
}
```

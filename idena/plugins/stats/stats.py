import idena.constants as con
import idena.emoji as emo
import idena.utils as utl
import logging

from telegram import ParseMode
from pycoingecko import CoinGeckoAPI
from idena.plugin import IdenaPlugin


class Stats(IdenaPlugin):

    def execute(self, bot, update, args):
        try:
            data = CoinGeckoAPI().get_coin_by_id(con.CG_ID)
        except Exception as e:
            error = f"{emo.ERROR} Could not retrieve price"
            update.message.reply_text(error)
            logging.error(e)
            self.notify(e)
            return

        if not data:
            update.message.reply_text(f"{emo.ERROR} Could not retrieve data")
            return

        name = data["name"]
        symbol = data["symbol"].upper()

        rank_mc = data["market_cap_rank"]
        rank_cg = data["coingecko_rank"]

        cs = int(float(data['market_data']['circulating_supply']))
        sup_c = f"{utl.format(cs)} {symbol}"

        if data["market_data"]["total_supply"]:
            ts = int(float(data["market_data"]["total_supply"]))
            sup_t = f"{utl.format(ts)} {symbol}"
        else:
            sup_t = "N/A"

        usd = data["market_data"]["current_price"]["usd"]
        eur = data["market_data"]["current_price"]["eur"]
        btc = data["market_data"]["current_price"]["btc"]
        eth = data["market_data"]["current_price"]["eth"]

        p_usd = utl.format(usd, force_length=True)
        p_eur = utl.format(eur, force_length=True, template=p_usd)
        p_btc = utl.format(btc, force_length=True, template=p_usd)
        p_eth = utl.format(eth, force_length=True, template=p_usd)

        p_usd = "{:>12}".format(p_usd)
        p_eur = "{:>12}".format(p_eur)
        p_btc = "{:>12}".format(p_btc)
        p_eth = "{:>12}".format(p_eth)

        v_24h = utl.format(int(float(data["market_data"]["total_volume"]["usd"])))
        m_cap = utl.format(int(float(data["market_data"]["market_cap"]["usd"])))

        if data["market_data"]["price_change_percentage_1h_in_currency"]:
            c_1h = data["market_data"]["price_change_percentage_1h_in_currency"]["usd"]
            c1h = utl.format(float(c_1h), decimals=2, force_length=True)
            h1 = "{:>10}".format(f"{c1h}%")
        else:
            h1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_24h_in_currency"]:
            c_1d = data["market_data"]["price_change_percentage_24h_in_currency"]["usd"]
            c1d = utl.format(float(c_1d), decimals=2, force_length=True)
            d1 = "{:>10}".format(f"{c1d}%")
        else:
            d1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_7d_in_currency"]:
            c_1w = data["market_data"]["price_change_percentage_7d_in_currency"]["usd"]
            c1w = utl.format(float(c_1w), decimals=2, force_length=True)
            w1 = "{:>10}".format(f"{c1w}%")
        else:
            w1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_30d_in_currency"]:
            c_1m = data["market_data"]["price_change_percentage_30d_in_currency"]["usd"]
            c1m = utl.format(float(c_1m), decimals=2, force_length=True)
            m1 = "{:>10}".format(f"{c1m}%")
        else:
            m1 = "{:>10}".format("N/A")

        if data["market_data"]["price_change_percentage_1y_in_currency"]:
            c_1y = data["market_data"]["price_change_percentage_1y_in_currency"]["usd"]
            c1y = utl.format(float(c_1y), decimals=2, force_length=True)
            y1 = "{:>10}".format(f"{c1y}%")
        else:
            y1 = "{:>10}".format("N/A")

        msg = f"{name} ({symbol})\n\n" \
              f"USD {p_usd}\n" \
              f"EUR {p_eur}\n" \
              f"BTC {p_btc}\n" \
              f"ETH {p_eth}\n\n" \
              f"Hour  {h1}\n" \
              f"Day   {d1}\n" \
              f"Week  {w1}\n" \
              f"Month {m1}\n" \
              f"Year  {y1}\n\n" \
              f"Market Cap Rank: {rank_mc}\n" \
              f"Coin Gecko Rank: {rank_cg}\n\n" \
              f"Volume 24h: {v_24h} USD\n" \
              f"Market Cap: {m_cap} USD\n" \
              f"Circ. Supp: {sup_c}\n" \
              f"Total Supp: {sup_t}\n\n"

        cg_link = f"👉 https://idena.today 👈"

        update.message.reply_text(
            text=f"`{msg}`{cg_link}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            quote=False)

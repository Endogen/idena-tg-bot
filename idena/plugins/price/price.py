import idena.emoji as emo
import logging

from telegram import ParseMode
from pycoingecko import CoinGeckoAPI
from idena.plugin import IdenaPlugin


class Price(IdenaPlugin):

    BASE = "DNA"
    CG_ID = "idena"
    CG_URL = "https://www.coingecko.com/coins/idena"

    @IdenaPlugin.threaded
    @IdenaPlugin.send_typing
    def execute(self, bot, update, args):
        try:
            result = CoinGeckoAPI().get_coin_ticker_by_id(self.CG_ID)
        except Exception as e:
            error = f"{emo.ERROR} Could not retrieve price"
            update.message.reply_text(error)
            logging.error(e)
            self.notify(e)
            return

        reply = "Price of DNA\n\n"
        for target, price in result["tickers"][0]["converted_last"].items():
            reply += f"{target.upper():<5}{price:.8f}\n"

        cg_link = f"\n👉 https://idena.today 👈"

        update.message.reply_text(
            text=f"`{reply}`{cg_link}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            quote=False)

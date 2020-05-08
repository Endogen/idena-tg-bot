import idena.constants as con
import idena.emoji as emo
import logging

from telegram import ParseMode
from idena.plugin import IdenaPlugin
from idena.coinpaprika import CoinPaprikaAPI


class Price(IdenaPlugin):

    @IdenaPlugin.threaded
    @IdenaPlugin.send_typing
    def execute(self, bot, update, args):
        try:
            res = CoinPaprikaAPI().get_ticker(con.CP_ID, quotes="USD,EUR,BTC,ETH")
        except Exception as e:
            error = f"{emo.ERROR} Could not retrieve price"
            update.message.reply_text(error)
            logging.error(e)
            self.notify(e)
            return

        reply = "Price of DNA\n\n"
        for target, details in res["quotes"].items():
            reply += f"{target.upper():<5}{details['price']:.8f}\n"

        cg_link = f"\n👉 https://idena.today 👈"

        update.message.reply_text(
            text=f"`{reply}`{cg_link}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            quote=False)

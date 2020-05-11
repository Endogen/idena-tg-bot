import idena.constants as con
import idena.emoji as emo
import logging

from telegram import ParseMode
from idena.plugin import IdenaPlugin
from idena.coinpaprika import CoinPaprikaAPI
from idena.qtrade import QtradeAPI, QtradeAuth


class Price(IdenaPlugin):

    link = f"\n👉 https://idena.today 👈"
    _market = "DNA_BTC"

    @IdenaPlugin.threaded
    @IdenaPlugin.send_typing
    def execute(self, bot, update, args):
        if args and args[0].lower() == "qtrade":
            try:
                qtrade = QtradeAPI(QtradeAuth(self.get_token("qtrade")))
                price = qtrade.get_ticker(self._market)["data"]["last"]
            except Exception as e:
                error = f"{emo.ERROR} Could not retrieve price"
                update.message.reply_text(error)
                logging.error(e)
                self.notify(e)
                return

            base = self._market.split('_')[1].upper()

            msg = f"Price of DNA (qTrade)\n\n"
            msg += f"{base:<5}{float(price):.8f}\n"

        else:
            try:
                res = CoinPaprikaAPI().get_ticker(con.CP_ID, quotes="USD,EUR,BTC,ETH")
            except Exception as e:
                error = f"{emo.ERROR} Could not retrieve price"
                update.message.reply_text(error)
                logging.error(e)
                self.notify(e)
                return

            msg = "Price of DNA (CoinGecko)\n\n"
            for target, details in res["quotes"].items():
                msg += f"{target.upper():<5}{details['price']:.8f}\n"

        update.message.reply_text(
            text=f"`{msg}`{self.link}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            quote=False)

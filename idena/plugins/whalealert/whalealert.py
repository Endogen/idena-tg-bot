import logging
import calendar
import requests
import idena.emoji as emo

from random import randrange
from datetime import datetime
from telegram import ParseMode
from idena.plugin import IdenaPlugin


class Whalealert(IdenaPlugin):

    def __enter__(self):
        trx = self.config.get("trx")
        api_url = self.config.get("api")
        limit = self.config.get("limit")
        trx_url = self.config.get("trx_url")
        interval = self.config.get("interval")
        exchanges = self.config.get("exchanges")

        # TODO: Change
        # first=randrange(0, interval),

        for name, address in exchanges.items():
            self.repeat_job(
                self.check,
                interval,
                context={
                    "name": name,
                    "address": address,
                    "limit": limit,
                    "interval": interval,
                    "api": api_url,
                    "trx_url": trx_url,
                    "trx": trx
                })

        return self

    def check(self, bot, job):
        url = job.context["api"]
        name = job.context["name"]
        steps = job.context["trx"]
        limit = job.context["limit"]
        trx_url = job.context["trx_url"]
        ex_addr = job.context["address"]
        interval = job.context["interval"]

        url += f"{ex_addr}/txs"

        skip = 0
        next = True
        while next:
            try:
                response = requests.get(url, params={"skip": skip, "limit": steps}).json()
                logging.info(f"Transactions: {response}")
                if not response or not response["result"]:
                    logging.error("No result", job.context)
                    return
            except Exception as e:
                msg = f"API not reachable: {e}"
                logging.error(msg)
                return

            first_trx = True
            for trx in reversed(response["result"]):
                logging.info("--------------------")
                logging.info(trx)

                timestamp = trx["timestamp"]
                amount = trx["amount"]
                type = trx["type"]
                from_addr = trx["from"]
                to_addr = trx["to"]
                hash = trx["hash"]

                d = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                sec_trx = int(calendar.timegm(d.timetuple()))
                sec_now = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

                logging.info(f"Timestamp   : {d}")
                logging.info(f"DNA Amount  : {float(amount):.4f}")
                logging.info(f"Millis Trx  : {sec_trx}")
                logging.info(f"Millis Now  : {sec_now}")
                logging.info(f"Difference  : {(sec_now - sec_trx)/60:.2f} Min.")

                if sec_trx < (sec_now - interval):
                    logging.info(f"In Timerange: {sec_trx < (sec_now - interval)}")
                    if first_trx:
                        logging.info(f"First Trans.: {first_trx}")
                        logging.info(f"Next Run    : {next}")
                        first_trx = False
                        next = False
                    continue

                logging.info(f"First Trans.: {first_trx}")
                logging.info("No Next Run : FALSE")

                first_trx = False

                if type == "SendTx" and float(amount) >= float(limit):
                    logging.info("Rel. Type   : Yes")
                    logging.info("Rel. Amount : Yes")

                    to_exchange = True if to_addr == ex_addr else False
                    logging.info(f"To Exchange : {to_exchange}")

                    amm = int(float(amount))
                    lnk = f"[Show Transaction Details]({trx_url + hash})"

                    if to_exchange:
                        adr = f"{from_addr[:8]}..."
                        msg = f"`{amm:,}` DNA from #{adr} to {name}\n{lnk}"
                    else:
                        adr = f"{to_addr[:8]}..."
                        msg = f"`{amm:,}` DNA from {name} to #{adr}\n{lnk}"

                    logging.info(f"Message     : {msg}")

                    for chat_id in self.config.get("send_to"):
                        try:
                            bot.send_message(
                                chat_id,
                                msg,
                                parse_mode=ParseMode.MARKDOWN,
                                disable_web_page_preview=True,
                                disable_notification=True)
                        except Exception as e:
                            msg = f"{emo.ERROR} Not possible to send whale alert: {e}"
                            logging.error(msg)
                            self.notify(msg)
                else:
                    logging.info(f"Transaction not relevant")
                    logging.info(f"Trx. Type  : {type}")
                    logging.info(f"Trx. Amount: {float(amount):.4f}")

            skip += steps

    @IdenaPlugin.owner
    @IdenaPlugin.threaded
    @IdenaPlugin.send_typing
    def execute(self, bot, update, args):
        if args:
            if args[0].lower() == "no":
                # TODO
                pass
            elif args[0].lower() == "off":
                # TODO
                pass
        else:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)

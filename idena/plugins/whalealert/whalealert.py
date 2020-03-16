import logging
import requests
import idena.emoji as emo

from random import randrange
from telegram import ParseMode
from idena.plugin import IdenaPlugin


class Whalealert(IdenaPlugin):

    def __enter__(self):
        if not self.config.get("active"):
            return self

        tx_count = self.config.get("tx_count")
        ad_url = self.config.get("ad_url")
        threshold = self.config.get("threshold")
        tx_url = self.config.get("tx_url")
        interval = self.config.get("interval")
        exchanges = self.config.get("exchanges")

        for name, address in exchanges.items():
            self.repeat_job(
                self.check,
                interval,
                first=randrange(0, interval),
                context={
                    "name": name,
                    "address": address,
                    "threshold": threshold,
                    "api": ad_url,
                    "trx_url": tx_url,
                    "trx": tx_count,
                    "last": None
                })

        return self

    def check(self, bot, job):
        url = job.context["api"]
        name = job.context["name"]
        steps = job.context["trx"]
        tx_url = job.context["trx_url"]
        ex_addr = job.context["address"]
        threshold = job.context["threshold"]
        last_tx = job.context["last"]

        url += f"{ex_addr}/txs"
        transactions = list()

        skip = 0
        next_run = True

        # Get all relevant transactions
        while next_run:
            try:
                response = requests.get(url, params={"skip": skip, "limit": steps}).json()
                logging.info(f"Transactions (skip={skip}, limit={steps}): {response}")
                if not response or not response["result"]:
                    msg = f"{emo.ERROR} No API result - {job.context}"
                    logging.error(msg)
                    self.notify(msg)
                    return
            except Exception as e:
                msg = f"{emo.ERROR} API not reachable: {e} - {job.context}"
                logging.error(msg)
                self.notify(msg)
                return

            if last_tx is None:
                transactions.extend(response["result"])
                next_run = False
            else:
                for tx in response["result"]:
                    if tx["hash"] == last_tx:
                        next_run = False
                        break
                    else:
                        transactions.append(tx)

            skip += steps

        # Analyse all relevant transactions
        for tx in reversed(transactions):
            amount = int(float(f"{float(tx['amount']):.1f}"))
            type = tx["type"]
            from_addr = tx["from"]
            to_addr = tx["to"]
            hash = tx["hash"]

            if type == "SendTx" and amount >= int(threshold):
                logging.info(f"FOUND: {tx}")

                job.context["last"] = tx["hash"]

                lnk = f"[Show Transaction Details]({tx_url + hash})"
                to_exchange = True if to_addr == ex_addr else False

                if to_exchange:
                    adr = f"{from_addr[:8]}"
                    msg = f"`{amount:,}` DNA from #{adr} to {name}\n{lnk}"
                else:
                    adr = f"{to_addr[:8]}"
                    msg = f"`{amount:,}` DNA from {name} to #{adr}\n{lnk}"

                for chat_id in self.config.get("notify"):
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

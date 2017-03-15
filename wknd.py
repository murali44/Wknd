import argparse
import datetime
import db
import logging
import scrape
import signal
import sql_db
import sys
import time
import utils

from logging.handlers import RotatingFileHandler
from selenium import webdriver

PATH='wknd.log'
LOGGER = logging.getLogger("Rotating Log")
LOGGER.setLevel(logging.INFO)
# add a rotating handler
handler = RotatingFileHandler(PATH, maxBytes=50000, backupCount=3)
LOGGER.addHandler(handler)

def main():
    """
    Perform a search on southwest.com for the given flight parameters.
    """
    args = utils.parse_args()
    desired_price = int(args.desired_total)

    while True:
        sql_db.delete_old()
        for d in utils.allfridays(int(args.weekends)):
            args.departure_date = d.strftime('%m/%d/%Y')
            args.return_date = (d + datetime.timedelta(days=2)).strftime('%m/%d/%Y')
            price = get_price(args)
            # Log
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            msg = "[{0}] {1}->{2}. ${3} on {4}.".format(st,
                                                        args.depart,
                                                        args.arrive,
                                                        price,
                                                        args.departure_date)

            sql_db.update_db(args, price)
            LOGGER.info(msg)
            LOGGER.info(sql_db.show_all())
            if price <= desired_price: utils.send_email(args, price)

            time.sleep(5)

        # Sleep before scraping again.
        LOGGER.info("Sleeping for {0} minutes.".format(args.interval))
        time.sleep(int(args.interval) * 60)

def get_price(args):
    # PhantomJS is headless, so it doesn't open up a browser.
    browser = webdriver.PhantomJS()
    try:
        price = scrape.scrape(args, browser)
    except:
        pass
    finally:
        browser.close()
        browser.service.process.send_signal(signal.SIGTERM)
        browser.quit()

    return price


if __name__ == "__main__":
    main()

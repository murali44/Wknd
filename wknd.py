import argparse
import datetime
import db
import logging
import scrape
import signal
import sys
import time
import utils

from logging.handlers import RotatingFileHandler
from selenium import webdriver

def main():
    """
    Perform a search on southwest.com for the given flight parameters.
    """
    args = utils.parse_args()
    desired_price = int(args.desired_total)

    while True:
        for d in utils.allfridays(int(args.weekends)):
            args.departure_date = d.strftime('%m/%d/%Y')
            args.return_date = (d + datetime.timedelta(days=2)).strftime('%m/%d/%Y')
            price = scrape.get_price(args)
            msg = "{0}->{1}. ${2} leaving on {3}.".format(args.depart,
                                                          args.arrive,
                                                          price,
                                                          args.departure_date)

            utils.log(msg)
            db.update_db(args, price)
            if price <= desired_price: utils.send_email(args, price)

            time.sleep(5)


if __name__ == "__main__":
    main()

import os
import signal
import smtplib
import sys
import json
import time
import datetime
import db
import utils
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def main():
    """
    Perform a search on southwest.com for the given flight parameters.
    """
    args = utils.parse_args()
    while True:
        desired_price = int(args.desired_total)
        found_depart_date = 0
        found_return_date = 0
        for d in utils.allfridays(int(args.weekends)):
            price = 100000
            # PhantomJS is headless, so it doesn't open up a browser.
            browser = webdriver.PhantomJS()
            args.departure_date = d.strftime('%m/%d/%Y')
            args.return_date = (d + datetime.timedelta(days=2)).strftime('%m/%d/%Y')
            try:
                price = scrape.scrape(args, browser)
            except:
                pass
            finally:
                # kill the specific phantomjs child proc
                browser.close()
                browser.service.process.send_signal(signal.SIGTERM)
                browser.quit()
            if price <= desired_price:
                desired_price = price
                found_depart_date = args.departure_date
                found_return_date = args.return_date
                print "cost:{0}. leaving:{1} Arrving:{2}".format(
                    desired_price, found_depart_date, found_return_date)
            else:
                print "{0}->{1}. Cheapest is {2} leaving on {3}. I'll keep looking.".format(args.depart, args.arrive, price, args.departure_date)
            # write to dynamoDB
            """response = db.get_item(args.arrive, args.departure_date)
            if 'Item' in response:
                if response['Item']['Price'] != price:
                    db.update_price(args.arrive,
                                    args.departure_date,
                                    price)
            else:
                db.add_item(args.depart,
                            args.arrive,
                            args.departure_date,
                            args.return_date, price)"""
            time.sleep(5)

        if found_depart_date != 0:
            print "found final"
            print "cost:{0}. leaving:{1} Arrving:{2}".format(
                desired_price, found_depart_date, found_return_date)
            utils.send_email(args.depart, args.arrive,
                       desired_price, found_depart_date)

        # Keep scraping according to the interval the user specified.
        time.sleep(int(args.interval) * 60)


if __name__ == "__main__":
    main()

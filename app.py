import argparse
import os
import signal
import smtplib
import sys
import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def main():
    """
    Perform a search on southwest.com for the given flight parameters.
    """
    args = parse_args()
    while True:
        desired_price = int(args.desired_total)
        found_depart_date = 0
        found_return_date = 0
        for d in allfridays(int(args.weekends)):
            # PhantomJS is headless, so it doesn't open up a browser.
            browser = webdriver.PhantomJS()
            args.departure_date = d.strftime('%m/%d/%Y')
            args.return_date = (d + datetime.timedelta(days=2)).strftime('%m/%d/%Y')
            try:
                price = scrape(args, browser)
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
                print "cost:{0}. leaving:{1} Arrving:{2}".format(desired_price, found_depart_date, found_return_date)
            else:
                print "{0} -> {1}. Cheapest is {2} leaving on {3}. I'll keep looking.".format(args.depart, args.arrive, price, args.departure_date)
            time.sleep(15)

        if found_depart_date != 0:
            print "found final"
            print "cost:{0}. leaving:{1} Arrving:{2}".format(desired_price, found_depart_date, found_return_date)
            send_email(args.depart, args.arrive, desired_price, found_depart_date)

        # Keep scraping according to the interval the user specified.
        time.sleep(int(args.interval) * 60)


def allfridays(weekends):
   d = datetime.date.today()
   while d.weekday() != 4:
       d += datetime.timedelta(1)

   for x in range(weekends):
      yield d
      d += datetime.timedelta(days = 7)

def parse_args():
    """
    Parse the command line for search parameters.
    """
    parser = argparse.ArgumentParser(description='Process command line arguments')

    parser.add_argument(
        "--one-way",
        action="store_true",
        help="If present, the search will be limited to one-way tickets.")

    parser.add_argument(
        "--depart",
        "-d",
        type=str,
        default='AUS',
        help="Origin airport code.")

    parser.add_argument(
        "--arrive",
        "-a",
        type=str,
        help="Destination airport code.")

    parser.add_argument(
        "--departure-date",
        "-dd",
        type=str,
        help="Date of departure flight.")

    parser.add_argument(
        "--return-date",
        "-rd",
        type=str,
        help="Date of return flight.")

    parser.add_argument(
        "--passengers",
        "-p",
        action="store",
        type=str,
        default=2,
        help="Number of passengers.")

    parser.add_argument(
        "--desired-total",
        "-dt",
        type=str,
        default=250,
        help="Ceiling on the total cost of flights.")

    parser.add_argument(
        "--weekends",
        "-wk",
        type=str,
        default=24,
        help="Number of weekends to search.")

    parser.add_argument(
        "--interval",
        "-i",
        type=str,
        default=40,
        help="Refresh time period.")

    args = parser.parse_args()

    return args

def send_email(depart_from, arrive_to, final_price, depart_date):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.environ['WKND_FROM_EMAIL'], os.environ['WKND_PASSWORD'])
        msg_body = "Found {0}->{1} deal. ${2}. Leaving {3}. On Southwest.".format(depart_from, arrive_to, final_price, depart_date)
        msg = 'Subject: {0}\n\n{1}'.format("WKND Deal found.", msg_body)
        server.sendmail(os.environ['WKND_FROM_EMAIL'], os.environ['WKND_TO_EMAIL'], msg)
        server.quit()
    except:
        pass

def scrape(args, browser):
    browser.get("https://www.southwest.com/")
    last_travel_date = browser.find_element_by_id("lastBookableDate").get_attribute("value")
    departure_date = datetime.datetime.strptime(args.departure_date, '%m/%d/%Y')
    return_date = datetime.datetime.strptime(args.return_date, '%m/%d/%Y')
    last_travel_date = datetime.datetime.strptime(last_travel_date, '%m/%d/%Y')

    if (departure_date > last_travel_date) or (return_date > last_travel_date):
        return 100000

    if args.one_way:
        # Set one way trip with click event.
        one_way_elem = browser.find_element_by_id("trip-type-one-way")
        one_way_elem.click()

    # Set the departing airport.
    depart_airport = browser.find_element_by_id("air-city-departure")
    depart_airport.send_keys(args.depart)

    # Set the arrival airport.
    arrive_airport = browser.find_element_by_id("air-city-arrival")
    arrive_airport.send_keys(args.arrive)

    # Set departure date.
    depart_date = browser.find_element_by_id("air-date-departure")
    depart_date.clear()
    depart_date.send_keys(args.departure_date)

    if not args.one_way:
        # Set return date.
        return_date = browser.find_element_by_id("air-date-return")
        return_date.clear()
        return_date.send_keys(args.return_date)

    # Clear the readonly attribute from the element.
    passengers = browser.find_element_by_id("air-pax-count-adults")
    browser.execute_script("arguments[0].removeAttribute('readonly', 0);", passengers)
    passengers.click()
    passengers.clear()

    # Set passenger count.
    passengers.send_keys(args.passengers)
    passengers.click()
    search = browser.find_element_by_id("jb-booking-form-submit-button")
    search.click()

    outbound_array = []
    return_array = []

    # Webdriver might be too fast. Tell it to slow down.
    wait = WebDriverWait(browser, 120)
    wait.until(EC.element_to_be_clickable((By.ID, "faresOutbound")))

    outbound_fares = browser.find_element_by_id("faresOutbound")
    outbound_prices = outbound_fares.find_elements_by_class_name("product_price")

    for price in outbound_prices:
        realprice = price.text.replace("$", "")
        outbound_array.append(int(realprice))

    lowest_outbound_fare = min(outbound_array)

    if not args.one_way:
        return_fares = browser.find_element_by_id("faresReturn")
        return_prices = return_fares.find_elements_by_class_name("product_price")

        for price in return_prices:
            realprice = price.text.replace("$", "")
            return_array.append(int(realprice))

        lowest_return_fare = min(return_array)
        real_total = lowest_outbound_fare + lowest_return_fare
    else:
        real_total = lowest_outbound_fare

    return real_total


if __name__ == "__main__":
    main()

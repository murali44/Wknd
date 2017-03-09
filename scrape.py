import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
        outbound_array.append(float(realprice))

    lowest_outbound_fare = min(outbound_array)

    if not args.one_way:
        return_fares = browser.find_element_by_id("faresReturn")
        return_prices = return_fares.find_elements_by_class_name("product_price")

        for price in return_prices:
            realprice = price.text.replace("$", "")
            return_array.append(float(realprice))

        lowest_return_fare = min(return_array)
        real_total = lowest_outbound_fare + lowest_return_fare
    else:
        real_total = lowest_outbound_fare

    return float(real_total)

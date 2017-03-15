import argparse
import datetime
import logging

from logging.handlers import RotatingFileHandler


def allfridays(weekends):
    d = datetime.date.today()
    while d.weekday() != 4:
        d += datetime.timedelta(1)

    for x in range(weekends):
        yield d
        d += datetime.timedelta(days = 7)

def send_email(args, price):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.environ['WKND_FROM_EMAIL'], os.environ['WKND_PASSWORD'])
        msg_body = "Found {0}->{1} deal. ${2}. Leaving {3}. On Southwest.".format(args.depart, args.arrive, price, args.departure_date)
        msg = 'Subject: {0}\n\n{1}'.format("WKND Deal found.", msg_body)
        server.sendmail(os.environ['WKND_FROM_EMAIL'], os.environ['WKND_TO_EMAIL'], msg)
        server.quit()
    except:
        pass

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
        default=30,
        help="Refresh time period.")

    args = parser.parse_args()

    return args

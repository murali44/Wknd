
## Installation

1. Clone this repository.
2. Install required modules by `pip install -r requirements.txt`
3. Download [PhantomJS](http://phantomjs.org/download.html) and put phantomjs.exe in your Scripts folder (Windows) or /usr/bin folder (Mac/Linux).

## Usage

Scrapes the Southwest website according to the interval you set. For best results when using this program, I recommend setting the interval between 2-3 hours. A more frequent interval than that might be excessive. When the price goes under a certain amount, you will be notified via text message.

`--one-way # Optional. By default, a round trip is assumed.`

`--depart, -d [airport code] # The airport to depart from.`

`--arrive, -a [airport code] # The airport to arrive in.`

`--departure-date, -dd [date] # Date to leave.`

`--return-date, -rd [date] # Optional. Date to return.`

`--passengers, -p [adults] # Number of passengers.`

`--desired-total, -dt [dollars] # The total fare for one person should be under this amount (in dollars).`

`--interval, -i [minutes] # Optional. How often to scrape Southwest's website (in minutes). Default value = 3 hours.`

For more information on the available command line arguments use the following command.

`python app.py --help`

Sample commands:

**NOTE:** Error checking is non-existent, so make sure to enter the commands properly as specified below.

`$ python app.py --depart HOU --arrive MDW --departure-date 05/12 --return-date 05/14 --passengers 2 --desired-total 215 --interval 30`

`$ python app.py --one-way  --depart HOU --arrive MDW --departure-date 05/12 --passengers 2 --desired-total 215 --interval 30`

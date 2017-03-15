import datetime
import gcal
import sqlite3
conn = sqlite3.connect('wknd.db')
cur = conn.cursor()

def close():
    conn.commit()
    conn.close()

def delete_old():
    today = datetime.date.today().strftime('%m/%d/%Y')
    cur.execute('''DELETE FROM wknd
                   WHERE departure_date < ?
                ''', (today,))
    conn.commit()

def show_all():
    cur.execute('''SELECT * FROM wknd''')
    return cur.fetchall()

def add_item(origin, destination, departure_date, return_date, cost, gcalEventId):
    cur.execute('''INSERT INTO wknd
                   (origin, destination, price, departure_date,
                   return_date, gcalEventId)
                   VALUES (?, ?, ?, ?,
                   ?, ?)''', (origin, destination, cost, departure_date,
                   return_date, gcalEventId))
    conn.commit()

def update_price(destination, departure_date, cost, gcalEventId):
    cur.execute('''UPDATE wknd
                   SET price=?, gcalEventId=?
                   WHERE departure_date=?
                   AND destination=?
                   ''', (cost, gcalEventId, departure_date, destination))
    conn.commit()

def get_item(destination, departure_date):
    result = {}
    cur.execute('''SELECT price, gcalEventId FROM wknd
                   WHERE departure_date=?
                   AND destination=?''', (departure_date, destination))
    response = cur.fetchone()
    if response:
        result['price'] = response[0]
        result['gcalEventId'] = response[1]
    else:
        result = None
    return result

def update_db(args, price):
    response = get_item(args.arrive, args.departure_date)
    if response:
        if response['price'] != price:
            gcalEventId = gcal.update(args.arrive, price, args.departure_date,
                                      args.return_date, response['gcalEventId'])
            update_price(args.arrive,
                         args.departure_date,
                         price, gcalEventId)
    else:
        gcalEventId = gcal.create(args.arrive, price, args.departure_date,
                             args.return_date)
        add_item(args.depart,
                 args.arrive,
                 args.departure_date,
                 args.return_date, price,
                 gcalEventId)
    show_all()

import boto3

# Get the service resource.
DB = boto3.resource('dynamodb')
TBL = DB.Table('Wknd')

def add_item(origin, destination, departure_date, return_date, cost):
    TBL.put_item(
        Item={
            'Dest': destination,
            'DepDate': departure_date,
            'origin': origin,
            'RetDate': return_date,
            'Price': cost,
        }
    )

def update_price(destination, departure_date, cost):
    TBL.update_item(
        Key={
            'Dest': destination,
            'DepDate': departure_date
            },
        UpdateExpression='SET Price = :tixprice',
        ExpressionAttributeValues={':tixprice': cost}
        )

def get_item(destination, departure_date):
    item = TBL.get_item(
        Key={
            'Dest': destination,
            'DepDate': departure_date,
        }
    )
    return item

def update_db(args, price):
    response = get_item(args.arrive, args.departure_date)
    if 'Item' in response:
        if response['Item']['Price'] != price:
            db.update_price(args.arrive,
                            args.departure_date,
                            price)
    else:
        db.add_item(args.depart,
                    args.arrive,
                    args.departure_date,
                    args.return_date, price)

import boto3

# Get the service resource.
DB = boto3.resource('dynamodb')

# Create the DynamoDB table.
TABLE = DB.create_table(
    TableName='Wknd',
    KeySchema=[
        {
            'AttributeName': 'Dest',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'DepDate',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'Dest',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'DepDate',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 2,
        'WriteCapacityUnits': 2
    }
)

# Wait until the table exists.
TABLE.meta.client.get_waiter('table_exists').wait(TableName='Wknd')

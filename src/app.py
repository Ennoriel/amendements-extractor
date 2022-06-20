def lambda_handler(event, context):

    print('Hello les haricots!')

    return {
        "statusCode": 200,
        "body": "OK",
    }

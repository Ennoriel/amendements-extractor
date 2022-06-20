from get_new_amend import do_work

def lambda_handler(event, context):

    do_work()

    return {
        "statusCode": 200,
        "body": "OK",
    }

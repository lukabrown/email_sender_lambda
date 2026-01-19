import boto3
import json

def lambda_handler(event, context):

    try:
        ses = boto3.client('ses')
        data = json.loads(event.get('body', {}))
        subject = data.get('subject', 'No Subject')
        body = data.get('body', 'No Body Content')

        message_id = ses.send_email(
            Source='webform@luka-brown.com',
            Destination={'ToAddresses':['contact@luka-brown.com']},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )

        if message_id is None:
            return {
                'statusCode': 500,
                'body': json.dumps("Failed to send email, no message ID returned.")
            }

        return {
            'statusCode': 200,
            'body': json.dumps("Sucessfully sent email.")
        }
    except ses.exceptions.MessageRejected as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f"Email rejected: {str(e)}")
        }
    except ses.exceptions.MailFromDomainNotVerifiedException as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f"Domain not verified: {str(e)}")
        }
    except ses.exceptions.ConfigurationSetDoesNotExistException as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f"Configuration set does not exist: {str(e)}")
        }
    except ses.exceptions.ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f"Client error: {str(e)}")
        }
    except ses.exceptions.AccountSendingPausedException as e:
        return {
            'statusCode': 403,
            'body': json.dumps(f"Account sending paused: {str(e)}")
        }
    except ses.exceptions.LimitExceededException as e:
        return {
            'statusCode': 429,
            'body': json.dumps(f"Limit exceeded: {str(e)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error sending email: {str(e)}")
        }

import boto3
import json
import re

ses = boto3.client('ses')
MAX_SUBJECT_LENGTH = 120
MAX_BODY_LENGTH = 2000

def lambda_handler(event, context):
    print(event)
    try:
        if "body" not in event or not event["body"]:
            return {
                'statusCode': 400,
                'body': json.dumps("Missing body.")
            }

        subject = event.get('subject', 'No Subject')
        body = event['body']

        if len(subject) > MAX_SUBJECT_LENGTH:
            return {
                'statusCode': 413,
                'body': json.dumps("Subject too long.")
            }
        if len(body) > MAX_BODY_LENGTH:
            return {
                'statusCode': 413,
                'body': json.dumps("Body too long.")
            }

        subject = sanitize_text(subject)
        body = sanitize_text(body)

        ses.send_email(
            Source='webform@luka-brown.com',
            Destination={'ToAddresses':['contact@luka-brown.com']},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )

        print(json.dumps("Successfully sent email."))
        return {
            'statusCode': 200,
            'body': json.dumps("Sucessfully sent email.")
        }
    except ses.exceptions.MessageRejected as e:
        print(json.dumps(f"Email rejected: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Email rejected.")
        }
    except ses.exceptions.MailFromDomainNotVerifiedException as e:
        print(json.dumps(f"Domain not verified: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Domain not verified.")
        }
    except ses.exceptions.ConfigurationSetDoesNotExistException as e:
        print(json.dumps(f"Configuration set does not exist: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Configuration set does not exist.")
        }
    except ses.exceptions.ClientError as e:
        print(json.dumps(f"Client error: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Client error.")
        }
    except ses.exceptions.AccountSendingPausedException as e:
        print(json.dumps(f"Account sending paused: {str(e)}"))
        return {
            'statusCode': 403,
            'body': json.dumps("Account sending paused.")
        }
    except ses.exceptions.LimitExceededException as e:
        print(json.dumps(f"Limit exceeded: {str(e)}"))
        return {
            'statusCode': 429,
            'body': json.dumps("Limit exceeded.")
        }
    except Exception as e:
        print(json.dumps(f"Error sending email: {str(e)}"))
        return {
            'statusCode': 500,
            'body': json.dumps("Error sending email.")
        }

def sanitize_text(text):
    """Remove control characters and strip extra whitespace"""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\x00", "", text)
    return text.strip()

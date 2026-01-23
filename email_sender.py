import boto3
import json
import re
import os

SES = boto3.client('ses')
MAX_SUBJECT_LENGTH = 120
MAX_BODY_LENGTH = 2000

def lambda_handler(event, context):
    print(event)
    try:
        if len(event) > 2:
            return {
                'statusCode': 413,
                'body': json.dumps("Too many fields.")
            }

        subject = event['subject']
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

        SES.send_email(
            Source='webform@luka-brown.com',
            Destination={'ToAddresses':['contact@luka-brown.com']},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            },
            ConfigurationSetName=os.environ["config_set"]
        )

        print(json.dumps("Successfully sent email."))
        return {
            'statusCode': 200,
            'body': json.dumps("Sucessfully sent email.")
        }
    except SES.exceptions.MessageRejected as e:
        print(json.dumps(f"Email rejected: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Email rejected.")
        }
    except SES.exceptions.MailFromDomainNotVerifiedException as e:
        print(json.dumps(f"Domain not verified: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Domain not verified.")
        }
    except SES.exceptions.ConfigurationSetDoesNotExistException as e:
        print(json.dumps(f"Configuration set does not exist: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Configuration set does not exist.")
        }
    except SES.exceptions.ClientError as e:
        print(json.dumps(f"Client error: {str(e)}"))
        return {
            'statusCode': 400,
            'body': json.dumps("Client error.")
        }
    except SES.exceptions.AccountSendingPausedException as e:
        print(json.dumps(f"Account sending paused: {str(e)}"))
        return {
            'statusCode': 403,
            'body': json.dumps("Account sending paused.")
        }
    except SES.exceptions.LimitExceededException as e:
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

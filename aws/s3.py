import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = 'ml-ds-app'


def uploadFile(awsSession: boto3.Session, filePath: str, s3Key: str):
    s3 = awsSession.client('s3')
    s3.upload_file(Filename=filePath, Bucket=BUCKET_NAME, Key=s3Key)

    return


def generatePresignedUrl(awsSession: boto3.Session, s3Key: str, expiration: int = 600):
    s3 = awsSession.client('s3')

    try:
        response = s3.generate_presigned_url(
            'get_object', Params={'Bucket': BUCKET_NAME, 'Key': s3Key}, ExpiresIn=expiration
        )
    except ClientError as e:
        print(e)
        return None

    # The response contains the presigned URL
    return response

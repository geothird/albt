import boto3


class ApiGateway(object):
    def __init__(self):
        self.client = boto3.client('apigateway')

    def create(self):
        print(self)

    def deploy(self):
        print(self)

    def update(self):
        print(self)

    def __import__(self, body):
        # body=b'bytes'
        response = self.client.import_rest_api(
            failOnWarnings=False,
            body=body
        )
        print(response)
        return response

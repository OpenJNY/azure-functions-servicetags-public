import logging
import json
import os
import urllib.request
from dotenv import load_dotenv

import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from __app__.shared.blobutils import get_container, has_blob


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    headers = {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    # load envrionment
    load_dotenv()
    logging.info('[env]')
    logging.info(os.environ)

    try:

        # connect to a blob service
        connect_str = os.getenv('CONNECT_STR')
        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)
        logging.info("Connected to the blob storage.")

        # get container client
        container_name = os.getenv('CONTAINER_NAME')
        container_client = get_container(blob_service_client, container_name)
        logging.info("Got the container client.")
        logging.info(container_client)

        # find the latest blob
        blob_names = [blob.name for blob in container_client.list_blobs()]
        latest_blob = sorted(blob_names)[-1]
        logging.info(latest_blob)

        # get the blob client
        blob_client = container_client.get_blob_client(latest_blob)
        logging.info(blob_client.__str__())

        # download the blob
        download_stream = blob_client.download_blob()
        data = download_stream.readall()
        json_data = json.loads(data)
        logging.info('download data')

        return func.HttpResponse(json.dumps(json_data), headers=headers)

    except Exception as e:
        logging.error(e)
        return func.HttpResponse(json.dumps({'error': e}),
                                 headers=headers,
                                 status_code=400)

import datetime
import logging
import os
from bs4 import BeautifulSoup
import requests
import urllib.request

import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from __app__.shared.blobutils import get_container, has_blob

from dotenv import load_dotenv


def main(mytimer: func.TimerRequest) -> None:
    # log the date
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    load_dotenv()
    logging.info('[env]')
    logging.info(os.environ)

    try:
        public_dlpage = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
        response = requests.get(public_dlpage)
        response.encoding = response.apparent_encoding
        logging.info('Got download page.')

        # parse it
        soup = BeautifulSoup(response.text)

        # find the download link
        links = soup.find_all('a')
        target_link = list(
            filter(
                lambda l: l['href'].startswith('https://download.microsoft')
                and l.text == 'click here to download manually',
                links))[0]['href']
        logging.info('Found target_link:' + target_link)

        # filename (e.g. ServiceTags_Public_20191216)
        filename = target_link.split('/')[-1]

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

        # check if the json exists:
        if has_blob(container_client, filename):
            msg = "The blob file '{}' alreadly exsits in the container '{}'.".format(
                filename, container_name)
            logging.info(msg)
            return

        # create new file in the blob
        logging.info('Create a new blob with name ' + filename)
        blob_client = container_client.get_blob_client(blob=filename)

        # download json file
        logging.info('Download json file from url ' + target_link)
        with urllib.request.urlopen(target_link) as f:
            data = f.read().decode('utf-8')

        # upload
        logging.info("Upload to Azure Storage as blob:" + filename)
        blob_client.upload_blob(data)

        logging.log("Success.")
        return

    except Exception as e:
        logging.error('Error:')
        logging.error(e)
        return
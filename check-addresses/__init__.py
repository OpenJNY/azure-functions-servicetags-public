import logging
import json
import os
import urllib.request
import ipaddress

from dotenv import load_dotenv

import azure.functions as func
from azure.storage.blob import BlobServiceClient
from __app__.shared.blobutils import get_container, has_blob

_ALLOWED_HTTP_METHOD = "POST"


def write_http_response(status_code: int, body_dict: dict) -> func.HttpResponse:
    """ Write a HTTP response object with status code and body.
    """
    headers = {"Content-type": "application/json", "Access-Control-Allow-Origin": "*"}
    return func.HttpResponse(
        json.dumps(body_dict), headers=headers, status_code=status_code
    )


def ipv4_contains(address: str, prefix: str) -> bool:
    """ Return True if the address is in the prefix, False otherwise.
    """
    ipv4_addr = ipaddress.IPv4Address(address)
    ipv4_net = ipaddress.IPv4Network(prefix)
    return ipv4_addr in ipv4_net


def create_servicetags_dict(json_data: object, address: str) -> object:
    res = []
    for service in json_data["values"]:
        for prefix in service["properties"]["addressPrefixes"]:
            if ipv4_contains(address, prefix):
                res.append(
                    {
                        "name": service["name"],
                        "id": service["id"],
                        "changeNumber": service["properties"]["changeNumber"],
                        "region": service["properties"]["region"],
                        "platform": service["properties"]["platform"],
                        "systemService": service["properties"]["systemService"],
                        "addressPrefix": prefix,
                    }
                )

    return res


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function "check-ip-range" processed a request.')

    # Check HTTP method
    if req.method.lower() != _ALLOWED_HTTP_METHOD.lower():
        return write_http_response(
            405,
            {"message": "Only {} HTTP Method is allowed".format(_ALLOWED_HTTP_METHOD)},
        )

    # Parse parmeters
    try:
        req_body = req.get_json()
        addresses = req_body.get("addresses")
    except Exception as e:
        return write_http_response(
            400,
            {
                "message": 'Invalid HTTP request body. Make sure the body being a JSON, like {"addresses": ["1.1.1.1", "2.2.2.2"]}.'
            },
        )

    # Load envrionment
    load_dotenv()
    logging.info("[env]")
    logging.info(os.environ)

    try:
        # connect to blob service
        logging.info("Connect to blob storage with CONNECT_STR.")
        connect_str = os.getenv("CONNECT_STR")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # get container client
        logging.info("Get the container client.")
        container_name = os.getenv("CONTAINER_NAME")
        container_client = get_container(blob_service_client, container_name)
        logging.info(container_client.get_container_properties())

        # find the latest blob
        logging.info("Find the latest blob.")
        blob_names = [blob.name for blob in container_client.list_blobs()]
        latest_blob_name = sorted(blob_names)[-1]
        logging.info("latest_blob_name: " + latest_blob_name)

        # get the blob client
        logging.info("Get blob_client corresponds to the latest blob.")
        blob_client = container_client.get_blob_client(latest_blob_name)
        logging.info(blob_client.get_blob_properties())

        # download the blob
        logging.info("Download blob data.")
        download_stream = blob_client.download_blob()
        data = download_stream.readall()
        json_data = json.loads(data)

        # filter services
        results = []
        for address in addresses:
            results.append(
                {
                    "address": address,
                    "servicetags": create_servicetags_dict(json_data, address),
                }
            )
        logging.info(results)

        return write_http_response(
            200, {"message": "success", "json": latest_blob_name, "results": results}
        )

    except Exception as e:
        logging.error(e)
        return write_http_response(400, {"message": e})

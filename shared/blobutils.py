from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import logging


def get_container(blob_service_client: BlobServiceClient,
                  container_name: str) -> bool:
    """ Get a container client
    """
    logging.info('blob_service_client.list_containers()')
    logging.info(list(blob_service_client.list_containers()))

    try:
        _ = blob_service_client.get_container_client(container_name)
        container_client = blob_service_client.get_container_client(
            container_name)
    except:
        container_client = blob_service_client.create_container(container_name)
    return container_client


def has_blob(container_client: ContainerClient, blob_name: str) -> bool:
    """ Return True if the blob file exists in the container.
    """
    blobs = list(container_client.list_blobs())
    logging.info('container_client.list_blobs')
    logging.info(blobs)

    filtered_blobs = list(filter(lambda b: b['name'] == blob_name, blobs))
    logging.info('filtered_blobs')
    logging.info(filtered_blobs)

    return True if len(filtered_blobs) > 0 else False
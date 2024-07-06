from confluent_kafka import Consumer, KafkaError
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
import requests
import logging
import json
import signal
import sys
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_opensearch_client():
    conn_string = "http://localhost:9200"
    conn_uri = urlparse(conn_string)

    if conn_uri.username is None:
        # REST client without security
        rest_high_level_client = {
            "url": f"{conn_uri.scheme}://{conn_uri.hostname}:{conn_uri.port}"
        }
    else:
        # REST client with security
        auth = HTTPBasicAuth(conn_uri.username, conn_uri.password)
        rest_high_level_client = {
            "url": f"{conn_uri.scheme}://{conn_uri.hostname}:{conn_uri.port}",
            "auth": auth
        }

    return rest_high_level_client


def create_index_if_not_exists(client, index_name):
    url = f"{client['url']}/{index_name}"

    # Check if the index already exists
    response = requests.head(url, auth=client.get('auth'))

    if response.status_code == 404:
        # Index does not exist, create it
        response = requests.put(url, auth=client.get('auth'))

        if response.status_code == 200:
            logger.info(f"The index '{index_name}' has been created successfully.")
        else:
            logger.error(f"Failed to create the index '{index_name}'. Status code: {response.status_code}, Response: {response.text}")
    else:
        logger.info(f"The index '{index_name}' already exists.")


def extract_id(json_str):
    try:
        json_obj = json.loads(json_str)
        return json_obj['meta']['id']
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error extracting ID from JSON: {e}")
        return None


def bulk_index_documents(client, index_name, documents):
    url = f"{client['url']}/_bulk"
    headers = {"Content-Type": "application/x-ndjson"}

    bulk_data = ""
    for document in documents:
        document_id = extract_id(document)
        if document_id:
            action = json.dumps({"index": {"_index": index_name, "_id": document_id}})
            bulk_data += f"{action}\n{document}\n"
            logger.info(f"Prepared document with ID: {document_id} for bulk indexing.")

    if bulk_data:
        response = requests.post(url, auth=client.get('auth'), data=bulk_data, headers=headers)
        if response.status_code == 200:
            logger.info(f"Bulk indexed {len(documents)} documents successfully.")
        else:
            logger.error(f"Failed to bulk index documents. Status code: {response.status_code}, Response: {response.text}")
    else:
        logger.warning("No valid documents to index.")


def consume_messages(opensearch_client):
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'my-consumer-group',
        'auto.offset.reset': 'latest',
        'enable.auto.commit': False
    }

    consumer = Consumer(consumer_config)
    topic = 'wiki'
    consumer.subscribe([topic])

    running = True

    def shutdown_handler(sig, frame):
        nonlocal running
        logger.info("Detected a shutdown, let's exit by calling consumer.close()...")
        running = False

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        while running:
            msg = consumer.poll(timeout=3.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(msg.error())
                    break

            documents = [msg.value().decode('utf-8')]
            bulk_index_documents(opensearch_client, 'wikimedia', documents)

            consumer.commit()
            logger.info("Offsets have been committed.")

            time.sleep(1)  # Sleep for 1 second before consuming the next batch

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


def main():
    # Create an OpenSearch client
    client = create_opensearch_client()

    # Create the index on OpenSearch if it doesn't exist already
    create_index_if_not_exists(client, 'wikimedia')

    # Consume messages from Kafka and process them
    consume_messages(client)


if __name__ == "__main__":
    main()

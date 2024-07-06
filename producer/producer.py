from confluent_kafka.admin import AdminClient, NewTopic
import logging
import sseclient
import requests
from confluent_kafka import Producer
from event_handler import WikimediaChangeHandler

# Configuration properties
BOOTSTRAP_SERVERS = 'kafka1:9093,kafka2:9095,kafka3:9097'  # Update bootstrap servers here
TOPIC = 'wiki'
URL = 'https://stream.wikimedia.org/v2/stream/recentchange'

def configure_logging():
    """Configures the logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [%(message)s]',
        handlers=[
            logging.FileHandler("wikimedia_kafka_producer.log"),
            logging.StreamHandler()
        ]
    )


def create_kafka_producer():
    """Creates and returns a Kafka producer instance."""
    conf = {
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'linger.ms': 20,
        'batch.size': 32 * 1024,
        'compression.type': 'snappy'
    }
    return Producer(conf)


def create_topic(admin_client):
    """Creates the Kafka topic if it doesn't exist."""
    topics = [NewTopic(topic=TOPIC, num_partitions=3, replication_factor=2)]
    fs = admin_client.create_topics(topics)
    for topic, f in fs.items():
        try:
            f.result()  # Wait for operation to finish
            logging.info(f"Topic '{topic}' created successfully.")
        except Exception as e:
            logging.error(f"Failed to create topic '{topic}': {e}")


def get_wikimedia_changes(handler: WikimediaChangeHandler):
    """Consumes real-time Wikimedia recent changes."""
    logging.info(f"Connecting to Wikimedia stream: {URL}")
    response = requests.get(URL, stream=True)
    print("Response Status Code:", response.status_code)  # Add this line
    handler.on_open()
    try:
        client = sseclient.SSEClient(URL)  # Pass URL directly
        for event in client:
            if event.event == 'message':
                handler.on_message(event, event)
    finally:
        handler.on_closed()


def main():
    """Main function to set up and run the Kafka producer and event handler."""
    configure_logging()
    logging.info("Starting Wikimedia Kafka Producer")
    producer = create_kafka_producer()
    
    # Create an AdminClient instance
    admin_client = AdminClient({'bootstrap.servers': BOOTSTRAP_SERVERS})
    
    # Create the topic if it doesn't exist
    create_topic(admin_client)
    
    handler = WikimediaChangeHandler(kafka_producer=producer, topic=TOPIC)
    get_wikimedia_changes(handler)


if __name__ == '__main__':
    main()

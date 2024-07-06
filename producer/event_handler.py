import logging
import json
from confluent_kafka import Producer

class WikimediaChangeHandler:
    def __init__(self, kafka_producer: Producer, topic: str):
        self.kafka_producer = kafka_producer
        self.topic = topic
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

    def on_open(self):
        """Handle the opening of the event stream (if needed)."""
        self.log.info("Opened connection to Wikimedia stream.")

    def on_closed(self):
        """Handle the closing of the event stream."""
        self.kafka_producer.flush()
        self.kafka_producer.close()
        self.log.info("Closed connection to Wikimedia stream and Kafka producer.")


    def on_message(self, event, message_event):
        """Handle an incoming message event."""
        try:
            # Check if message_event.data is not empty
            if message_event.data.strip():
                data = json.loads(message_event.data)
                key = str(data.get('id', ''))
                value = json.dumps(data)
                self.kafka_producer.produce(self.topic, key=key, value=value, callback=self.delivery_report)
                self.kafka_producer.poll(0)
            else:
                self.log.warning("Received empty message data, skipping...")

        except json.JSONDecodeError as e:
            self.log.error(f"Failed to decode JSON: {e}")


    def delivery_report(self, err, msg):
        """Delivery report callback called once a message is produced."""
        if err is not None:
            self.log.error(f"Message delivery failed: {err}")
        else:
            self.log.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
import pika
import time

from budget_calculator.main import budget_calc
from encoder import encoder
from utils.token import is_user_token_valid
from utils import environment

class CalcInputConsumer(object):
    EXCHANGE = environment.VARIABLES['BUDGET_CALCS']
    EXCHANGE_TYPE = 'direct'
    QUEUE = environment.VARIABLES['CALC_INPUTS']
    ROUTING_KEY = environment.VARIABLES['CALC_INPUTS']

    def __init__(self, amqp_url, virtual_host, credentials):
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self.virtual_host = virtual_host
        self.credentials = credentials
        self._isConnected = False

    def connect(self):
        print('Connecting to %s', self._url)
        return pika.SelectConnection(pika.ConnectionParameters(self._url,
                                                               virtual_host=self.virtual_host,
                                                               credentials=self.credentials),
                                                               self.on_connection_open,
                                                               stop_ioloop_on_close=False)

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        print('Closing connection')
        self._connection.close()

    def add_on_connection_close_callback(self):
        print('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        self._connection.ioloop.stop()
        self._isConnected = False

        if not self._closing:
            print('Connection closed, reconnecting now...', reply_code, reply_text)
            self.reconnect()

    def on_connection_open(self, unused_connection):
        print('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def reconnect(self):
        while not self._isConnected:
            try:
                self.run()
            except Exception:
                print('Reconnection failed.. trying again..')
                self._isConnected = False
                time.sleep(10)

    def add_on_channel_close_callback(self):
        print('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        print('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        print('Channel opened')
        self._channel = channel
        self._channel.basic_qos(prefetch_count=1)
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def setup_exchange(self, exchange_name):
        print('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        print('Exchange declared')
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        print('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name, durable=True)

    def on_queue_declareok(self, method_frame):
        print('Binding %s to %s with %s',
                    self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.ROUTING_KEY)

    def add_on_cancel_callback(self):
        print('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        print('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        print('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body
        """
        print('Received message # %s from %s: %s', basic_deliver.delivery_tag, properties.app_id, body)

        message = encoder.deserializer(body)

        if message.token and is_user_token_valid(message.token):
            budget_calc(message.data)

        self.acknowledge_message(basic_deliver.delivery_tag)

    def on_cancelok(self, unused_frame):
        print('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def stop_consuming(self):
        if self._channel:
            print('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self):
        print('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)

    def on_bindok(self, unused_frame):
        print('Queue bound')
        self.start_consuming()

    def close_channel(self):
        print('Closing the channel')
        self._channel.close()

    def open_channel(self):
        print('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()
        self._isConnected = True

    def stop(self):
        print('Stopping')
        self._closing = True
        self.stop_consuming()
        print('Stopped')


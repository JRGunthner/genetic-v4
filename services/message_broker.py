import pika
from utils import environment


def log_calc_status(message):
    virtual_host = environment.VARIABLES["VIRTUAL_HOST"]
    virtual_passwd = environment.VARIABLES["VIRTUAL_PASSWD"]
    credentials = pika.PlainCredentials(virtual_host, virtual_passwd)
    amqp_url = environment.VARIABLES["AMQP_URL"]
    connection = pika.BlockingConnection(pika.ConnectionParameters(amqp_url,
                                                                   virtual_host=virtual_host,
                                                                   credentials=credentials))

    channel = connection.channel()
    channel.exchange_declare(exchange=environment.VARIABLES['BUDGET_CALCS'],exchange_type='direct')
    channel.queue_declare(queue=environment.VARIABLES['CALC_STATUS'], durable=True)
    channel.queue_bind(exchange=environment.VARIABLES['BUDGET_CALCS'],queue=environment.VARIABLES['CALC_STATUS'])
    channel.basic_publish(exchange=environment.VARIABLES['BUDGET_CALCS'],
                          routing_key=environment.VARIABLES['CALC_STATUS'],
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,
                              content_type="application/json"
                          ))

    connection.close()

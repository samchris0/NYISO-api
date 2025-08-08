import logging

def ConfigureLogging(app):
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        filename="log.log",
        filemode='w'
    )
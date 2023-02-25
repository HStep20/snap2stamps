import logging


def get_log_handler(log_file: str) -> logging.Logger:
    """
    Parameters:
        - log_file: The File Path to the output log file

    Returns:
        - app_log: the log handler to write logs to file and the console
    """
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s(%(lineno)d) - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    # Setup File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    # Setup Stream Handler (i.e. console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)

    # Get our logger
    app_log = logging.getLogger("root")
    app_log.setLevel(logging.INFO)

    # Add both Handlers
    app_log.addHandler(file_handler)
    app_log.addHandler(stream_handler)
    return app_log

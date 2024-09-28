import logging

def setup_logging(args):
    # Create the main logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if args.verbose >= 3 else logging.INFO)

    # Create console handler (no timestamps, just messages)
    console_handler = logging.StreamHandler()
    if args.verbose >= 3:
        console_handler.setLevel(logging.DEBUG)
    elif args.verbose == 2:
        console_handler.setLevel(logging.WARNING)
    elif args.verbose == 1:
        console_handler.setLevel(logging.ERROR)
    else:
        console_handler.setLevel(logging.CRITICAL)

    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Create file handler (with timestamps)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add handlers to the main logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Suppress logs from third-party libraries (like whois) from showing in the console
    # Create a separate file handler for third-party logs
    third_party_file_handler = logging.FileHandler('app.log')
    third_party_file_handler.setLevel(logging.ERROR)
    third_party_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [third-party] - %(message)s')
    third_party_file_handler.setFormatter(third_party_formatter)

    # Capture third-party module logs (such as whois and dns) and log to file only
    whois_logger = logging.getLogger("whois")
    whois_logger.setLevel(logging.ERROR)
    whois_logger.propagate = False  # Prevent logs from showing in the console
    whois_logger.handlers = []  # Clear default handlers
    whois_logger.addHandler(third_party_file_handler)

    dns_logger = logging.getLogger("dns")
    dns_logger.setLevel(logging.ERROR)
    dns_logger.propagate = False  # Prevent logs from showing in the console
    dns_logger.handlers = []  # Clear default handlers
    dns_logger.addHandler(third_party_file_handler)

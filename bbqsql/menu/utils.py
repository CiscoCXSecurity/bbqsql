# file: utils.py

from urlparse import urlparse
import socket

def validate_url(url):
    #parse the url
    parsed_url = urlparse(url)
    #check if the hostname/ip is valid
    try:
        socket.gethostbyname(parsed_url.netloc)
        host_valid = True
    except socket.error:
        host_valid = False
    return parsed_url.scheme in ['http','https'] and host_valid
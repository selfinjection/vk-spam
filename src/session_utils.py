from urllib.parse import urlparse

# TODO: replace with re expr > [ownerid, postid]
def wall_link_parse(link: str):
    return urlparse(link).path[5:].split('_')

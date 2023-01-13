from urllib.parse import urlparse

### TODO: replace with a regular expression 
### https://vk.com/wall-42446186_33429 -> [-42446186, 33429]
def wall_link_parse(link: str):
    return urlparse(link).path[5:].split('_')

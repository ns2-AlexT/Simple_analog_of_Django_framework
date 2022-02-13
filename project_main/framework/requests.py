import quopri


def parse_request_get_or_post(request: str):
    # print(f'Parsing {request}')
    result = {}
    get_params = request.split('&')
    for item in get_params:
        k, v = item.split('=')
        result[k] = v
    return result


class GetRequest:
    @staticmethod
    def parse_get_request(get_request):
        if get_request['QUERY_STRING']:
            return parse_request_get_or_post(get_request['QUERY_STRING'])


class PostRequest:
    @staticmethod
    def get_data_request(post_request) -> bytes:
        len_post_request = int(post_request['CONTENT_LENGTH']) if post_request['CONTENT_LENGTH'] else 0
        data_of_request = post_request['wsgi.input'].read(len_post_request) if len_post_request > 0 else b''
        return data_of_request

    @staticmethod
    def parse_post_request(post_request: bytes) -> dict:
        if post_request:
            return parse_request_get_or_post(post_request.decode(encoding='utf-8'))

    @staticmethod
    def post_data_request(post_request):
        post_data_request = PostRequest.get_data_request(post_request)
        return PostRequest.parse_post_request(post_data_request)

    """
    Decoding post request in case of Cyrillic
    """

    @staticmethod
    def decode_post_data(post_request):
        decode_request_dict = {}
        for k, v in post_request.items():
            val = bytes(v.replace('%', '=').replace('+', ''), 'UTF-8')
            val_decode = quopri.decodestring(val).decode('UTF-8')
            decode_request_dict[k] = val_decode
        return decode_request_dict

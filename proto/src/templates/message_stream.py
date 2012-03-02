from binary_tools import to_bin

class MessageStream(object):

    def __init__(self, stream, protocol):
        self._cache = []
        self._stream = stream
        self._protocol = protocol

    def get(self, message_template, timeout=None, header_filter=None):
        header_fields = message_template.header_parameters
        print "*TRACE* Get message with params %s" % header_fields
        msg = self._get_from_cache(message_template, header_fields, header_filter)
        if msg:
            print "*TRACE* Cache hit. Cache currently has %s messages" % len(self._cache)
            return msg
        while True:
            header, pdu_bytes = self._protocol.read(self._stream, timeout=timeout)
            if self._matches(header, header_fields, header_filter):
                return self._to_msg(message_template, header, pdu_bytes)
            else:
                self._cache.append((header, pdu_bytes))

    def _get_from_cache(self, template, fields, header_filter):
        index = 0
        while index < len(self._cache):
            header, pdu = self._cache[index]
            if self._matches(header, fields, header_filter):
                self._cache.pop(index)
                return self._to_msg(template, header, pdu)
        return None

    def _to_msg(self, template, header, pdu_bytes):
        msg = template.decode(pdu_bytes, parent=header)
        msg._add_header(header)
        return msg

    def _matches(self, header, fields, header_filter):
        if header_filter:
            if header_filter not in fields:
                raise AssertionError('Trying to filter messages by header field %s, but no value has been set for %s' %
                                     (header_filter, header_filter))
            if header[header_filter].bytes  != to_bin(fields[header_filter]):
                return False
        return True

    def empty(self):
        self.cache = []
        self._stream.empty()

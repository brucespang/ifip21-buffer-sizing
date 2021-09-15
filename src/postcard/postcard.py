import struct

class Postcard():
    def __init__(self, buf):
        parsed = struct.unpack("!BBB4s4sHHIIIII", buf[0:35])
        self.unaligned_field_1 = parsed[0]
        self.unaligned_field_2 = parsed[1]
        self.unaligned_field_3 = parsed[2]
        self.ipv4_src_addr = '.'.join(map(str, parsed[3]))
        self.ipv4_dst_addr = '.'.join(map(str, parsed[4]))
        self.src_port = parsed[5]
        self.dst_port = parsed[6]
        self.seq_no = parsed[7]
        self.ack_no = parsed[8]
        self.queue_depth = parsed[9]
        self.timestamp = parsed[10]
        self.switch_id = parsed[11]
        
        # TODO: parse the unaligned fields
        self.is_mirrored = (self.unaligned_field_1 & 0b10000000) >> 7
        self.was_dropped = (self.unaligned_field_1 & 0b01110000) >> 4
        self.original_egress_port = ((self.unaligned_field_1 & 0b00000011) << 7) + ((self.unaligned_field_2 & 0b11111110) >> 1)
        self.original_ingress_port = ((self.unaligned_field_2 & 0b00000001) << 8) + (self.unaligned_field_3 & 0b11111110)

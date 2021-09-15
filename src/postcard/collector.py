import socket
import socketserver
import click
import sys
from postcard import Postcard
import postcard_logger
import time
from threading import Thread

class PostcardServer(Thread):
    def __init__(self, host, port, thread_id):
        Thread.__init__(self)

        self.host = host
        self.port = port
        self.thread_id = thread_id
        self.num_received = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    def run(self):
        self.sock.bind((self.host, self.port))
        
        print("[{}] listening on {}:{}".format(self.thread_id, self.host, self.port),
              file=sys.stderr)

        while True:
            data, addr = self.sock.recvfrom(128)
            self.num_received += 1
            postcard = Postcard(data)
            postcard_logger.log(
                thread_id=self.thread_id,
            
                switch_id=postcard.switch_id,

                egress_port=postcard.original_egress_port,
                ingress_port=postcard.original_ingress_port,

                ipv4_src_addr=postcard.ipv4_src_addr,
                ipv4_dst_addr=postcard.ipv4_dst_addr,
            
                src_port=postcard.src_port,
                dst_port=postcard.dst_port,

                seq_no=postcard.seq_no,
                ack_no=postcard.ack_no,

                postcard_timestamp=postcard.timestamp,
                queue_depth_cells=postcard.queue_depth,

                was_dropped=postcard.was_dropped
            )

    
@click.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=4444)
@click.option("--threads", default=8, type=int)
def main(host, port, threads):
    servers = []
    for thread_id in range(threads):
        s = PostcardServer(host, port, thread_id)
        s.start()
        servers.append(s)

    last_received = [0 for _ in servers]
    while True:
        received = [0 for _ in servers]
        for i,server in enumerate(servers):
            received[i] = server.num_received

        for i,r,l in zip(range(threads), received, last_received):
            print(i, r - l, file=sys.stderr)

        last_received = received
        time.sleep(1)

if __name__ == "__main__":
    main()


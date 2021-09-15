#include <assert.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <netdb.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

typedef struct __attribute__((packed)) {
  uint8_t unaligned_field_1;
  uint8_t unaligned_field_2;
  uint8_t unaligned_field_3;
  struct in_addr ipv4_src_addr;
  struct in_addr ipv4_dst_addr;
  uint16_t src_port;
  uint16_t dst_port;
  uint32_t seq_no;
  uint32_t ack_no;
  uint32_t queue_depth;
  uint32_t timestamp;
  uint32_t switch_id;
} postcard_hdr;

static uint64_t num_received;

__attribute__((noreturn)) static void* postcard_collector() {
  num_received = 0;
  
  int sock = socket(AF_INET, SOCK_DGRAM, 0);
  if (sock < 0) {
    perror("socket");
    exit(1);
  }

  int opt = 1;
  setsockopt(sock, SOL_SOCKET, SO_REUSEPORT, (const void *)&opt , sizeof(int));

  struct sockaddr_in addr;
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  addr.sin_port = htons(4444);

  if (bind(sock, (struct sockaddr *) &addr, sizeof(addr)) < 0) {
    perror("bind");
    exit(1);
  }

  char buf[1024];
  struct sockaddr_in client;
  uint32_t client_len = sizeof(client);
  while (true) {
    ssize_t received = recvfrom(sock, buf, 1024, 0, (struct sockaddr*) &client, &client_len);
    if (received < 0) {
      perror("recvfrom");
      exit(1);
    }
    assert(received == 43);
    
    struct timespec time;
    if (clock_gettime(CLOCK_MONOTONIC_RAW, &time) < 0) {
      perror("clock_gettime");
      exit(1);
    }

    num_received += 1;
    
    postcard_hdr* postcard = (postcard_hdr*)buf;
    uint8_t was_dropped = (postcard->unaligned_field_1 & 0b01110000) >> 4;
    uint32_t egress_port = ((uint32_t)(postcard->unaligned_field_1 & 0b00000011) << 7) + ((uint32_t)(postcard->unaligned_field_2 & 0b11111110) >> 1);
    uint32_t ingress_port = ((uint32_t)(postcard->unaligned_field_2 & 0b00000001) << 8) + (uint32_t)(postcard->unaligned_field_3 & 0b11111110);

    // not converting ipv4 addrs since inet_ntoa requires network byte order.
    postcard->src_port = ntohs(postcard->src_port);
    postcard->dst_port = ntohs(postcard->dst_port);
    postcard->seq_no = ntohl(postcard->seq_no);
    postcard->ack_no = ntohl(postcard->ack_no);
    postcard->queue_depth = ntohl(postcard->queue_depth);
    postcard->timestamp = ntohl(postcard->timestamp);
    postcard->switch_id = ntohl(postcard->switch_id);

    printf("%ld.%09ld: postcard: ", time.tv_sec, time.tv_nsec);
    printf("ipv4_src_addr=%s ", inet_ntoa(postcard->ipv4_src_addr));
    printf("ipv4_dst_addr=%s ", inet_ntoa(postcard->ipv4_dst_addr));
    printf("src_port=%d ", postcard->src_port);
    printf("dst_port=%u ", postcard->dst_port);
    printf("seq_no=%u ", postcard->seq_no);
    printf("ack_no=%u ", postcard->ack_no);
    printf("queue_depth_cells=%u ", postcard->queue_depth);
    printf("postcard_timestamp=%u ", postcard->timestamp);
    printf("switch_id=%u ", postcard->switch_id);
    printf("was_dropped=%u ", was_dropped);
    printf("egress_port=%u ", egress_port);
    printf("ingress_port=%u\n", ingress_port);
    fflush(stdout);
  }
}

int main() {
  pthread_t collector;
  if (pthread_create(&collector, NULL, postcard_collector, NULL) < 0) {
    perror("pthread_create");
    exit(1);
  }

  uint64_t last_received = 0;
  while (true) {
    fprintf(stderr, "rate: %lu postcards/sec\n", num_received - last_received);
    last_received = num_received;
    
    sleep(1);
  }
}

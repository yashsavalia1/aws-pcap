#include <pcap.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <net/ethernet.h>
#include <signal.h>

pcap_t *handle;

struct capture_stats {
    unsigned int ps_recv;
    unsigned int ps_ifdrop;
    unsigned int ps_drop;
};

void sigintHandler(int sig) {
    signal(sig, SIG_IGN);
    printf("\nSIGINT - Breaking loop\n");
    pcap_breakloop(handle);
}

void packet_handler(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    struct ether_header *eth_header = (struct ether_header *)packet;
    struct ip *ip_header = (struct ip *)(packet + sizeof(struct ether_header));
    int ip_header_length = ip_header->ip_hl * 4;

    struct sockaddr_in source, dest;
    memset(&source, 0, sizeof(source));
    source.sin_addr.s_addr = ip_header->ip_src.s_addr;

    memset(&dest, 0, sizeof(dest));
    dest.sin_addr.s_addr = ip_header->ip_dst.s_addr;

    printf("{\"src_ip\": \"%s\", \"dst_ip\": \"%s\", \"protocol\": %d", inet_ntoa(source.sin_addr), inet_ntoa(dest.sin_addr), ip_header->ip_p);

    if (ip_header->ip_p == IPPROTO_TCP) {
        struct tcphdr *tcp_header = (struct tcphdr *)(packet + sizeof(struct ether_header) + ip_header_length);
        printf(", \"src_port\": %d, \"dst_port\": %d", ntohs(tcp_header->th_sport), ntohs(tcp_header->th_dport));
    } else if (ip_header->ip_p == IPPROTO_UDP) {
        struct udphdr *udp_header = (struct udphdr *)(packet + sizeof(struct ether_header) + ip_header_length);
        printf(", \"src_port\": %d, \"dst_port\": %d", ntohs(udp_header->uh_sport), ntohs(udp_header->uh_dport));
    }
    printf(", \"raw_data\": \"");
    for (int i = 0; i < header->len; i++) {
        printf("%02x", packet[i]);
    }
    printf("\"");
    printf("}\n");

    struct capture_stats *stats = (struct capture_stats *)args;
    stats->ps_recv++;
}

int main(int argc, char *argv[]) {
    signal(SIGINT, sigintHandler);
    
    char errbuf[PCAP_ERRBUF_SIZE];
    int timeout_limit = 1000;

    pcap_if_t *alldevs, *dev;
    char *dev_name;

    if (pcap_findalldevs(&alldevs, errbuf) == -1) {
        fprintf(stderr, "Error finding devices: %s\n", errbuf);
        return 1;
    }

    if (alldevs == NULL) {
        fprintf(stderr, "No network devices found\n");
        return 1;
    }

    dev = alldevs;
    dev_name = dev->name;

    handle = pcap_open_live(dev_name, BUFSIZ, 1, timeout_limit, errbuf);
    if (handle == NULL) {
        fprintf(stderr, "Couldn't open device %s: %s\n", dev_name, errbuf);
        pcap_freealldevs(alldevs);
        return 2;
    }

    struct capture_stats stats = {0};
    pcap_loop(handle, -1, packet_handler, (u_char *)&stats);

    struct pcap_stat captureStats;
    pcap_stats(handle, &captureStats);


    printf("%d Packets received\n", stats.ps_recv);
    printf("%d Dropped by interface\n", captureStats.ps_ifdrop);
    printf("%d Dropped by kernel\n", captureStats.ps_drop);

    pcap_close(handle);
    pcap_freealldevs(alldevs);
    return 0;
}

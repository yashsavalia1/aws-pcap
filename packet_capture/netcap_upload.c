#include "netcap_upload.h"
#include "netcap.h"
#include "netparse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    capture(packet_handler);
    return 0;
}

void packet_handler(u_char *fileDumper, const struct pcap_pkthdr *header,
                    const u_char *body) {

    // pcap_dump(fileDumper, header, body);
    linux_linklayer_sll_t linkLayerInfo = {};
    ip_header_t ipInfo = {};
    tcp_header_t tcpInfo = {};
    udp_header_t udpInfo = {};
    char fix_unrecognised[1024];
    fix_payload_t fixInfo = {.unrecognised = fix_unrecognised};

    parsePacket(1, header, body, &linkLayerInfo, &ipInfo, &tcpInfo, &udpInfo,
                &fixInfo);

    printf("}}\n");
    //  printf("Packet at %lu.%lu - Capture length: %d, Total length: %d\n",
    //         header->ts.tv_sec, header->ts.tv_usec, header->caplen,
    //         header->len);
}

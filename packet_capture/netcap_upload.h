#ifndef NETCAP_UPLOAD_H
#define NETCAP_UPLOAD_H
#include "netparse.h"
#include <pcap/pcap.h>

void packet_handler(u_char *fileDumper, const struct pcap_pkthdr *header,
                    const u_char *body);
#endif

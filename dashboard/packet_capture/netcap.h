#ifndef NETCAP_H
#define NETCAP_H
#include <pcap/pcap.h>

int printDevices();
int captureNPackets(char *device, int numPackets);
int capture(pcap_handler packet_hander);
void sigintHandler(int sig);
void packet_handler(u_char *fileDumper, const struct pcap_pkthdr *header,
                    const u_char *body);

#endif

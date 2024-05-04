#ifndef NETCAP_H
#define NETCAP_H
#include <pcap/pcap.h>

int printDevices();
int captureNPackets(char *device, int numPackets);
int capture(pcap_handler packet_hander);
void sigintHandler(int sig);

#endif

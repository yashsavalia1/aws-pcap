#include "netcap.h"
#include <errno.h>
#include <pcap.h> /* GIMME a libpcap plz! */
#include <pcap/pcap.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <string.h>
#include "netparse.h"

pcap_t *handle;

int printDevices() {
    pcap_if_t *alldevices; /* name of the devices to use */
    char errbuf[PCAP_ERRBUF_SIZE];

    /* ask pcap to find a valid device for use to sniff on */
    int devsts = pcap_findalldevs(&alldevices, errbuf);

    /* error checking */
    if (alldevices == NULL || devsts != 0) {
        printf("%s\n", errbuf);
        exit(1);
    }

    /* print out device name */
    printf("Available Devices:\n");
    for (pcap_if_t *dev = alldevices; dev; dev = dev->next) {
        printf("    - %s\n", dev->name);
    }

    pcap_freealldevs(alldevices);

    return 0;
}

int captureNPackets(char *device, int numPackets) {
    char errbuf[PCAP_ERRBUF_SIZE]; /* PCAP error buffer */
    pcap_t *handle;                /* capture handle */
    const u_char *packet;
    struct pcap_pkthdr packet_header;
    int timeout_limit = 1;
    int successfulCaptures = 0;

    /* Open device for live capture */
    handle = pcap_open_live(device, BUFSIZ, numPackets, timeout_limit, errbuf);

    /* Check if device open successful */
    if (handle == NULL) {
        printf("pcap_open_live err: %s\n", errbuf);
        exit(1);
    }

    /* Loop to capture n packets */
    for (int i = 0; i < numPackets; i++) {
        packet = pcap_next(handle, &packet_header);
        if (packet == NULL) {
            printf("No packet received within timeout\n");
            continue;
        }
        printf("Packet #%d - Capture length: %d, Total length: %d\n", i,
               packet_header.caplen, packet_header.len);
        successfulCaptures++;
    }

    printf("Successfully captured %d packets\n", successfulCaptures);

    return 0;
}

void verify(int status, pcap_t *handle, char *msg) {
    if (status < 0) {
        pcap_perror(handle, msg);
        exit(1);
    }
}

int capture(pcap_handler packet_handler) {
    signal(SIGINT, sigintHandler);
    /* CAPTURE SETTINGS */
    /* interface to which the capture should listen to */
    const char *INTERFACE = "any";

    /* first bytes should the packet data be captured, 65535 is enough for full
     * packet data capture */
    const int SNAPSHOT_LENGTH = 65535;

    /* if not 0, capture data that aren't  directed to the interface as well */
    const int PROMISCUOUS_MODE = 0;

    /* if not 0, capture full frame from packets not directed to the interface.
     * WARNING: WILL DISCONNECT INTERFACE FROM NETWORK */
    const int RF_MONITOR_MODE = 0;

    /* timeout (in ms) for when packets aren't delivered  when they arrive */
    const int TIMEOUT = 1;

    /* if not 0, immediate mode will be set, and packets are captured on arrival
     * without buffering (may drop packets on capture) */
    const int IMMEDIATE_MODE = 0;

    /* buffer size for incoming packets */
    //     const int BUFFER_SIZE = BUFSIZ;

    /* timestamp type */
    const int TIMESTAMP_TYPE = PCAP_TSTAMP_HOST_HIPREC;

    /* timestamp resolution when capturing packets */
    const int TIMESTAMP_PRECISION = PCAP_TSTAMP_PRECISION_MICRO;

    /* capturing filter to prevent copying "uninteresting" packets from kernal
     * mode to user mode */
    const char *FILTER = "not (arp or (ip proto \\icmp) or (port 123) or (port 22))";

    struct bpf_program filterProgram;
    pcap_t *filterHandle;
    int datalink_type;
    char errbuf[PCAP_ERRBUF_SIZE];
    int status;
    struct pcap_stat captureStats;
    pcap_dumper_t *fileDumper;

    /* Check if handle creation succeeded */
    handle = pcap_create(INTERFACE, errbuf);
    if (handle == NULL) {
        printf("Handle creation failed: %s\n", errbuf);
        exit(1);
    }

    /* Applying capture settings */
    status = pcap_set_snaplen(handle, SNAPSHOT_LENGTH);
    verify(status, handle, "Setting snaplen failed: ");

    status = pcap_set_promisc(handle, PROMISCUOUS_MODE);
    verify(status, handle, "Setting promsc failed: ");

    status = pcap_set_rfmon(handle, RF_MONITOR_MODE);
    verify(status, handle, "Setting rfmon failed: ");

    status = pcap_set_timeout(handle, TIMEOUT);
    verify(status, handle, "Setting timeout failed: ");

    status = pcap_set_immediate_mode(handle, IMMEDIATE_MODE);
    verify(status, handle, "Setting immediate mode failed: ");

    //    status = pcap_set_buffer_size(handle, BUFFER_SIZE);
    //    verify(status, handle, "Setting buffer size failed: ");

    status = pcap_set_tstamp_type(handle, TIMESTAMP_TYPE);
    verify(status, handle, "Setting timestamp type failed: ");

    status = pcap_set_tstamp_precision(handle, TIMESTAMP_PRECISION);
    printf("%d\n", status);
    verify(status, handle, "Setting timestamp precision failed: ");

    pcap_activate(handle);

    /* Compiling filter program */
    datalink_type = pcap_datalink(handle);
    verify(datalink_type, handle, "Error retrieving data link type: ");

    filterHandle = pcap_open_dead(datalink_type, SNAPSHOT_LENGTH);
    status = pcap_compile(filterHandle, &filterProgram, FILTER, 0,
                          PCAP_NETMASK_UNKNOWN);
    verify(status, filterHandle, "Filter compilation failed: ");

    /* Setting filter */
    status = pcap_setfilter(handle, &filterProgram);
    verify(status, handle, "Setting filter failed: ");
    pcap_freecode(&filterProgram);

    /* Setup pcap saving */
    fileDumper = pcap_dump_open(handle, "output_capture.pcap");
    if (fileDumper == NULL) {
        pcap_perror(handle, "Failed to create dumper: ");
    }

    pcap_loop(handle, 0, packet_handler, (u_char *)fileDumper);

    pcap_dump_close(fileDumper);

    status = pcap_stats(handle, &captureStats);
    verify(status, handle, "Cannot acquire capture statistics: ");
    printf("%d Packets received\n", captureStats.ps_recv);
    printf("%d Dropped by kernal\n", captureStats.ps_drop);
    printf("%d Dropped by interface\n", captureStats.ps_ifdrop);

    pcap_close(handle);
    return 0;
}

void sigintHandler(int sig) {
    signal(sig, SIG_IGN);
    printf("\nSIGINT - Breaking loop\n");
    pcap_breakloop(handle);
}

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

    int result = parsePacket(1, header, body, &linkLayerInfo, &ipInfo, &tcpInfo, &udpInfo,
                &fixInfo);
    if (result != -1){
        printf("}}\n");
    }
    fflush(stdout);
    //  printf("Packet at %lu.%lu - Capture length: %d, Total length: %d\n",
    //         header->ts.tv_sec, header->ts.tv_usec, header->caplen,
    //         header->len);
}

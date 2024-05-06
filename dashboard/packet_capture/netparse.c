#ifndef _GNU_SOURCE
#define _GNU_SOURCE 1
#endif
#include "netparse.h"
#include <netinet/in.h>
#include <pcap/pcap.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

unsigned long long parseValue(const u_char *buf, int size) {
    unsigned long ret = 0;
    for (int i = 0; i < size; i++) {
        ret += (unsigned long long)buf[i] << (8ULL * (size - i - 1));
    }
    return ret;
}

int parsePacket(const int printJson, const struct pcap_pkthdr *header,
                const u_char *packet, linux_linklayer_sll_t *linklayer,
                ip_header_t *ip, tcp_header_t *tcp, udp_header_t *udp,
                fix_payload_t *fix) {

    printf("{\"tstamp_sec\": "
           "\"%ld\",\"tstamp_nano\":\"%ld\",\"capture_length\":\"%d\",\"total_"
           "length\":\"%d\",\"raw_data\":{\"rawhex\":\"",
           header->ts.tv_sec, header->ts.tv_usec, header->caplen, header->len);

    if (printJson) {
        for (int i = 0; i < header->caplen; i++) {
            printf("%02X", packet[i]);
        }
    }
    printf("\",");

    linklayer->lsll_pkt_type = (u_short)parseValue(packet, 2);
    linklayer->lsll_addr_type = (u_short)parseValue(packet + 2, 2);
    linklayer->lsll_addr_len = (u_short)parseValue(packet + 4, 2);
    linklayer->lsll_src = (u_long)parseValue(packet + 6, 8);
    linklayer->lsll_proto = (u_short)parseValue(packet + 14, 2);

    char *sllString = NULL;
    if (printJson) {
        if (asprintf(
                &sllString,
                "\"sll_packet_type\":\"%d\",\"sll_address_type\":\"%d\","
                "\"sll_address_length\":\""
                "%d\",\"sll_source_address\":\"%016lx\",\"sll_protocol\":\"%"
                "04x\"",
                linklayer->lsll_pkt_type, linklayer->lsll_addr_type,
                linklayer->lsll_addr_len, linklayer->lsll_src,
                linklayer->lsll_proto) == -1) {
            printf("ASPRINTF ERR \n");
            return -1;
        }
        printf("%s", sllString);
        free(sllString);
    }

    int currentOffset = 0;

    switch (linklayer->lsll_proto) { /* Check packet type */
    case 0x0800:                     /* Ethernet */
        // printf("This is an ethernet packet\n");
        break;
    case 0x0806: /*ARP*/
        // printf("This is an ARP packet\n");
        return 0;
    default: /* Anything else */
        // printf("This is an not an unknown packet\n");
        return -1;
    }

    currentOffset += LINUX_SLL_SIZE;
    const u_char *ip_pointer = packet + LINUX_SLL_SIZE;
    ip->ip_vhl = ip_pointer[0];
    ip->ip_tos = ip_pointer[1];
    ip->ip_len = (u_short)parseValue(ip_pointer + 2, 2);
    ip->ip_id = (u_short)parseValue(ip_pointer + 4, 2);
    ip->ip_off = (u_short)parseValue(ip_pointer + 6, 2);
    ip->ip_ttl = ip_pointer[8];
    ip->ip_p = ip_pointer[9];
    ip->ip_sum = (u_short)parseValue(ip_pointer + 10, 2);
    ip->ip_src = (u_int)parseValue(ip_pointer + 12, 4);
    ip->ip_dst = (u_int)parseValue(ip_pointer + 16, 4);

    if (printJson) {
        printf(",\"ip_version\":\"%d\",\"ip_header_length\":\"%d\",\"ip_"
               "type_of_"
               "service\":\"%04x\",\"ip_total_length\":\"%d\",\"ip_id\":\"%"
               "04x\",\"ip_offset\":\""
               "%04x\",\"ip_time_to_live\":\"%d\",\"ip_protocol\":\"%"
               "02x\",\"ip_checksum\":\""
               "%04x\","
               "\"ip_src_ip\":\"%08x\",\"ip_dst_ip\":\"%08x\"",
               IP_V(ip), IP_HL(ip), ip->ip_tos, ip->ip_len, ip->ip_id,
               ip->ip_off, ip->ip_ttl, ip->ip_p, ip->ip_sum, ip->ip_src,
               ip->ip_dst);
    }

    currentOffset += IP_HL(ip) * 4;
    const u_char *transmission_pointer = ip_pointer + IP_HL(ip) * 4;
    const u_char *payload_pointer;

    /* Determine and Parse Protocol */
    switch (ip->ip_p) {
    case 0x06:
        // printf("This is a TCP packet\n");
        tcp->th_sport = (u_short)parseValue(transmission_pointer, 2);
        tcp->th_dport = (u_short)parseValue(transmission_pointer + 2, 2);
        tcp->th_seq = (u_int)parseValue(transmission_pointer + 4, 4);
        tcp->th_ack = (u_int)parseValue(transmission_pointer + 8, 4);
        tcp->th_offx2 = transmission_pointer[12];
        tcp->th_flags = transmission_pointer[13];
        tcp->th_win = (u_short)parseValue(transmission_pointer + 14, 2);
        tcp->th_sum = (u_short)parseValue(transmission_pointer + 16, 2);
        tcp->th_urp = (u_short)parseValue(transmission_pointer + 18, 2);
        if (printJson) {
            printf(",\"tcp_src_port\":\"%d\",\"tcp_dst_port\":\"%d\",\"tcp_"
                   "sequence_num\":\""
                   "%04x\",\"tcp_ack_number\":\"%04x\",\"tcp_offset\":\"%"
                   "d\",\"tcp_flags\":\""
                   "%02x\",\"tcp_"
                   "window\":\"%d\",\"tcp_checksum\":\"%04x\",\"tcp_urgent_"
                   "pointer\":\"%d\"",
                   tcp->th_sport, tcp->th_dport, tcp->th_seq, tcp->th_ack,
                   TH_OFF(tcp), tcp->th_flags, tcp->th_win, tcp->th_sum,
                   tcp->th_urp);
        }
        if (TH_OFF(tcp) * 4 < 20) {
            // printf("Malformed TCP Packet\n");
            return -1;
        }
        payload_pointer = transmission_pointer + TH_OFF(tcp) * 4;
        currentOffset += TH_OFF(tcp) * 4;
        break;
    case 0x11:
        // printf("This is a UDP packet\n");
        udp->uh_sport = (u_short)parseValue(transmission_pointer, 2);
        udp->uh_dport = (u_short)parseValue(transmission_pointer + 2, 2);
        udp->uh_len = (u_short)parseValue(transmission_pointer + 4, 2);
        udp->uh_sum = (u_short)parseValue(transmission_pointer + 8, 2);
        if (printJson) {
            printf(",\"udp_src_port\":\"%d\",\"udp_dst_"
                   "port\":\"%d\",\"udp_total_"
                   "length\":\"%d\",\"udp_checksum\":\"%04x\"",
                   udp->uh_sport, udp->uh_dport, udp->uh_len, udp->uh_sum);
        }
        payload_pointer = transmission_pointer + 8;
        currentOffset += 8;
        break;
    default:
        // printf("This is a packet of unknown protocol\n");
        return -1;
    }

    /* Checking if payload is FIX */
    char payloadHeader[6];
    memcpy(payloadHeader, payload_pointer, 6);
    if (strncmp(payloadHeader, FIX_HEADER, 6) != 0) {
        // printf("Not a FIX Packet!\n");
        return -1;
    }

    char *fixDelim = "\x01";
    char *fixPtr;
    char fixData[header->caplen - currentOffset + 1];
    memcpy(fixData, payload_pointer, header->caplen - currentOffset);
    fixData[header->caplen - currentOffset] = '\0';
    char *tag = strtok_r(fixData, fixDelim, &fixPtr);

    if (tag == NULL) {
        // printf("Invalid FIX Packet\n");
        return -1;
    }

    while (tag != NULL) {
        char *label = strtok(tag, "=");

        /* Analyse tag */
        if (strcmp(label, FIX_BEGIN_STRING) == 0) {
            fix->beginString = strtok(NULL, "=");
        } else if (strcmp(label, FIX_BODY_LENGTH) == 0) {
            fix->bodyLength = strtok(NULL, "=");
        } else if (strcmp(label, FIX_MSG_TYPE) == 0) {
            fix->msgType = strtok(NULL, "=");
        } else if (strcmp(label, FIX_SENDER_COMP_ID) == 0) {
            fix->senderCompID = strtok(NULL, "=");
        } else if (strcmp(label, FIX_TARGET_COMP_ID) == 0) {
            fix->targetCompID = strtok(NULL, "=");
        } else if (strcmp(label, FIX_MSG_SEQ_NUM) == 0) {
            fix->msgSeqNum = strtok(NULL, "=");
        } else if (strcmp(label, FIX_SENT_TSTAMP) == 0) {
            fix->sendingTime = strtok(NULL, "=");
        } else if (strcmp(label, FIX_CL0RDID) == 0) {
            fix->cl0rdID = strtok(NULL, "=");
        } else if (strcmp(label, FIX_SYMBOL) == 0) {
            fix->symbol = strtok(NULL, "=");
        } else if (strcmp(label, FIX_ORD_STATUS) == 0) {
            fix->ordStatus = strtok(NULL, "=");
        } else if (strcmp(label, FIX_SIDE) == 0) {
            fix->side = strtok(NULL, "=");
        } else if (strcmp(label, FIX_ORD_TYPE) == 0) {
            fix->ordType = strtok(NULL, "=");
        } else if (strcmp(label, FIX_ORD_QTY) == 0) {
            fix->ordQty = strtok(NULL, "=");
        } else if (strcmp(label, FIX_TIME_IN_FORCE) == 0) {
            fix->timeInForce = strtok(NULL, "=");
        } else if (strcmp(label, FIX_PRICE) == 0) {
            fix->price = strtok(NULL, "=");
        } else if (strcmp(label, FIX_MDREQ_ID) == 0) {
            fix->mdReqID = strtok(NULL, "=");
        } else if (strcmp(label, FIX_CHECKSUM) == 0) {
            fix->checksum = strtok(NULL, "=");
            break;
        }
        tag = strtok_r(NULL, fixDelim, &fixPtr);
    }
    if (printJson) {
        printf(",\"fix_begin_string\":\"%s\",\"fix_body_length\":\"%s\",\""
               "fix_msg_type\":\"%s\",\""
               "fix_sender_comp_id\":\"%s\",\"fix_target_comp_id\":\"%s\",\""
               "fix_msg_seq_num\":\""
               "%s\",\"fix_sent_tstamp\":\"%s\",\"fix_cl0rdid\":\"%s\","
               "\"fix_symbol\":\"%s\",\""
               "fix_ord_status\":\"%s\",\"fix_side\":\"%s\",\"fix_ord_type\":"
               "\"%s\",\""
               "fix_ord_qty\":\""
               "%s\",\"fix_time_in_force\":\"%s\",\"fix_price\":\"%s\","
               "\"fix_mdreq_id\":\"%s\",\""
               "fix_checksum\":\"%s\"",
               fix->beginString, fix->bodyLength, fix->msgType,
               fix->senderCompID, fix->targetCompID, fix->msgSeqNum,
               fix->sendingTime, fix->cl0rdID, fix->symbol, fix->ordStatus,
               fix->side, fix->ordType, fix->ordQty, fix->timeInForce,
               fix->price, fix->mdReqID, fix->checksum);
    }
    return 0;
}

#ifndef NETPARSE_H
#define NETPARSE_H

#include <pcap/pcap.h>
#include <sys/types.h>

#define FIX_HEADER "8=FIX."
#define LINUX_SLL_SIZE 16

/* FIX Tags */
#define FIX_BEGIN_STRING "8"
#define FIX_BODY_LENGTH "9"
#define FIX_MSG_TYPE "35"
#define FIX_SENDER_COMP_ID "49"
#define FIX_TARGET_COMP_ID "56"
#define FIX_MSG_SEQ_NUM "34"
#define FIX_SENT_TSTAMP "52"
#define FIX_CL0RDID "11"
#define FIX_SYMBOL "55"
#define FIX_ORD_STATUS "39"
#define FIX_SIDE "54"
#define FIX_ORD_TYPE "40"
#define FIX_ORD_QTY "38"
#define FIX_TIME_IN_FORCE "59"
#define FIX_PRICE "44"
#define FIX_MDREQ_ID "262"
#define FIX_CHECKSUM "10"

/* Linux cooked linklayer */
struct linux_linklayer_sll {
    u_short lsll_pkt_type;  /* packet type */
    u_short lsll_addr_type; /* address type */
    u_short lsll_addr_len;  /* address length */
    u_long lsll_src;        /* src mac address */
    u_short lsll_proto;     /* ip protocol */
};
typedef struct linux_linklayer_sll linux_linklayer_sll_t;

/* IP header */
struct ip_header {
    u_char ip_vhl;        /* version << 4 | header length >> 2 */
    u_char ip_tos;        /* type of service */
    u_short ip_len;       /* total length */
    u_short ip_id;        /* identification */
    u_short ip_off;       /* fragment offset field */
#define IP_RF 0x8000      /* reserved fragment flag */
#define IP_DF 0x4000      /* don't fragment flag */
#define IP_MF 0x2000      /* more fragments flag */
#define IP_OFFMASK 0x1fff /* mask for fragmenting bits */
    u_char ip_ttl;        /* time to live */
    u_char ip_p;          /* protocol */
    u_short ip_sum;       /* checksum */
    u_int ip_src;         /* source ip address */
    u_int ip_dst;         /* destination ip address */
};
#define IP_V(ip) ((ip)->ip_vhl >> 4)
#define IP_HL(ip) ((ip)->ip_vhl & 0x0F)
typedef struct ip_header ip_header_t;

/* TCP header */
struct tcp_header {
    u_short th_sport; /* source port */
    u_short th_dport; /* destination port */
    u_int th_seq;     /* sequence number */
    u_int th_ack;     /* acknowledgement number */
    u_char th_offx2;  /* data offset, rsvd */
#define TH_OFF(th) (((th)->th_offx2 & 0xf0) >> 4)
    u_char th_flags;
#define TH_FIN 0x01
#define TH_SYN 0x02
#define TH_RST 0x04
#define TH_PUSH 0x08
#define TH_ACK 0x10
#define TH_URG 0x20
#define TH_ECE 0x40
#define TH_CWR 0x80
#define TH_FLAGS (TH_FIN | TH_SYN | TH_RST | TH_ACK | TH_URG | TH_ECE | TH_CWR)
    u_short th_win; /* window */
    u_short th_sum; /* checksum */
    u_short th_urp; /* urgent pointer */
};
typedef struct tcp_header tcp_header_t;

/* UDP header */
struct udp_header {
    u_short uh_sport; /* source port */
    u_short uh_dport; /* destination port */
    u_short uh_len;   /* udp length */
    u_short uh_sum;   /* checksum */
};
typedef struct udp_header udp_header_t;

/* FIX Payload */
struct fix_payload {
    char *beginString;
    char *bodyLength;
    char *msgType;
    char *msgSeqNum;
    char *senderCompID;
    char *targetCompID;
    char *sendingTime;
    char *cl0rdID;
    char *symbol;
    char *ordStatus;
    char *side;
    char *ordType;
    char *ordQty;
    char *timeInForce;
    char *price;
    char *mdReqID;
    char *checksum;
    char *unrecognised;
};
typedef struct fix_payload fix_payload_t;

int parsePacket(const int diagnostics, const struct pcap_pkthdr *header,
                const u_char *packet, linux_linklayer_sll_t *linklayer,
                ip_header_t *ip, tcp_header_t *tcp, udp_header_t *udp,
                fix_payload_t *fix);
#endif

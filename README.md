# group-02-project

## Name
CloudPCap

## Description

CloudPCap is a packet-capture software that is desigend to work in cloud environments. Specifically, we set up the packet-capture software using AWS EC2 and AWS Traffic Mirroring. 

In algorithmic / high frequency trading, algorithms will oftentimes be set up to trade once certain indicators are met. This means that the tick-to-trade time is crucial. In other words, it is very important for traders to enter trades as quickly as possible upon receiving relevant market data. Traders can analyze their tick-to-trade time by tracking their incoming and outgoing packets using ```tcpdump```. Many trading shops and firms are able to spend thousands on expensive hardware, data feeds, etc, allowing them to efficiently trade (and analyze incoming / outgoing packets). 

However, data feeds in cryptocurrency are far cheaper / free, meaning that there are many at-home traders algorithmically trading crypto. Our idea is simple. We are offering software to all types of traders interested in tracking their incoming and outgoing packets. 

Suppose you have a "trader" server (EC2 instance). The trader is sending trade requests, receiving trade confirmation, etc. In addition, the server is receving real-time market data from a data feed. Upon receiving market data, if there is a calculated trade signal, the trader makes a trade request immediately. Using AWS Traffic Mirroring, we can direct (essentially copy over) all incoming and outgoing requests to a second "monitor" server (another EC2 instance). On this monitor server, our application can capture and parse the packets to display in an inutitive front-end application. 

Packet / traffic analysis includes in-depth analytics and charts of tick-to-trade latency. Assuming the exchange has timestamp information as well, we provide latency analytics comparing when the exchange sent the data and when the data arrived at the "trader" server. 

This is highly useful for all traders as the costs of running two EC2 instances along with Traffic Mirroring are significantly cheaper than the upfront hardware and energy costs of a  setup. 

### Areet Sheth

<img src="assets/Areet-Headshot.jpeg" width="200" height="200">

Areet is an undergraduate student dual majoring in Computer Science + Statistics and Mathematics at the University of Illinois Urbana-Champaign.

[LinkedIn](https://www.linkedin.com/in/areet-sheth/), [Github](https://github.com/areetsheth), [Email](assheth2@illinois.edu)

### Yash Savalia

<img src="assets/Yash-Headshot.png" width="200" height="200">

Yash is an undergraduate student enrolled in a dual degree in Computer Science + Astronomy and Engineering Physics at the University of Illinois Urbana-Champaign.

[LinkedIn](https://www.linkedin.com/in/yash-savalia/), [Github](https://github.com/yashsavalia1), [Email](savalia2@illinois.edu)


## Project Visualization / Demo 
INSERT FRONT-END IMAGES AND DEMO VIDEO HERE

## Installation
INSTALLATION STEPS HERE

## Usage
ADD SIMPLE USAGE GUIDE HERE

## Support
Contact either Areet or Yash for support. 

## Roadmap
- Integrating realistic / real time data feed
- Machine learning analytics
- More sophisticated front-end UX and charting
- Integration of supporting multiple exchanges and order APIs


## Contributing
If you are interested in contributing, please reach out to Areet or Yash via their contact. 

## License
For open source projects, say how it is licensed.

## Project status
In progress. 

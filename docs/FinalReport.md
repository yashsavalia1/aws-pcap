# Cloud-based Packet Capture

[[_TOC_]]

## 1. Abstract

In HFT (High Frequency Trading), traders constantly receive market data. When their algoriths detect preset market behaviour, they trigger trade requests. Thus, the tick-to-trade time is very important for traders. Tick-to-trade time is the the latenchy between receiving market data and placing a trade. It is very important for traders to tune their hardware to make this process more efficient. 

Unlike other instruments and markets, cryptocurrency has more at-home traders. These traders do not work for major firms or shops, but rather trade from their computers or phones. This is possible becasue cryptocurrency is decentralized and all traders have fair access to the market feed. 

We present a unique solution to cryptocurrency traders: CloudPCap (Cloud-based packet pacture). As traders receive incoming market data packets, we monitor the latency of the packets to see the difference between the time the packet was sent from the exchange and the time the packet was received by the trader. We also monitor the difference between the time the packet was received and the time the trade was placed. Traders can use this to compare different data feed exchanges, order exchanges, and algorithms. 

The most appealing aspect of our solution is that the software is built to be stored on AWS, or other cloud based services. This provides a much cheaper alternative for at-home traders compared to an expensive hardware setup. 

## 2. Introduction

### 2.1 Team Profile

#### Areet Sheth

<img src="../assets/Areet-Headshot.jpeg" width="200" height="200">

Areet is an undergraduate student dual majoring in Computer Science + Statistics and Mathematics at the University of Illinois Urbana-Champaign.

[LinkedIn](https://www.linkedin.com/in/areet-sheth/), [Github](https://github.com/areetsheth), [Email](assheth2@illinois.edu)

#### Yash Savalia

<img src="../assets/Yash-Headshot.png" width="200" height="200">

Yash is an undergraduate student enrolled in a dual degree in Computer Science + Astronomy and Engineering Physics at the University of Illinois Urbana-Champaign.

[LinkedIn](https://www.linkedin.com/in/yash-savalia/), [Github](https://github.com/yashsavalia1), [Email](savalia2@illinois.edu)

### 2.2 Relevant Concepts

#### Exchange

An exchange is where financial instruments are traded. Exchanges essentially host the financial instrument, and contain major aspects like a data feed, order matching engine, etc

#### Data Feed

Exchanges send out financial data to any user that is subscribed. This data can be private (based on specific trades by the user) or public (general information). In our case, the financial data is general cryptocurrency price and market data. We achieve this using a websocket server. 

#### Order Matching Engine

Exchanges have an order matching engine that receives buy and sell orders and maintains them. The engine matches buy (bid) offers and sell (ask) offers against each other. An order matching engine is essentially a maintained and algorithmic order book. In our case, a full OME is not necessary. Instead, we have an HTTP server receive orders from the trader for latency analytics. 


#### Websocket vs. HTTP Server

A websocket involves a livestream of data. A user can subscribe to a websocket, and receive streams of data without making additional requests. HTTP servers involve making requests to obtain data. 

#### Network Packets

Network packets are fundamental units of data transmitted over a network. They contain both the data being sent and the necessary information for routing and delivery, including source and destination addresses. Packets are typically small in size and travel independently across the network, often taking different routes to reach their destination. Through protocols like TCP/IP, packets ensure reliable and efficient communication between devices connected to the network.

#### Packet Capture

Packet capture, also known as packet sniffing or network sniffing, is the process of intercepting and logging data packets that are being transmitted over a network. This can be done using specialized software or hardware tools called packet sniffers. Packet capture allows network administrators and security professionals to analyze network traffic, diagnose network issues, and investigate security breaches by inspecting the contents of the captured packets. It provides insights into the communication patterns, protocols used, and potential security threats within a network environment. In our case, we use the libpcap or pcap library to capture packets. 

#### SSL Decryption

SSL decryption, also known as SSL/TLS interception or SSL inspection, is a process used to decrypt encrypted traffic transmitted over a Secure Sockets Layer (SSL) or Transport Layer Security (TLS) encrypted connection. This decryption is typically performed by security appliances or proxies that have access to the encryption keys. In our case, the market data is encrpyted. When the client makes a connection with the websocket server, the SSL key is logged. This key is used for decryption later in the process. 

#### AWS ec2 Instance

An Amazon Elastic Compute Cloud (EC2) instance is a virtual server in the Amazon Web Services (AWS) cloud. Users can rent and launch EC2 instances to run their applications, store data, or host websites on scalable computing capacity. EC2 instances offer various configurations in terms of CPU, memory, storage, and networking resources to meet different workload requirements. Users can choose from a wide range of pre-configured templates (Amazon Machine Images or AMIs) or create custom images to deploy their applications quickly. EC2 instances are billed on a pay-as-you-go basis, allowing users to scale their computing resources up or down based on demand.

#### AWS Traffic Mirroring

Traffic mirroring in AWS is a feature that allows you to capture and inspect network traffic in your Virtual Private Cloud (VPC). It works by creating a copy of the network traffic passing through an Elastic Network Interface (ENI) and then sending that copy to a designated destination for analysis. This destination could be an Amazon EC2 instance, an AWS Partner solution, or an AWS service like Amazon VPC Flow Logs or Amazon Athena. Traffic mirroring is useful for troubleshooting, monitoring, and security analysis purposes, providing insight into the traffic patterns and potential security threats within your VPC.

## 3. Tools and Technology

### Front-End: Vite, React, and Tailwind

### Back-end: GO packet capture application

Using Echo for the HTTP server (trading API) and websocket (data feed). Also using the GO pcap library for packet capture. 

### Database: SQLite

## 4. In-Depth Project Summary

### 4.1 Project Vision:

Our project name is CloudPCap - packet capture in the cloud. CloudPCap is a packet-capture software that is desigend to work in cloud environments. Specifically, we set up the packet-capture software using AWS EC2 and AWS Traffic Mirroring. 

In algorithmic / high frequency trading, algorithms will oftentimes be set up to trade once certain indicators are met. This means that the tick-to-trade time is crucial. In other words, it is very important for traders to enter trades as quickly as possible upon receiving relevant market data. Traders can analyze their tick-to-trade time by tracking their incoming and outgoing packets using ```tcpdump```. Many trading shops and firms are able to spend thousands on expensive hardware, data feeds, etc, allowing them to efficiently trade (and analyze incoming / outgoing packets). 

However, data feeds in cryptocurrency are far cheaper / free, meaning that there are many at-home traders algorithmically trading crypto. Our idea is simple. We are offering software to all types of traders interested in tracking their incoming and outgoing packets. 

Suppose you have a "trader" server (EC2 instance). The trader is sending trade requests, receiving trade confirmation, etc. In addition, the server is receving real-time market data from a data feed. Upon receiving market data, if there is a calculated trade signal, the trader makes a trade request immediately. Using AWS Traffic Mirroring, we can direct (essentially copy over) all incoming and outgoing requests to a second "monitor" server (another EC2 instance). On this monitor server, our application can capture and parse the packets to display in an inutitive front-end application. 

Packet / traffic analysis includes in-depth analytics and charts of tick-to-trade latency. Assuming the exchange has timestamp information as well, we provide latency analytics comparing when the exchange sent the data and when the data arrived at the "trader" server. 

This is highly useful for all traders as the costs of running two EC2 instances along with Traffic Mirroring are significantly cheaper than the upfront hardware and energy costs of a setup. 

### 4.2 Inner Workings:

There are 3 main servers at work: Data Feed Websocket, Order API, and the Client. Realistically, traders have a trustworthy data feed, but for now we are using a mock datafeed. In addition, traders receive order confirmation from their broker. Again, for the sake of the project, we use an artificial HTTP Order API. Finally, the client connects to data feed and order api servers. 

The concept is simple. After connecting, the client will receive data from the data feed via a socket. Upon receiving data, the client will send orders (based on an algorithm). These incoming and outgoing packets are copied to a monitoring ec2 instance using AWS Traffic Mirroring. 

The monitoring server accepts the packets and decodes them. It takes the receiving time and the decoded initial time to calculate packet latency. It can also calculate packet latency for tick-to-trade time. This occurs because the client stores an SSL key that is used to decrypt the SSL packets on the monitor side. The decoded information is stored in SQLite, which is then used on the front-end for live displays of information. 

### 4.3 Live Demo:

[Link to the demonstration]()

### 4.4 Project Breakdown:

Areet:
- Created python HTTP and Websocket servers. 
- Added encryption to servers. 
- Created C scripts for packet capture and parsing. 
- Added packet decrpytion. 

Yash:
- Spearheaded front-end design.
- Spearheaded conversion of packet capture and servers to Go. 
- Worked on full-stack design (included database).
- Configured AWS. 

Together:
- Created accurate HTTP and Websocket servers, and migrated to Go. 
- Migrated the packet capture to Go. 
- Configured packet decrpytion, and optimized for the web application. 
- Designed the client. 

Future Steps:
- Areet will focus on the statistical analysis. 
- Yash will focus on creating better front-end functionality. 
- Together, they will work on all latency analysis (incoming market data latency and tick-to-trade latency). Together, they will incorporate advanced functionality as well, as listed in future work below. 

## 5. Future Work

Our next steps are as follows:

- Ensure fully accurate data via packet capture and front-end display. 
- Utilize a real data feed for more accurate information and appeal.
- Finish integrating the order API server to track tick-to-trade analytics. 
- Include multiple exchanges, order servers, etc for more in-depth analytics. 
- Use machine learning and statistical modeling when analyzing latency. 
- Add more functionality for charting on the front-end. 
- Add functionality for users to test/backtest algorithms, and deploy them real time. 
- Containerize the entire system.

## 6. Project Reflections

### Areet:

Before this project, I had some experience with making full-stack application, but the project gave me a much better experience with the development process. I was able to work on end-to-end development of a full-stack application, and had an impact on the design process for the front-end, back-end, and application layer. 

My main takeaways were:
- Learning the importance of trial and error. The project involved many successes but more failures. Many times we had to take a step back and restart our process, using new technologies. This truly increased the amount I learned. 
- Start with simple steps, then increase complexity. Starting with simple servers, slowly adding encryption, then connecting to the front-end, integrating with AWS and finally tackling decryption greatly helped with the project process. 
- Packet-capture concepts. Before this, we covered pcap in class, but I did not fully understand the concepts. This project helped me understand every aspect of packet capture, including how to use Wireshark, how to use libpcap, how to understand packets, how to decrypt packets, etc
- Go. I was able to learn Go for the first time, which was very exciting. 
- Future work. The project is not fully complete, and I am excited to learn more by completing the project and adding more to the project. 

### Yash: 

My main takeawys were:
- Similar to Areet, learning the importance of trial and error. It was a rewarding process of constantly making errors and learning. 
- I was very unaware of packet capture, so the project helped increase my understanding. Now I understand how packet capture works and can use packet capture for latency analysis for financial and other projects going forward. 
- I always knew Go, but never had a chance to use it. Using it was very fun, but still presented a learning curve. 
- I have done many full-stack projects, but this project was quite challenging, so I was able to learn alot from it. This includes more advanced charting, creating a better UI/UX, working with a complex backend, etc. 
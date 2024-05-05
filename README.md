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

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
If you are interested in contributing, please reach out to Areet or Yash via their contact. 

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.

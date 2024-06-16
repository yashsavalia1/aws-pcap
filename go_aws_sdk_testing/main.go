package main

import (
	"fmt"
	"log"
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ec2"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	sess, err := session.NewSession(&aws.Config{
		Region: aws.String(os.Getenv("AWS_REGION")),
		Credentials: credentials.NewStaticCredentials(
			os.Getenv("AWS_ACCESS_KEY_ID"),
			os.Getenv("AWS_SECRET_ACCESS_KEY"),
			"",
		),
	})
	if err != nil {
		log.Fatal("Error creating session:", err)
	}

	svc := ec2.New(sess)

	//params := &ec2.DescribeInstanceStatusInput{}

	// resp, err := svc.DescribeInstanceStatus(params)
	// if err != nil {
	// 	log.Fatal("Error describing instance status:", err)
	// }
	//fmt.Printf("Instance Status: %s\n", resp)

	tagParams := &ec2.DescribeTagsInput{}
	tagsResp, err := svc.DescribeTags(tagParams)
	if err != nil {
		log.Fatal("Error describing tags:", err)
	}
	//fmt.Printf("Tags: %s\n", tagsResp)

	trafficMirrorParams := &ec2.DescribeTrafficMirrorSessionsInput{}
	trafficMirrorResp, err := svc.DescribeTrafficMirrorSessions(trafficMirrorParams)
	if err != nil {
		log.Fatal("Error describing traffic mirror sessions:", err)
	}
	//fmt.Printf("Traffic Mirror Sessions: %s\n", trafficMirrorResp)

	networkInterfacesParams := &ec2.DescribeNetworkInterfacesInput{}
	networkInterfacesResp, err := svc.DescribeNetworkInterfaces(networkInterfacesParams)
	if err != nil {
		log.Fatal("Error describing network interfaces:", err)
	}
	//fmt.Printf("Network Interfaces: %s\n", networkInterfacesResp)

	if len(trafficMirrorResp.TrafficMirrorSessions) == 0 {
		log.Fatal("No Traffic Mirror Sessions found")
	}

	NetworkInterfaceId := trafficMirrorResp.TrafficMirrorSessions[0].NetworkInterfaceId

	if len(networkInterfacesResp.NetworkInterfaces) == 0 {
		log.Fatal("No Network Interfaces found")
	}

	ec2InstanceId := ""

	for _, networkInterface := range networkInterfacesResp.NetworkInterfaces {
		if *networkInterface.NetworkInterfaceId == *NetworkInterfaceId {
			ec2InstanceId = *networkInterface.Attachment.InstanceId
			break
		}
	}

	if ec2InstanceId == "" {
		log.Fatal("No EC2 Instance found")
	}

	if len(tagsResp.Tags) == 0 {
		log.Fatal("No Tags found")
	}

	for _, tag := range tagsResp.Tags {
		if *tag.ResourceId == ec2InstanceId {
			fmt.Printf("ec2 instance Name: %s\n", *tag.Value)
		}
	}

}

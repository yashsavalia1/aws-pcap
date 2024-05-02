require('dotenv').config();
const AWS = require('aws-sdk');

//Configure AWS SDK with your credentials
AWS.config.update({
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    region: process.env.AWS_REGION
  });

// Create an EC2 object
const ec2 = new AWS.EC2();

// Define parameters for the describeInstances operation
const params = {};

// Call the describeInstances method

ec2.describeInstanceStatus(params, (err, data) => {
    if (err) {
        console.error("Error:", err);
    } else {
        console.log("Success:", JSON.stringify(data, null, 2));
    }
});
// ec2.describeInstances(params, (err, data) => {
//   if (err) {
//     console.error("Error:", err);
//   } else {
//     console.log("Success:", JSON.stringify(data, null, 2));
//   }
// });

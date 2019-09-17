# Hackathon IAA 2019
# Continental Data Square - Monetization Framework
Welcome to the continental.cloud Hackathon.
Now that you've found your way to the github repo here are the first steps to start with.

The time is limited! You might split up your team into several roles, based on your skillset.
For example:
- Service / Backend Developer
- HMI Developer
- Designer
- Presentation & Business123

How to start your work is dependent on your role. Here is what we have to help you with this.
If you have any questions you can always ask our experts or team guides to help you.

## Basic component architecture
Each team in the hackathon will create microservices. These microservices publish to topics that can be subscribed to. The publishing and subscribing happens through the service router.

The service router can be found at:
```
wss://continental2.crossbario.com/ws
```

All teams share the service router, and the realm on this router(`realm1`). Topics are categorized under realms, no two topics should have the same name under a realm.
For that reason each team is only allowed to work on topics with a specific prefix.

Depending on your team, the prefix allocated to your team is as follows:

1. Team 1: com.conti.hackathon.team1
2. Team 2: com.conti.hackathon.team2
3. Team 3: com.conti.hackathon.team3
4. Team 4: com.conti.hackathon.team4

To connect to the realm a username (`teamX`) and password is necessary, which is provided by the group leader.

## Chat system

Exchange code snippets or information in a rocket chat - join **http://chat.dmp.be.continental.cloud**

## Continous Integration

You can use the preapred Gitlab CI setup to deploy your HTML5 application to the destination.
Please rename the file accordingly. Only commits on MASTER will be deployed.

## Task 1 - Get ready to earn
After following this section a team will have their own Ethereum wallet with ether and XBR tokens, which are necessary for the participation of the hackathon. The major steps are:
1. Setup Metamask
2. Request Ether & XBR
3. Open Payment Channel


### 1.1 Setup Metamask
1. Metamask is a light client for Ethereum. It allows for creation and managing of Ethereum wallets. Metamask is a browser extension, using Chrome, Firefox, Opera or Brave install Metamask from: https://metamask.io/
2. Once Metamask is installed it will prompt you to import or create new wallet, choose create new wallet, and choose a password for the new wallet.
3. Metamask uses a seedphrase to derive private/public key pairs (an Ethereum wallet is a private/public key pair). Use the default seedphrase that is provided by Metamask, but copy it somewhere as in the next step you are required to input the seedphrase once again for confirmation.
4. Once the wallet is created open Metamask by clicking at the browser extension situated on the toolbar on the top right. By default Metamask uses Ethereum Main Network, change this by clicking on the label, from the dropdown choose Ropsten Test Network.


### 1.2 Request Ether & XBR
1. Click the menu icon in Metamask and click add new token
2. Click Custom Token, copy paste the XBR Token address and click next.
```
0xCfEB869F69431e42cdB54A4F4f105C19C080A601
```
3. From Metamask, copy your Ethereum address and paste it on the  hackathon chat.
4. We will send you Ether and XBR Token, soon you will see your Ether and XBR Token balance updated.

### 1.3 Open Payment Channel
Register and open a payment channel from here:
http://iaa2019-hackathon-apps.s3-website.eu-central-1.amazonaws.com/


## Task 2 - Time is money
After this task you will have a service running that sells some data on the market and earns XBR tokens for your team.
It will also provide you with data you can use for testing and developing your own service.
Only one of your team members should run this service at the same time (unless you know what you are doing).

To get it up and running the following steps are needed:
1. Clone the example code from GitLab and move to the `service/fleet-simulation` folder.
2. Build the docker container by running `docker build -t fleet-simulation .` (don't forget the dot at the end!).
3. Modify the env.list file with the required settings. You will need the delegate's private key from the first task and your login credentials to the service router.
4. Start the docker container via the `docker run -it --env-file env.list fleet-simulation`.
5. Check the output to see if your data gets bought.

## Task 3 - Become a service provider
Upon completion of this task your team will have a service running that buys some data from the fleet simulation and sells something of your chosing to interested parties.
It will also be useful for providing a service to enhance the life of your persona.

To accomplish this task you will need to do the following:
1. Decide whether you want to develop the service in in Node.js or Python3.
2. Go to the `service/simple-js` or `service/simple-python` folder.
3. Adapt the buyer code to use your buyer delegate address and buy data from your fleet-simulation.
4. Change the seller code to use a new seller delegate key and sell on a topic of your choice.
5. Forward/filter/transform some data from the seller to your buyer.
6. Inform your team lead that you accomplished this task to earn the extra tokens.

## Task 4 - Develop vehicle app
The goal of this task is to develop an HMI application that shows up on the vehicle demonstrator.
This app should be an HTML5 application that automatically gets deployed on code check-in into the GitLab server.
It should fulfill the needs of a chosen persona with the help of data provided by your backend service.

The following steps are needed to get it running:
* In the `app/` folder you need to work the following files:
  * `index.html`
  * `main.js`
1. Receive persona private key from your team lead.
2. Make the appropiate config changes to `main.js`.
3. Implement a example rpc call in the service provider from previous task. The buy data button shall become active after the rpc call is made.
4. Implement purchasing of keys from the service provider with the click of the buy button.
5. Display the bought data on the frontend.
6. Check if you receive tokens from the persona.


## Task 5 - Sell your idea
When the timer runs out you need to present your idea to the jury.
The jury will invest 6000 tokens into the ideas of the hackteams.
To convice them, you need to prepare a 12 minute presentation including:
* Your team
* The story and needs of your selected persona
* The idea of your hackteam
* High level details of implementation (It is a management jury)
* Your Business model - Which data is monetized ? What is the target group & market ?
* Show your app on the demonstrator

It's up to you to present. You can prepare slides or use the whiteboard. Tell the story!
The jury will evaluate your idea based on factors such as innovativeness, potential and feasability.
After all presentation, invested tokens will be added at the end to your team wallet.

## If you need help at any point, feel free to ask our experts to help you. Have fun at the hackathon !


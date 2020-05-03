# Devops automation task submission

This folder contains my submission of the devops automation task.

## The task:
Create a vagrant environment with 3 servers and configure it using chef, puppet or ansible:
 - 2 web servers there each of the hosts will show a single static page with a message: 
Hello from web server <server name> 
 - 	1 load balancer between those 2 servers.

## Submission:
The files in this folder perform the requested task, here's a detailed description of the files:

| Filename | Description |
| ------ | ------ |
| [Vagrantfile](Vagrantfile) | The Vagrant configuration file, supports 1-9 web servers |
| [cookbooks/apache/recipes/default.rb](cookbooks/apache/recipes/default.rb) | Chef recipe for Apache installation (common for both webservers and load-balancer) |
| [cookbooks/apache/recipes/default.rb](cookbooks/apache/recipes/default.rb) | Chef recipe for the web-servers configuration |
| [cookbooks/apache/templates/default/index.html.erb](cookbooks/apache/templates/default/index.html.erb) | Chef template for the static html response with the hostname embedded |
| [cookbooks/apache/files/default/fixed-response.conf](cookbooks/apache/files/default/fixed-response.conf) | Chef cookbook_file to return the same static response for any requested URI by modifying the http 404 response  |
| [cookbooks/apache/recipes/lb-config.rb](cookbooks/apache/recipes/lb-config.rb) | Chef recipe for the load-balancer configuration |
| [cookbooks/apache/templates/default/balancer.conf.erb](cookbooks/apache/templates/default/balancer.conf.erb) | Chef template for the load-balancer configuration, supports 1-9 web servers |
| [roles/web.json](roles/web.json) | Chef role for deploying the web-servers |
| [roles/lb.json](roles/lb.json) | Chef role for deploying the load-balancer |
| [nodes/](nodes/) | Chef nodes directory, required for running Chef |
| [README.md](README.md) | This documentation file |


## Prerequisites and assumptions
  - Vagrant is installed and functional
  - The running user has sufficient permissions 
  - curl is installed and functional (for testing)
  - Internet access is available (for downloading images and other components)
  - Host has sufficient resources for running the guest VMs
  - There are no other running VMs (or what-not) occupying the same IPs and localhost ports as the VMs in this task (see [Vagrantfile](Vagrantfile))
  
## Checking the task:
To deploy the VMs, clone this repo and from the Automation directory run:

`$ vagrant up`

To test the load-balanced output, run the following command several times:

`$ curl http://localhost:8011/`



Enjoy :)

  Nadav.

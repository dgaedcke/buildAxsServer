# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "wittman/centos-6.7"
  config.vm.box_check_update = false

  config.vm.network "private_network", ip: "192.168.192.168"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
end

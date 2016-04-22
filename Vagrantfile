# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "axs-server"
  config.vm.box_check_update = false

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
  end

  config.vm.network "private_network", ip: "192.168.192.168"
  config.vm.network "forwarded_port", guest: 8000, host: 5000
end

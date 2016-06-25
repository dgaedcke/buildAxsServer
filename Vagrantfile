# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "axs-server"
  config.vm.box_check_update = false
  config.vm.hostname = "vagrant-axs-server"

  config.ssh.username = "vagrant"

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
  end

  config.vm.provider "digital_ocean" do |d, override|
    override.ssh.private_key_path = "~/.ssh/id_rsa"
    override.vm.box = "digital_ocean"
    override.vm.box_url = "https://github.com/devopsgroup-io/vagrant-digitalocean/raw/master/box/digital_ocean.box"
    # Disable default synced folder
    override.vm.synced_folder ".", "/vagrant", disabled: true

    d.token = ENV["DIGITALOCEAN_API_KEY"]
    d.ssh_key_name = ENV["DIGITALOCEAN_SSH_KEY"] || "Vagrant"
    # Image IDs are retrievable with `vagrant digitalocean-list images $DIGITALOCEAN_API_KEY`
    d.image = "18084429" # axs-server-1466806201
    d.region = "nyc3"
    d.size = "1gb"
  end

  config.vm.network "private_network", ip: "192.168.192.168"
  config.vm.network "forwarded_port", guest: 8000, host: 5000
end

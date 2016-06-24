# Paysys Vagrant environment


## Usage:
	# to pull the master branch, run this:
	fab loadenv:dev gitpull
	fab loadenv:dev loadData
	will need to reset the dewey@minggl.com password in the DB to:
	'pbkdf2:sha1:1000$X4xknZGM$fcf1c6a3dd929ad3ea096ece42761e523d150049' == apple
	after reloading the DB

## Requirements

 - [Vagrant 1.8+](https://www.vagrantup.com/downloads.html)
 - [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
 - [Fabric](http://www.fabfile.org/)
  - Fabric and its dependencies can be installed with `pip install -r requirements.txt`

### Optional

 - [vagrant-digitalocean](https://github.com/devopsgroup-io/vagrant-digitalocean)

## Creating a development environment

  1. Create the Virtualbox VM using Vagrant.

    ```
    $ vagrant up
    ```

  2. Run the Fabric task `deploy` against the newly created VM. We're also running the task `loadenv` with `dev` as an argument to load the `dev.yml` (context) file which is also provided in this repository. This file specifies information such as the IP address of our Vagrant VM and the roles which it has defined. At the start of the deploy, you will be prompted for the passphrase for the SSH key provided in `files/id_deploy`.

    ```
    $ fab loadenv:dev deploy
    ```

    You can also specify a remote branch or tag to deploy by providing an argument to deploy:

    ```
    $ fab loadenv:dev deploy:testing-branch
    ```

  3. After a successful fabric run, your application should now be visible at `localhost:8000` on your local machine. This is configured by a forwarded port in the Vagrantfile, but you can also access services directly on the Virtual Machine at address `192.168.192.168`.

  4. If you want to make any changes on the VM, login using:

    ```
    $ vagrant ssh
    ```

  5. Finally, when you are done, you can destroy the environment by running:

    ```
    $ vagrant destroy
    ```

### DigitalOcean

#### Installing the Vagrant plugin

Before you can do anything with DigitalOcean via Vagrant, the plugin must be installed using the following command:

```
$ vagrant plugin install vagrant-digitalocean
```

#### Creating a droplet using Vagrant

In order to authenticate with DigitalOcean, you will need to retrieve your DigitalOcean API key (which can be found in the control panel under the Apps & API section) and export it as the environment variable `DIGITALOCEAN_API_KEY` in your shell:

```
$ export DIGITALOCEAN_API_KEY=44dcafebeef45924cdd29d34943daf42182c1cd694f8e85f06561c6b12334a4f
```

This environment variable can also be permanently set in your .bashrc or user profile in a number of different ways.

Now, you should be able to run `vagrant up` using the DigitalOcean provider:

```
$ vagrant up --provider=digital_ocean
```

#### SSH Keys on DigitalOcean

In order to communicate with your new droplet, you must have an SSH key at `~/.ssh/id_rsa`. The `vagrant-digitalocean` plugin will attempt to add this key to your account under the name `Vagrant`. If the key at `~/.ssh/id_rsa` is already installed under a different name on your account, this will fail with the following error:

```
There was an issue with the request made to the DigitalOcean
API at:

Path: /v2/account/keys
URI Params: {:name=>"Vagrant", :public_key=>"ssh-rsa <redacted>\n"}

The response status from the API was:

Status: 422
Response: {"id"=>"unprocessable_entity", "message"=>"SSH Key is already in use on your account"}

```

To fix this issue, set the environment variable `DIGITALOCEAN_SSH_KEY` to the name of the key on your account which `~/.ssh/id_rsa` corresponds to. For example, if your key is currently installed with the name `Dewey`:

```
$ export DIGITALOCEAN_SSH_KEY=Dewey
```

This tells the DigitalOcean plugin to instead use the key named `Dewey` or install a new key named `Dewey` and inject that key when creating the new droplet.

Similarly, you will need to set an alternate key name (as above) if the key `Vagrant` is already in use on your account and it does not correspond to the key at `~/.ssh/id_rsa` on your host.

## Database seedfile

If `sql_seedfile` is specified in the `dev.yml` config, the file at this path will be uploaded and imported to the `pay` database before deploying the application.


DG Changes to this config:
in dev.yml:
	sql_seedfile: seedDB.sql
in Vagrantfile:
	change 2nd 8000 to 5000
	config.vm.network "forwarded_port", guest: 8000, host: 5000
in fabfile:
	added me as superuser
	sudo('mysql -e \'GRANT ALL ON *.* TO `deweyg`@`%` IDENTIFIED BY "zebra10"\'')

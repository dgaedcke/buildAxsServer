# Paysys Vagrant environment

DG Changes to this config:
in dev.yml:
	sql_seedfile: seedDB.sql
in Vagrantfile:
	change 2nd 8000 to 5000
	config.vm.network "forwarded_port", guest: 8000, host: 5000
in fabfile:
	added me as superuser
	sudo('mysql -e \'GRANT ALL ON *.* TO `deweyg`@`%` IDENTIFIED BY "zebra10"\'')



## Requirements

 - [Vagrant 1.8+](https://www.vagrantup.com/downloads.html)
 - [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
 - [Fabric](http://www.fabfile.org/)

## Creating a development environment

  1. Create the Virtualbox VM using Vagrant.

    ```
    $ vagrant up
    ```

  2. Run the Fabric task `deploy` against the newly created VM. We're also running the task `loadenv` with `dev` as an argument to load the `dev.yml` file which is also provided in this repository. This file specifies information such as the IP address of our Vagrant VM and the roles which it has defined. At the start of the deploy, you will be prompted for the passphrase for the SSH key provided in `files/id_deploy`.

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

## Database seedfile

If `sql_seedfile` is specified in the `dev.yml` config, the file at this path will be uploaded and imported to the `pay` database before deploying the application.

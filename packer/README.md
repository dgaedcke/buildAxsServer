# AXS Server Packer template

## Requirements

 - [Packer](https://www.packer.io/)

## Instructions

 1. Place the database seed file in `../files/payprod-live.sql.gz`.
 2. Build the Vagrant box. This will take a _long_ time.

    ```
    packer build -only=virtualbox-iso template.json
    ```

 3. Add the new box to Vagrant

    ```
    vagrant box add --force --name axs-server packer_virtualbox-iso_virtualbox.box
    ```

## Building for DigitalOcean

 1. Place the database seed file in `../files/payprod-live.sql.gz`.
 2. Export your DigitalOcean API key in your current environment (if needed).

    ```
    $ export DIGITALOCEAN_API_KEY=foo
    ```

 3. Build the image. This will take a _long_ time.

    ```
    packer build -only=digitalocean template.json
    ```

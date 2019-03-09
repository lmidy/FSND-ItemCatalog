# Udacity Item Catalog Assignment Objective

Develop a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users have the ability to post, edit, and delete their own items.

## Set Up

1. Clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).

2. Look for the *catalog* folder and replace it with the contents of this respository.

## Usage

Launch the Vagrant VM from inside the *vagrant* folder with:

`vagrant up`

Then access the shell with:

`vagrant ssh`

Then move inside the catalog folder:

`cd /vagrant/catalog`

Create database
`python database_setup.py`

Load data
`python lotsofgrudges.py`

Then run the application:

`python finalproject.py`

Browse the application at this URL:

`http://localhost:5000/`

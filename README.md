# Udacity Item Catalog Assignment Objective

Develop a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users have the ability to post, edit, and delete their own items.

## What you need

1. Clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).

2. Look for the *catalog* folder and replace it with the contents of this respository.

## How to run catalog

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

## Context
This catalog is all about sharing grudges, reading and sharing
Grudget = grudge bucket / aka grudge category
Grudge = a story worth sharing, a child of a grudget

CRUD Operations
--All users can create grudgets (grudge category)
--Only the author of the grudget can edit / delete a grudget
--Any authenticated user can create grudges against any existing grudgets

Browse the application at this URL:

`http://localhost:5000/`

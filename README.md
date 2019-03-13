## Udacity Item Catalog Assignment 

Develop a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users have the ability to post, edit, and delete their own items.

## What you need

1. Clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).

2. Look for the *catalog* folder and replace it with the contents of this respository.

## How to run catalog

Launch the Vagrant VM from inside the *vagrant* folder with:
```
vagrant up
```
Then access the shell with:
```
vagrant ssh
```
Then move inside the catalog folder:

```
cd /vagrant/catalog
```
Create Database with users
```
python database_setup.py
```
Load data:
```
python lotsofgrudges.py
```
If grudges loaded succesfully you should see:
```
all grudges loaded, woot woot
```
Then run the application:
```
python finalproject.py
```
Browse the application at this URL:
http://localhost:5000/

## Context of Item Catalog
This catalog is all about sharing grudges, reading others grudges

Grudget = grudge bucket,  aka grudge category

Grudge = a story worth sharing, a child of a grudget, akin to item

## Project Rubric


| AREA | CRITERIA | HOW THIS PROJECT MEETS SPECIFICATIONS |
| ------ | ------ |------ |
| API Endpoints | Does the project implement a JSON enpoint with all required content? | project contains 3 JSON endpoints 
| CRUD READ | Does website read category and item from a database | yes Grudgets are categories, and grudges are items
| CRUD CREATE | Does website include a form to update a record in db and correctly processes the form | yes logged in users can create grudgets and any grudge against any grudget
| CRUD UPDATE | Does website include a form to update a record in db and correctly processes the form | yes logged in users can update their own grudges, they can also update the title of someone elses authored grudget title
| CRUD DELETE | Website does include a form to edit/update a curretn record in db table and correctly processes submitted forms | Yes logged in user can delete their created grudges. Only creator of grudget can delete a grudget. 
| Authentication and Authorization| Website implement a 3rd party authentication and authorization service | Yes via Google Accounts
| Authentication and Authorization | login and logout | Yes shows login button if you dont have active session, shows logout button if you are already logged in
| Code Quality | PEP8 | Yes, on finalproject.py, not on database_setup.py
| Code Quality | Are comments present? | Yes, also include flash on header of page to validate functions
| README | README file included detailing all steps to run application | Yes
| Issues | Known issues | Google button/function does not work in incognito window. 

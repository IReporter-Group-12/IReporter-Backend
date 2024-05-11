# IReporter-Backend

# Instructions for working with Postgresql
1. To install Postgres, run the following commands from your Ubuntu terminal:

`sudo apt update` \
`sudo apt install postgresql postgresql-contrib libpq-dev`

2. Then confirm that Postgres was installed successfully:

 `psql --version`

3. Run this command to start the Postgres service:

 `sudo service postgresql start`

 4. Finally, you'll also need to log in as the postgres super user so that you are able to connect to the database from Flask:

`sudo -u postgres psql`

5. Change the password for the postgres user to 'password':

`ALTER USER postgres PASSWORD 'password';`

6. After exiting the psql terminal, install the PostgreSQL Explorer extension on VSCode (by Chris Kolkman), open it and add the following to the requested fields:

    - hostname: 127.0.0.1
    - postgresql user: postgres
    - password: password
    - port number: 5432
    - connection: standard
    - database to connect: ireporter-db

7. To view a specific table, right-click the table, click select and add the number of entries you would like to see.

# Creating a secret key
1. In the flask-app directory, create a .env file in which the secret key will be stored.
2. In your terminal, open the python command line and add the following commands:

```
    import secrets

    secret_key = secrets.token_urlsafe(32)

    print("Random Secret Key:", secret_key)
```
3. Copy the generated secret key and add the following to the .env file:

`SECRET_KEY = [add your secret key]`
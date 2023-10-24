Generate new key and a self signed certificate(recommended, one is already provided inside apache-config/certs):
 - change directory to apache-config/certs `cd apache-config/certs`
 - run command `sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout development.key -out development.crt`
 - press enter to bypass all except Common Name, for this enter `127.0.0.1` for local development

Both http and https are served on ports 8000 and 8001 respectively, for testing run:
 - `docker build -t mechanics-backend .`
 - `docker-compose up`
 - navigate to `https://localhost:8001/api/v1/users` (for example)
 - browser may prompt to accept certificate, if not done already
 - verify that https is shown in the url
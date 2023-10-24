# Verification Frontend Integration

Run backend following the above guideline.\
Do *NOT* load `data/app.json` for testing frontend integration.\
Please use `data/integration-test-data.json`.\
See details from below.

For production, no data is needed.

# Deployment

## Run MySQL Server
Run MySQL Server before start the app.

## Configure database
Set the environmental variables:\
`DB_NAME`: database name, default: mechanics\
`DB_HOST`: MySQL server, default:localhost\
`DB_PORT`: MySQL Server port, default: 3306\
`DB_USER`: MySQL login username, default: mechanics\
`DB_PASSWORD`: MySQL login password, default: password

## Configure SMTP server
Set the environmental variables:\
`SMTP_HOST`: smtp host, required\
`SMTP_PORT`: smtp port, default: 25\
`SMTP_SECURE`: smtp is secure flag, default: False\
`SMTP_USERNAME`: smtp username, optional\
`SMTP_PASSWORD`: smtp password, optional\
`SMTP_EMAIL_FROM`: smtp email sender, required

## Configure Azure AD
Set the environmental variables:\
`AZURE_CLIENT_ID`: the azure tenant id, required.\
`AZURE_TENANT_ID`: the azure ad app client id, required

## Create environment and Install dependencies
1. Run command `python -m venv env`.
1. Use virtual environment.
    - Windows: `env\Scripts\activate`.
    - Linux/OS X: `. env/bin/activate`.
1. Run command `python -m pip install --upgrade pip` to ensure latest pip.
1. Run command `pip install -r requirements.txt` to install dependencies.

## Migrate database
Run command `python manage.py migrate app`.\
Ensure that database is empty with no tables before run this command.

## Run Django Server
Run command `python manage.py runserver`.

## Local Test
If test in local environment, add `127.0.0.1` to `ALLOWED_HOSTS` in `settings.py`.

## Run docker
1. Run command `docker build -t mechanics-backend .` to build docker image.
2. Run command `docker-compose up -d` after building image.
3. Run command `docker-compose exec mechanics_backend python manage.py migrate app` to crate db.
4. Run command `docker-compose exec mechanics_backend python manage.py loaddata data/integration-test-data.json` to set sample data.

# Verification
## Load sample data
Run command `python manage.py loaddata data/app.json`.\
Ensure that Migrate database have done and all tables are empty before run this command.

## Load frontend integration test data
Run command `python manage.py loaddata data/integration-test-data.json`.\
Ensure that Migrate database have done and all tables are empty before run this command.\
`integration-test-data.json` has more projects and vins for testing.

## Set postman
1. Open postman.
1. Import `MechanicsAPI.postman_collection.json`.
1. Import `MechanicsAPI.postman_environment.json`.

## Postman environment
`host`: api host url.\
`admin-token`: admin user token.\
`standard-token`: standard user token.\
`invalid-token`: invalid user token.

## Verification
Send postman request top to bottom.\
Sample data is ready for non-stop verification with postman.

## Authorization tokens
### Admin
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwiaWQiOjEsIm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInRodW1ibmFpbFVybCI6bnVsbH0.3Aq4TFin4OwWEgaHzRQf2ClJ_CM-L7cvUpqiH-CRBIo

### Standard
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InN0YW5kYXJkQGV4YW1wbGUuY29tIiwiaWQiOjIsIm5hbWUiOiJzdGFuZGFyZCIsInJvbGUiOiJzdGFuZGFyZCIsInRodW1ibmFpbFVybCI6bnVsbH0.qgYGdQ-Nazj3f3dBxmvgXXIJDFNWwoIXeWpcdo0BXGY

## Changelog

### Backend Update - New Design

 - added asynchronous file import code
 - implement the changes in the endpoints `/mappings`
 


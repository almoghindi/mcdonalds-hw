# Mcdonald's - Home assignment

This project processes customer data from a mobile app, including:
Purchase history (timestamp + amount)
Session history (timestamp of each app open)
It computes customer-level aggregates over the past 8 weeks, and assigns each customer to a messaging bucket based on configurable thresholds.

# Architecture diagram and description
![image](https://github.com/user-attachments/assets/2a8015bc-9145-4fbc-ab6e-8e159a574831)

### Core Components:
- **Database** - Stores all raw and processed data, Including 4 Entities/Tables - Customer, AppSession, Purchase and Messages.
- **Scheduler** - Runs periodic tasks automatically, Triggers the aggregation and messaging process at scheduled intervals (every 8 weeks).
- **FastAPI server** - REST API server for receiving events from the mobile app, running data seeding, and triggering aggregations for your testing.
- **Generate data** - A script that writes 10000 unique customers to a database, with sessions per week according to Poisson distribution, and purchases according to Log-normal distribution.
- **Aggregation service** - Service for processing raw data, reads all raw sessions and purchases, aggregates them per customer, then decides message type and calls the send message method available in the messages service.
- **Messaging service** - This service is responsible for sending SMS (no SMS API integration) and saving messages into the database.
- **logger** - Application activity tracking, testing, debugging, core sample layer for future use.

### How components fit together ?
- **Scheduler** - Runs on a different thread, then triggers aggregation_and_messaging method, so it does its magic to aggregate every customer and send an SMS message every 8 weeks. 
- **Aggregation service** - Asking the database for the raw data of customers and sessions, than aggregating every customer based on the LOW_SPEND_THRESHOLD and HIGH_ACTIVITY_THRESHOLD parameters, than calls the messaging service after deciding which message should be sent.
- **Messaging service** - Getting customer and message type, than senging SMS to the customer, and saves the message in the database for tracking.
- **Generate data** - Generates customers, sessions and purchases due to demands and saves them into the db.
- **FastAPI server** - The template is expandable for future uses, including catching client requests like "Session created" due to the app opening, and purchasing in the application. You can test my features as well.
- **Database** - integrating with the services for generating syntethic data, read raw data and saving messages per customer.

### Folder Structure
```bash
mcdonalds-hw/
├── .github/ # Template for future CI/CD using Github Actions.
├── albemic/ # Configurations for migrations.
├── app/ # Core logic of the application.
├── tests/ # Every testing file here.
```
# Tech choices:
- **Language** - *Python* 3.10+ was chosen for its modern features and suitability for data-centric backend systems. The language offers a rich ecosystem of libraries for data processing, database interaction, web development, and scheduling.
- **Database** - *PostgreSQL* was selected for its reliability, support for relational data, and ability to handle time-series aggregations efficiently. It supports advanced indexing and analytical queries, and is trusted in production for data integrity, performance and scaling.
- **Libraries** -
  - *SQLAlchemy*: A powerful and popular ORM, great for flexability, aggregations and complex queries, ideal for analytics-focused projects, supports migrations as well.
  - *Alembic*: Chosen to manage database schema changes safely, works well with SQLAlchemy (developed by the same group).
  - *python-dotenv*: Selected to manage configuration and environment variables in a clean, secure, and independent way.
  - *psycopg2*: Chosen because it's the most widely used and reliable PostgreSQL adapter (driver) for Python.
  - *FastAPI*: Selected as the web framework for this project because it's fast (there is a reason why it calls fastapi), lightweight, and perfectly suited for building modern REST APIs.
  - *numpy*: Provides powerful tools for numerical data generation and manipulation.
  - *schedule*: Chosen for its simplicity — it runs recurring tasks directly in the app without extra setup, perfect for lightweight job automation.
  - *pytest*: Selected for its popularity, simplicity and power in writing and running tests. It makes it easy to test data logic like aggregation and messaging, ensuring the system works correctly as it evolves.
  - *uvicorn*: ASGI server used to run FastAPI apps.
- **Scheduling approach** - The *schedule* library is used to periodically trigger the customer aggregation and messaging logic. It runs inside the app, making it a simple and effective solution for automating recurring tasks like weekly engagement analysis.

# Instructions:
In order to the project to run, you must have python 3.10+ installed in your PC.
### Instructions to setup and run the project (guide for windows users):

1. Create an Virtual environment
```bash
python -m venv .venv
./.venv/Scripts/activate
```
2. Install Required librarries
```bash
pip install -r requirements.txt
```
3. Lunch the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

To make an Data generation ,migration and aggregation you have 2 options: 
- Call the routes using Swagger (http://localhost:8000/docs):
![Screenshot 2025-05-14 134608](https://github.com/user-attachments/assets/74646344-8df8-44da-82c7-343fb35b7f48)

or
- Call the routes using api calling platform (Postman/ThunderClient):
  - For Generate data, call the route ```/seed```.
  - For Spin up the schema (or migrate), call thw route ```/migrations```.
  - For Run the aggregation & populate messages, call thw route ```/aggregate-and-message-test``` (or wait 8 weeks).

# Sample output
### Aggregation completed screenshot:
![Screenshot 2025-05-13 182939](https://github.com/user-attachments/assets/fb3a62ee-6d44-4c0b-b0a7-bc6bbc1e93de)

### Data generation completed screenshot: 
![Screenshot 2025-05-13 193230](https://github.com/user-attachments/assets/3238e3c0-7e9e-44e7-8f91-bded3bc51738)

### Sucessfull tests:
![Screenshot 2025-05-13 201645](https://github.com/user-attachments/assets/cb446fba-d2bd-4fe1-b8ad-3585a46d809a)

### Video showing Aggregation and messaging running:
https://github.com/user-attachments/assets/09f2457a-437d-4c16-919b-379a5c1941ba

### Video showing generate data running:
https://github.com/user-attachments/assets/914a9158-5ea5-411b-a2fc-59c131861265

# Assumptions:
- **Time Zones**: The timestamps are all in UTC, any datetime is universal and treated as UTC when processing.
- **Data Anomalies**: Invalid or missing timestamps are ignored, Purchases or sessions without a timestamp or customer ID are skipped during aggregation.
- **Edge Cases**: 
  - Customers with no sessions or purchases are still included in the results with default values (e.g., 0 spend, 0 sessions).
  - Division by zero is avoided when calculating averages by setting session averages to 0 if no sessions exist.
  - Datetimes with no timezone info, Treated as UTC by default to avoid inconsistencies.
  - Future-dated events, sessions or purchases with timestamps in the future are excluded from calculations.

# Future enhancements:
- **AI Integrations**: Add AI capabilities to make the system behavior-driven. A ML model can be fine-tuned to predict customer behavior based on historical data, replacing static thresholds with adaptive logic. Additionally, a smart messaging system powered by an LLM can analyze customer patterns, decide which message type to send, and even generate personalized message content. AI can also support anomaly detection by learning how to identify irregularities or edge cases in the data, as outlined in the Assumptions section. With the right prompts or training, the system could detect outliers and handle data issues more intelligently.
- **Real SMS integration**: connect to a Twilio (or a different provider) as an SMS provider (consider renting a company number).
- **Unit tests coverage**: Implmented basic unit tests for the services of messagging and aggregation. maybe extend it with more comprehensive tests, and add more types of tests like loading tests, integration tests (with the different services) and 'end-to-end' tests for the system itself and the different flows.
- **CI/CD pipeline**: Implemented template for CI/CD using Github Actions, added automated testing to github pushes, and deployed to a cloud service like AWS after every test is successful. Add automated testing and deployment using GitHub Actions or similar tools for reliable development workflows.
- **Scaling**: Docker file added in order to have a consistent deployment across development for the API, adding Kubernetes will help with horizontal scaling, job scheduling and helps to extend the scale to a different level. In term of the database, this is one of the reasons that PostgreSQL chosed, it supports a large scale of data and scales easily when needed, really optimized for production.
- **User segmentation logic**: Add more segmentation criteria for even more personlized messages, not only BOOST or REWARD but even more personal per people, having the peoples that falls in the middle get messages as well.
- **More comprehensive customers tracking**: Not ony session and purchases, but liked products, added to basket, watched products and more.


### root files
__init__.py -> Instantiates an instance of Broadcaster as well as includes the factory function for the FastAPI app. Within this function we also create a celery app before adding the routers.

ai.py -> OpenAI helper functions for message dicts, as well as an AI class we use for making chat completion requests

config.py -> lru_cache get_settings function that returns a config class based on the FASTAPI_CONFIG mode that holds all the environment variables and constants

db.py -> Instantiates a supabase client for interacting with the managed database

dependencies.py -> Functions to be used with FastAPI Depends in endpoint definitions such as get_db

main.py -> Creates "app" from the FastAPI app factory and sets "celery" to app.celery_app

### /routes

Contains the FastAPI routers with the endpoints. 
routes/v1/api.py -> loads the individual routers from each module in the /routes/v1/endpoints/ folder using the appropriate prefix for each.


### /schemas

Contains the Pydantic models that are used for validating and serializing the input and output data of the API endpoints


### /models

Contains the Pydantic models that are used for mapping to the tables contained in our managed Supabase Postgresql database, which is accessed using the Supabase client that is built on Postgrest.
Modules should be named the same as the table they map to in the database.

### /tasks


### /utils


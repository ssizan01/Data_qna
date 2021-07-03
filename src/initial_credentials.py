# Initialize the clients
import os
from google.api_core.client_options import ClientOptions
from google.cloud import bigquery
from google.cloud.dataqna import AutoSuggestionServiceClient, Question, QuestionServiceClient, SuggestQueriesRequest, UpdateUserFeedbackRequest, UserFeedback
from google.cloud import bigquery_storage
from config import project_name,tables_list
from pathlib import Path
from glob import glob


base_path = Path(__file__).parent
secrets_path = (base_path / "../secrets").resolve()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = glob(str(secrets_path) + "/*.json")[0]
#print(glob(str(secrets_path) + "/*.json")[1])
location = "us"  # "us" or "eu"
client_options = ClientOptions(api_endpoint=f"{location}-dataqna.googleapis.com:443")
suggest_client = AutoSuggestionServiceClient(client_options=client_options)
questions_client = QuestionServiceClient(client_options=client_options)
bq_client = bigquery.Client()
bqstorageclient = bigquery_storage.BigQueryReadClient()
parent = questions_client.common_location_path(project_name, location)
import os
import streamlit as st
from google.api_core.client_options import ClientOptions
from google.cloud import bigquery
from google.cloud.dataqna import AutoSuggestionServiceClient, Question, QuestionServiceClient, SuggestQueriesRequest, UpdateUserFeedbackRequest, UserFeedback
from google.cloud import bigquery_storage
from config import project_name,tables_list
from pathlib import Path
from glob import glob
import matplotlib.pyplot as plot
import altair as alt
import pickle

base_path = Path(__file__).parent
secrets_path = (base_path / "../secrets").resolve()


table_dic ={}
for item in tables_list:
    table_dic[item.partition('.')[2]] = f"//bigquery.googleapis.com/projects/{project_name}/datasets/{item.partition('.')[0]}/tables/{item.partition('.')[2]}"


dataset_name = st.sidebar.selectbox(
    'Select Dataset',
    list(table_dic.keys())
)

# Initialize the clients

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = glob(str(secrets_path) + "/*.json")[0]
location = "us"  # "us" or "eu"
client_options = ClientOptions(api_endpoint=f"{location}-dataqna.googleapis.com:443")
suggest_client = AutoSuggestionServiceClient(client_options=client_options)
questions_client = QuestionServiceClient(client_options=client_options)
bq_client = bigquery.Client()
bqstorageclient = bigquery_storage.BigQueryReadClient()
parent = questions_client.common_location_path(project_name, location)


if os.path.exists("objs.pkl"):
    print(f'data comes here 00')
    with open('objs.pkl','rb') as f:  # Python 3: open(..., 'rb')
            user_input = pickle.load(f)


user_input = None
if user_input is not None:
    print(f'user input after pickling is {user_input}')

@st.cache()
def get_df_from_question(user_input):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = glob(str(secrets_path) + "/*.json")[0]
    location = "us"  # "us" or "eu"
    client_options = ClientOptions(api_endpoint=f"{location}-dataqna.googleapis.com:443")
    suggest_client = AutoSuggestionServiceClient(client_options=client_options)
    questions_client = QuestionServiceClient(client_options=client_options)
    bq_client = bigquery.Client()
    bqstorageclient = bigquery_storage.BigQueryReadClient()
    parent = questions_client.common_location_path(project_name, location)

    question = Question(scopes=[table_dic[dataset_name]], query=user_input)
    question_response = questions_client.create_question(parent=parent, question=question)
    question_resouce_url = question_response.name + "/userFeedback"
    print(question_resouce_url)
    plain_english_interpretation = question_response.interpretations[0].human_readable.generated_interpretation.text_formatted
    raw_sql = question_response.interpretations[0].data_query.sql
    sql_query = question_response.interpretations[0].data_query.sql.replace('\n', ' ')

    df = (
        bq_client.query(sql_query)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )


    return df,raw_sql,plain_english_interpretation,question_resouce_url

@st.cache()
def get_suggestions(user_input):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = glob(str(secrets_path) + "/*.json")[0]
    location = "us"  # "us" or "eu"
    client_options = ClientOptions(api_endpoint=f"{location}-dataqna.googleapis.com:443")
    suggest_client = AutoSuggestionServiceClient(client_options=client_options)
    questions_client = QuestionServiceClient(client_options=client_options)
    bq_client = bigquery.Client()
    bqstorageclient = bigquery_storage.BigQueryReadClient()
    parent = questions_client.common_location_path(project_name, location)

    suggestions_response = suggest_client.suggest_queries(SuggestQueriesRequest(parent=parent, scopes=[table_dic[dataset_name]],query=user_input,suggestion_types = ['TEMPLATE']))
    #suggested_query = suggestions_response.suggestions[0].suggestion_info.annotated_suggestion.text_formatted
    suggestions_list = []
    for suggestion in suggestions_response.suggestions:
        suggestions_list.append(suggestion.suggestion_info.annotated_suggestion.text_formatted)
    #print(f'lenght of suggestions is {suggestions_list}')
    return suggestions_list
#-------------------------------------------


def get_text():
    input_text = st.text_input("Type in your question here:")
    return input_text


st.title("""
Data Qna Demo
""")

st.write(f"Your current selected DataSet is {dataset_name}")

user_input = get_text()
#print(f'user input is {user_input}')
#suggestions_list = get_suggestions(user_input=user_input)

generate_suggestion = st.button('Generate Suggestion', key=1)
if generate_suggestion:
    user_input = st.text_input('Suggested Query is:', value=get_suggestions(user_input=user_input)[0], key=1)
    with open('objs.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
        print(f'pickling file')
        pickle.dump(user_input, f)


if user_input == '':
    pass
else:
    try:
        dataframe,raw_sql,plain_english_interpretation,question_resouce_url = get_df_from_question(user_input=user_input)
        st.write(f'Plain english interpretation for what you typed is ** {plain_english_interpretation} **')
        st.subheader('Result:')

        dataframe
        df_columns = dataframe.columns.values.tolist()
        if len(df_columns) >= 2:
            c = alt.Chart(dataframe).mark_bar().encode(x=df_columns[1], y=df_columns[0])
            st.altair_chart(c, use_container_width=True)
        else:
            print('data is here')
            c = alt.Chart(dataframe).mark_text().encode(x=df_columns[0])
            st.altair_chart(c)
        print(f'size of the dataframe is {dataframe.shape}')

        st.subheader("""
        Following is the interpreted SQL:
        """)
        textsplit = raw_sql.splitlines()
        for x in textsplit:
            st.write(x)

        radio_options = ['Yes','No']
        feedback_button = st.radio('Did the Query work as expected?', radio_options)
        if feedback_button == "Yes":
            user_comments = st.text_area('Comment here')
            user_feedback = UserFeedback(name=question_resouce_url,rating=1, free_form_feedback=user_comments)
            questions_client.update_user_feedback(request=UpdateUserFeedbackRequest(user_feedback=user_feedback,update_mask={'paths': ["rating","free_form_feedback"]}))
        else:
            st.text_area('Comment here')
            user_comments = st.text_area('Comment here')
            user_feedback = UserFeedback(name=question_resouce_url,rating=2, free_form_feedback=user_comments)
            questions_client.update_user_feedback(request=UpdateUserFeedbackRequest(user_feedback=user_feedback,update_mask={'paths': ["rating","free_form_feedback"]}))

    except:
        st.error(f'Please enter a valid question for the selected Dataset')


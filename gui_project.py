import pickle
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from wordcloud import WordCloud
data_full = pd.read_csv('./data_full.csv')
data_tmp = pd.read_csv('./data_tmp.csv')
stopwords = list()
with open('./vietnamese-stopwords.txt', mode='r', encoding='utf-8') as f:
  for line in f:
    stopwords.append(line.strip('\n'))
with open('./model_normal_2.pkl', 'rb') as f:
  model_normal_2 = pickle.load(f)
with open('./label_encoder_normal.pkl', 'rb') as f:
  label_encoder_normal = pickle.load(f)
with open('./tfidf_normal.pkl', 'rb') as f:
  tfidf_normal = pickle.load(f)
def predict_text(text):
  return label_encoder_normal.inverse_transform(model_normal_2.predict(tfidf_normal.transform([text])))[0]
def show_information_restaurant(id):
  try:
    data_check = data_full[data_full['IDRestaurant'] == id]
    st.write(f'Name Restaurant: {data_check.iloc[0]["Restaurant"]}')
    st.write(f'Address Restaurant: {data_check.iloc[0]["Address"]}')
    st.write(f'Total Vote: {data_check.shape[0]}')
    vote_positive = data_check[data_check["Rating"] > 7.8].shape[0] + data_tmp[((data_tmp['Sentiment'] == 'Positive') & (data_tmp['IDRestaurant'] == id))].shape[0]
    vote_negative = data_check[data_check["Rating"] < 6.8].shape[0] + data_tmp[((data_tmp['Sentiment'] == 'Negative') & (data_tmp['IDRestaurant'] == id))].shape[0]
    st.write(f'Vote Positive: {vote_positive}')
    st.write(f'Vote Negative: {vote_negative}')
    st.write(f'Average Rating: {round(data_check["Rating"].mean(), 1)}')
    new_data_positive = pd.concat([data_check[data_check["Rating"] > 7.8], data_tmp[((data_tmp['Sentiment'] == 'Positive') & (data_tmp['IDRestaurant'] == id))]], axis=0, ignore_index=True)
    new_data_negative = pd.concat([data_check[data_check["Rating"] < 6.8], data_tmp[((data_tmp['Sentiment'] == 'Negative') & (data_tmp['IDRestaurant'] == id))]], axis=0, ignore_index=True)
    if vote_positive > 0:
      st.write('WordCloud Positive:')
      wordcloud = WordCloud(background_color='white', stopwords=stopwords, max_words=30).generate(' '.join(new_data_positive['Comment'].tolist()))
      st.image(wordcloud.to_array(), width=600)
    if vote_negative > 0:
      st.write('WordCloud Negative:')
      wordcloud = WordCloud(background_color='white', stopwords=stopwords, max_words=30).generate(' '.join(new_data_negative['Comment'].tolist()))
      st.image(wordcloud.to_array(), width=600)
  except:
    st.write(f'ID Restaurant: {id} not found')
# Write code create sidebar selectbox
st.set_page_config(page_title="Sentiment Analysis Application", page_icon="🧊", layout="wide", initial_sidebar_state="expanded")
st.title("Sentiment Analysis")
st.sidebar.title("Options in application Sentiment Analysis")
selectbox = st.sidebar.selectbox("Projects", ["Visualization Dataset", "Predict New Feedback", "Show Evaluation"])
if selectbox == "Visualization Dataset":
  st.subheader("Visualization Dataset")
  id_restaurant = st.number_input(label="ID Restaurant", placeholder="Enter ID Restaurant", step=1)
  if isinstance(id_restaurant, int):
    if id_restaurant > 0:
      show_information_restaurant(id_restaurant)
    else:
      st.warning('ID Restaurant must be greater than 0', icon="⚠️")
  else:
    st.error('ID Restaurant must be integer', icon="⚠️")
elif selectbox == "Predict New Feedback":
  st.subheader("Predict New Feedback")
  radio_option = st.radio("Choose your option:", ["Enter your feedback", "Upload file"])
  if radio_option == "Enter your feedback":
    text_predict = st.text_area(label="Feeback", placeholder="Enter New Feedback")
    if (text_predict != "") or (text_predict is None):
      st.snow()
      predict_feedback = predict_text(text_predict)
      st.write(f'Predict Feedback: {predict_feedback}')
  else:
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'csv'])
    if uploaded_file is not None:
      if Path(uploaded_file.name).suffix == '.txt':
        text_predict = uploaded_file.read().decode('utf-8')
        list_text_predict = text_predict.split('\n')
        list_sentiment = list()
        if len(list_text_predict) > 0:
          for text in list_text_predict:
            predict_feedback = predict_text(text.strip('\n'))
            list_sentiment.append(predict_feedback)
          list_feedback = pd.DataFrame({'Feedback': list_text_predict, 'Sentiment': list_sentiment})
          st.dataframe(list_feedback, width=600)
        else:
          st.warning('File is empty')
      else:
        data_feedback_csv = pd.read_csv(uploaded_file)
        try:
          data_feedback_csv['Sentiment'] = data_feedback_csv['Feedback'].apply(lambda x: predict_text(x))
          st.dataframe(data_feedback_csv, width=600)
        except:
          st.warning('File not found or format file is not correct', icon="⚠️")
else:
  st.subheader("Show Evaluation")
  st.write("This is the classification report of Naive Bayes model (BEST model):")
  st.image('./classification_report_nb.png', width=600)
  st.write("This is the classification report of Logistic Regression model:")
  st.image('./classification_report_lr.png', width=600)
  st.write("This is the classification report of Random Forest model:")
  st.image('./classification_report_rf.png', width=600)
  st.write("This is the classification report of XGBoost model:")
  st.image('./classification_report_xgb.png', width=600)

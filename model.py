import joblib
import pandas as pd
import numpy as np
import os

# Load the necessary models and data
# user_final_rating = joblib.load(open("pickle/user_final_rating.pkl", "rb"))

model_path = os.path.join("pickle", "user_final_rating.pkl")
user_final_rating = joblib.load(open(model_path, "rb"))

df_final = joblib.load(open("pickle/df_final.pkl", "rb"))
tfidf = joblib.load(open("pickle/tfidf_vectorizer.pkl", "rb"))
xgb = joblib.load(open("pickle/best_model_xgb.pkl", "rb"))

def product_recommendations_user(user_name):
    """Returns top 5 recommended products for a given user along with sentiment scores"""
    if user_name not in user_final_rating.index:
        return f"The user '{user_name}' does not exist. Please provide a valid user name."

    top20_recommended_products = list(user_final_rating.loc[user_name].sort_values(ascending=False)[:20].index)

    
    df_top20_products = df_final[df_final.name.isin(top20_recommended_products)].drop_duplicates(subset=['cleaned_review'])

    
    if df_top20_products.empty:
        return "No recommendations found for this user."

    # Transform text using TF-IDF
    X = tfidf.transform(df_top20_products['cleaned_review'])
    X_df = pd.DataFrame(X.toarray(), columns=tfidf.get_feature_names_out())

    
    # Include numerical features
    # X_num = df_top20_products[['review_length']].reset_index(drop=True)

    X_num = df_top20_products[['review_length','vader_sentiment']]

    # Reset indices before concatenation
    X_df = X_df.reset_index(drop=True)

    X_num = X_num.reset_index(drop=True)

    # X_df = X_df.reset_index(drop=True)

    df_top_20_products_final_features = pd.concat([X_df, X_num], axis=1)

    # Predict sentiment
    df_top20_products['predicted_sentiment'] = xgb.predict(df_top_20_products_final_features)

    # Process sentiment results
    df_top20_products['positive_sentiment'] = df_top20_products['predicted_sentiment'].apply(lambda x: 1 if x == 1 else 0)

    pred_df = df_top20_products.groupby(by='name').sum()
    pred_df = pred_df.rename(columns={'positive_sentiment': 'pos_sent_count'})

    pred_df['total_sent_count'] = df_top20_products.groupby(by='name')['predicted_sentiment'].count()
    pred_df['pos_sent_percentage'] = np.round(pred_df['pos_sent_count'] / pred_df['total_sent_count'] * 100, 2)

    pred_df = pred_df.reset_index()

    # Return top 5 recommended products
    return pred_df.sort_values(by="pos_sent_percentage", ascending=False)[:5][["name", "pos_sent_percentage"]]

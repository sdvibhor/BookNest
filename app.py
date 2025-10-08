from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load data
popular_books_df = pickle.load(open('processed-data/popular-books.pkl', 'rb'))

# Try to load recommendation data if available
try:
    pt = pickle.load(open('processed-data/pt.pkl', 'rb'))
    books = pickle.load(open('processed-data/books.pkl', 'rb'))
    similarity_score = pickle.load(open('processed-data/similarity_score.pkl', 'rb'))
    recommendation_available = True
except:
    recommendation_available = False

@app.route('/')
def index():
    return render_template('index.html', 
                           book_name=list(popular_books_df['Book-Title'].values),
                           author_name=list(popular_books_df['Book-Author'].values),
                           image_url=list(popular_books_df['Image-URL-M'].values),
                           votes=list(popular_books_df['Num-Rating'].values),
                           rating=list(popular_books_df['Avg-Rating'].values))

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    if not recommendation_available:
        return render_template('recommend.html', error=True, message="Recommendation system is not available.")
    
    user_input = request.form.get('book_name')
    
    # Check if book exists in our dataset
    if user_input not in pt.index:
        return render_template('recommend.html', error=True, message=f"'{user_input}' not found in our database. Please try another book.")
    
    # Get the index of the book
    index = np.where(pt.index == user_input)[0][0]
    
    # Get similarity scores and sort them
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:8]
    
    # Get book details for recommended books
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)
    
    return render_template('recommend.html', data=data)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')
    if query:
        suggestions = popular_books_df[popular_books_df['Book-Title'].str.contains(query, case=False, na=False)]['Book-Title'].unique().tolist()
    else:
        suggestions = []
    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    app.run(debug=True)

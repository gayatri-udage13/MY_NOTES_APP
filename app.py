from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/notesdb")
mongo = PyMongo(app)

@app.route('/')
def index():
    notes = mongo.db.notes.find()
    return render_template('index.html', notes=notes)

@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        notes = mongo.db.notes.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}}
            ]
        })
        return render_template('index.html', notes=notes)
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_note():
    title = request.form['title']
    content = request.form['content']
    mongo.db.notes.insert_one({'title': title, 'content': content})
    return redirect(url_for('index'))

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_note(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        mongo.db.notes.update_one({'_id': ObjectId(id)}, {'$set': {'title': title, 'content': content}})
        return redirect(url_for('index'))
    note = mongo.db.notes.find_one({'_id': ObjectId(id)})
    return render_template('edit_note.html', note=note)

@app.route('/delete/<id>')
def delete_note(id):
    mongo.db.notes.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

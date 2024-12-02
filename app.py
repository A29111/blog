from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_restful import Api, Resource
from models import db, Diary
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# 設定資料庫連線
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 資料庫初始化
with app.app_context():
    db.create_all()

# RESTful API 定義
class DiaryAPI(Resource):
    # 取得所有日記或單篇日記
    def get(self, diary_id=None):
        if diary_id:
            diary = Diary.query.get(diary_id)
            if not diary:
                return {'message': 'Diary not found'}, 404
            return {
                'id': diary.id,
                'title': diary.title,
                'author': diary.author,
                'content': diary.content,
                'date': diary.date.strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            diaries = Diary.query.all()
            return [{
                'id': d.id,
                'title': d.title,
                'author': d.author,
                'content': d.content,
                'date': d.date.strftime('%Y-%m-%d %H:%M:%S')
            } for d in diaries]

    # 新增日記
    def post(self):
        data = request.json
        new_diary = Diary(
            title=data['title'],
            author=data['author'],
            content=data['content'],
            date=datetime.now()
        )
        db.session.add(new_diary)
        db.session.commit()
        return {'message': 'Diary created', 'id': new_diary.id}, 201

    # 更新日記
    def put(self, diary_id):
        data = request.json
        diary = Diary.query.get(diary_id)
        if not diary:
            return {'message': 'Diary not found'}, 404
        diary.title = data['title']
        diary.author = data['author']
        diary.content = data['content']
        db.session.commit()
        return {'message': 'Diary updated'}

    # 刪除日記
    def delete(self, diary_id):
        diary = Diary.query.get(diary_id)
        if not diary:
            return {'message': 'Diary not found'}, 404
        db.session.delete(diary)
        db.session.commit()
        return {'message': 'Diary deleted'}

# 註冊 API
api.add_resource(DiaryAPI, '/api/diaries', '/api/diaries/<int:diary_id>')

# 前端路由
@app.route('/')
def index():
    diaries = Diary.query.all()
    return render_template('index.html', diaries=diaries)

@app.route('/new', methods=['GET', 'POST'])
def new_diary():
    if request.method == 'POST':
        new_diary = Diary(
            title=request.form['title'],
            author=request.form['author'],
            content=request.form['content'],
            date=datetime.now()
        )
        db.session.add(new_diary)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new.html')

@app.route('/view/<int:diary_id>')
def view_diary(diary_id):
    diary = Diary.query.get_or_404(diary_id)
    return render_template('view.html', diary=diary)

@app.route('/edit/<int:diary_id>', methods=['GET', 'POST'])
def edit_diary(diary_id):
    diary = Diary.query.get_or_404(diary_id)
    if request.method == 'POST':
        diary.title = request.form['title']
        diary.author = request.form['author']
        diary.content = request.form['content']
        db.session.commit()
        return redirect(url_for('view_diary', diary_id=diary.id))
    return render_template('edit.html', diary=diary)

if __name__ == '__main__':
    app.run(debug=True)

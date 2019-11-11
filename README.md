# bernie_eats
文化祭用お好み焼き注文管理システム

デモサイト : [https://bernie-eats-demo.herokuapp.com/](https://bernie-eats-demo.herokuapp.com/)

本番サイト : [https://bernie-eats.herokuapp.com/](https://bernie-eats.herokuapp.com/)

急遽本システムを作成することとなり、３日で作成し、機能追加や変更があったため要リファクタリングの必要がある

時間があったとき、実装したくてもできなかった機能等を実装したい

## 機能一覧
- お好み焼き注文
- 注文状況の確認
- 調理、配達、注文キャンセル等のステータス管理
- 売り上げ集計
- ステータスログ表示

## ローカル環境構築方法
```bash
# ソースコードをクローン
$ git clone https://github.com/jonki324/bernie_eats.git

# プロジェクトフォルダに移動
$ cd bernie_eats

# 仮想環境作成
$ pipenv sync --dev

# 環境変数設定
$ export FLASK_APP=run.py
$ export FLASK_ENV=development

# データベース初期化
$ flask shell
>>> from application.models import db
>>> db.create_all()

# アプリ起動
$ pipenv run python run.py
```

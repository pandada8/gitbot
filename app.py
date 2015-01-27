from flask import Flask,request,g
import json
from flask import g

app = Flask(__name__)

def load_repos():
    with open('repos.json') as fp:
        repos = json.load(fp)
        g.repos = {}
        for i in repos:
            g.repos[i['key']] = i
            app.logger.debug('Found Repo in {path} with key: {key}'.format(**i))
        app.logger.info('Load {} repos successfully'.format(len(g.repos)))



@app.route('/payload',methods=['POST'])
def payload():
    key = request.args.get('key')
    return ''



if __name__ == "__main__":
    with app.app_context():
        load_repos()
    app.run(debug=True)

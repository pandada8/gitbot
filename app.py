from flask import Flask,request,g
import json
import logging
from flask import g
import hmac
import hashlib
import yaml
import os
import subprocess

def md5(string):
    return hashlib.md5(string.encode('UTF8')).hexdigest()

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
logging.basicConfig()

def load_repos():
    global repos
    repos = {}
    with open('config.yaml') as fp:
        _repos = yaml.load(fp)
        for i in _repos:
            repos[md5(i['path'])] = i
            app.logger.debug('Found Repo in {} with key: {}'.format(i['path'], md5(i['path'])))
        app.logger.info('Load {} repos successfully'.format(len(repos)))

load_repos()

@app.route('/payload',methods=['POST'])
def payload():
    global repos
    if request.headers.get('X-GitHub-Event','') != 'push':
        return (json.dumps({
            'err':1,
            'msg':'Wrong Action Posted'
        }),400)
    elif not (request.args.get('s') and request.args.get('s') in repos):
        return (json.dumps({
            'err':2,
            'msg':"Wrong Repo"
        }),400)
    else:
        repo = repos[request.args.get('s')]
        sign = request.headers.get('X-Hub-Signature').split('=')[1]
        sign_payload = hmac.new(repo['secret_key'].encode('UTF-8'),request.data,'sha1').hexdigest()
        if not hmac.compare_digest(sign,sign_payload):
            return json.dumps({
                'err':3,
                'msg':'Wrong secret_key'
            })
        # Now we trust the post
        try:
            sub = subprocess.Popen(['git','pull'],cwd = os.path.expanduser(repo.get('path')),stdout = subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = sub.communicate()
            ret = sub.returncode
            if ret == 0:
                return json.dumps({'err':0,'msg':'finished successfully','stdout':out,'stderr':err})
            else:
                return json.dumps({'err':-1,'msg':'intern err','stdout':out,'stderr':err}), 500
        except Exception as e:
            return json.dumps({'err':-2,'msg':'server exception','err':str(e)}), 502
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

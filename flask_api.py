from flask import Flask
from flask import request, Response, make_response
from flask import session, redirect, url_for
import requests
import json
import traceback

app = Flask(__name__)
 
host = '127.0.0.1'
headers = {'PRIVATE-TOKEN': '9fd8K5EbXfiKL2Q78yZf'}

@app.route('/hello',methods=['POST','GET'])
def hello_world():
    return json.dumps('Hello World!')

def create_project_token(project_id):
    rt = {}
    rt['ec'],rt['em'] = (0,'OK')
    create_url = 'http://%s/api/v4/projects/%s/triggers' % (host,project_id)
    description_info = "%s description" % project_id
    description = {"description":description_info}
    create_r = requests.post(create_url,headers=headers,data=description)

    rt['ec'] = create_r.status_code
    if create_r.status_code != 201:
        rt['em'] = 'Err'
        return rt

    rt['em'] = create_r.json()
    return rt

def get_project_token(project_id):
    token_url = "http://%s/api/v4/projects/%s/triggers" % (host,project_id)
    token_r = requests.get(token_url,headers=headers)

    # Failed on API call
    if token_r.status_code != 200:
        return token_r.status_code

    if token_r.text == '[]':
        # Create a new trigger if there is no one
        create_res = create_project_token(project_id)
        # Return if failed on create trigger
        if create_res.get('ec') != 201:
            return create_res
        token = str(create_res['em'].get('token'))
    else:
        # Parse token from response
        token_info = token_r.json()
        token = token_info[0]['token']

    return token
    
    
@app.route('/autorun-ci',methods=['POST','GET'])
def gitlab_webhook():
    try:
        data = request.data
        data_info = json.loads(data)
        project_id = data_info.get('object_attributes').get('source').get('id')
        ref_name = data_info.get('object_attributes').get('source_branch')
        action = data_info.get('object_attributes').get('action')
        state = data_info.get('object_attributes').get('state')
        token = get_project_token(project_id)
        if action == 'update' or action == 'open' or state = 'opened':
            url = 'http://%s/api/v4/projects/%s/trigger/pipeline' % (host,project_id)
            payload = {'token':token,'ref':ref_name}
            r = requests.post(url,data=payload)
            return json.dumps(r.json())
        else:
            return "ignore"
    except Exception:
        return json.dumps(traceback.format_exc())
    
     
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=7777)

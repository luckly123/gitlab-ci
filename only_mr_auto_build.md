# gitlab-ci 只在执行merge request操作自动build
gitlab-ci在触发push和merge request操作时都会自动build，本文将介绍如何在push操作后不触发build，只在merge request操作触发build，提高gitlab-ci的运行效率。
一. 设置webhook

注；本文介绍的webhook是用flask框架作为web server（Flask的用法本文不做详细介绍）

1.flask + uwsgi + nginx

a.nginx配置(本文只介绍gitlab-ci自带的nginx配置)

vim /var/opt/gitlab/nginx/conf/nginx-status.conf 添加如下配置（注:端口、nginx的根目录自定义)

server {

    listen 127.0.0.1:7777;
    location / {

        root /opt/webhook;

        uwsgi_param  QUERY_STRING       $query_string;

        uwsgi_param  REQUEST_METHOD     $request_method;

        uwsgi_param  CONTENT_TYPE       $content_type;

        uwsgi_param  CONTENT_LENGTH     $content_length;




        uwsgi_param  REQUEST_URI        $request_uri;

        uwsgi_param  PATH_INFO          $document_uri;

        uwsgi_param  DOCUMENT_ROOT      $document_root;

        uwsgi_param  SERVER_PROTOCOL    $server_protocol;

        uwsgi_param  REQUEST_SCHEME     $scheme;

        uwsgi_param  HTTPS              $https if_not_empty;




        uwsgi_param  REMOTE_ADDR        $remote_addr;

        uwsgi_param  REMOTE_PORT        $remote_port;

        uwsgi_param  SERVER_PORT        $server_port;

        uwsgi_param  SERVER_NAME        $server_name;

        uwsgi_pass unix:///run/uwsgi/app/autorun-ci/socket;

        

    }

}



b.设置uwsgi

安装ugsgi：pip install uwsgi

注：本文所用的uswgi版本为1.2.3，版本略低，配置与高版本的略有不同，如若是高版本的uwsgi 请参考相关文档

在/etc/uwsgi/apps-available/ 目录下添加autorun-ci.ini，内容如下：

[uwsgi]

#user identifier of uWSGI processes

uid = gitlab-www

#group identifier of uWSGI processes

gid = gitlab-www

plugins = python

module = run:app

master = true

chdir = /opt/webhook

touch-chain-reload = true




c.配置flask

将falsk的脚本放到/opt/webhook(也就是nginx的根目录)

vim run.py

from flask_api import app




if __name__ == '__main__':

    app.run()

通过run.py 能启动flask程序




至此nginx + uwsgi + flask 配置完成




二.启动服务

1.启动uwsgi 

/etc/init.d/uwsgi start

2.启动nginx

gitlab-ctl restart nginx




三.添加Pipline tragger

1.添加tragger

Setting -> CI/CD -> Pipeline triggers -> Add tragger 添加tragger




2.设置tragger

URL: 设置为 http://172.20.21.10:7777/autorun-ci

Tragger:只勾选Merge request events 选项




3.获取共享token，方便在flask程序调用gitlab-ci Api使用

点击右上角头像 -> Setting -> Acess Tokens -> 设置Name -> 勾选 api和sudo 选项 -> 记录下生成的token

注：此token拥有配置多个用户tragger的权限




四.flask api 代码以我们的应用场景为例

a.当merge request的动作为update、open或者state为opened时调用pipline的tragger 自动build

注:pipline tragger的url在添加tragger完成后可以看到

b.通过piplines api获取tragger的详细信息

c.当用户不存在tragger时通过piplines api创建tragger

详见：piplines api (https://docs.gitlab.com/ee/api/pipline_traggers.html)  




五.编辑.gitlab-ci.yml添加 except pushes；例如：

clang-format:

  stage: check

  except:

  -pushes

在git push后不运行build操作














# QUANTAXIS 的后台api

<!-- TOC -->

- [QUANTAXIS 的后台api](#quantaxis-的后台api)
    - [后端的标准和格式规范](#后端的标准和格式规范)
        - [基础标准](#基础标准)
    - [命名格式](#命名格式)
    - [后端的实现方式和注意事项](#后端的实现方式和注意事项)
        - [跨域支持](#跨域支持)
        - [权限](#权限)
    - [必须实现的部分](#必须实现的部分)
        - [用户管理 /user](#用户管理-user)
        - [回测部分 /backtest](#回测部分-backtest)
        - [行情查询部分 /marketdata](#行情查询部分-marketdata)
            - [current](#current)
        - [实时行情推送 /realtime](#实时行情推送-realtime)

<!-- /TOC -->


quantaxis 采用前后端分离的模式开发,所以对于后端而言 是一个可以快速替换/语言随意的部分.只需要按照规则设置好REST的url即可


## 后端的标准和格式规范

### 基础标准

quantaxis的后台可以用 nodejs(express/koa), python(flask/django/tornado), go 等等语言实现

quantaxis的后台部分主要是作为微服务,给前端(web/client/app)等提供标准化的查询/交互接口


## 命名格式

quantaxis的后台命名格式

http://ip:port/功能(backtest/marketdata/user/..)/细分功能(info/query_code/..)

example:

```
http://localhost:3000/backtest/info_cookie?cookie=xxxxx  ==>  按backtest的cookie查询backtest的信息

```

## 后端的实现方式和注意事项


### 跨域支持

因为是前后端分离的模式, 需要对于url采取跨域允许

跨域在python中的实现

#### Flask

```python
@app.route("/status")
def status():
    rst = make_response(jsonify('200'))
    rst.headers['Access-Control-Allow-Origin'] = '*'
    rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent"
    rst.headers['Access-Control-Allow-Headers'] = allow_headers
    return rst

```


#### Tornado

```python
class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        print（"setting headers!!!"）
        self.set_header("Access-Control-Allow-Origin", "*") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def post(self):
        self.write('some post')

    def get(self):
        self.write('some get')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()
```

跨域在nodejs中的实现

#### express

```javascript

router.get('*', function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");
  res.header("Access-Control-Allow-Methods", "PUT,POST,GET,DELETE,OPTIONS");
  res.header("X-Powered-By", ' 3.2.1')
  res.header("Content-Type", "application/json;charset=utf-8");
  next();
});

```

### 权限

后台服务需要保护好隐私不被泄露,避免路径攻击和端口暴露等问题

## 必须实现的部分


### 用户管理 /user

登陆

http://localhost:3000/users/login?name=admin&password=admin

注册

http://[ip]:[port]/users/signup?name=[name]&password=[password]


### 回测部分 /backtest



### 行情查询部分 /marketdata & /data

功能性的API,分别代表着 日线/分钟线/实时(5档)/分笔数据

#### URI总规则
总URI为 http://[ip]:[port]/[market_type]/[frequence]?code=[]&start=[]&end=[]

#### 股票日线

http://[ip]:[port]/marketdata/stock/day?code=[]&start=[]&end=[]

#### 股票分钟线

http://[ip]:[port]/marketdata/stock/min?code=[]&start=[]&end=[]

#### 股票实时上下五档
http://[ip]:[port]/marketdata/stock/realtime?code=[]&start=[]&end=[]

#### 股票分笔数据
http://[ip]:[port]/marketdata/stock/transaction?code=[]&start=[]&end=[]




#### current

http://[ip]:[port]/stock/history/time?code=000001&start=2017-01-01&end=2018-02-02

### 实时行情推送 /realtime


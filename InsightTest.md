# Insight后端基本接口测试记录

**测试工具：POSTMAN**

[TOC]

## 1. 用户管理接口

### 1.1 验证码接口

1. **测试用例1**

```json
按照接口规定参数传入测试(注册时验证码)
[GET]
{
    "flag": "register",
    "email": "*********@qq.com"
}
```

**测试成功，对应邮箱接收到注册验证码**

<img src="img/img1.png" alt="注册验证码接收成功" style="margin: 0 auto">

2. **测试用例2**

```json
按照接口规定参数传入测试(修改密码时验证码)
[GET]
{
    "flag": "update",
    "email": "*********@qq.com"
}
```

**测试成功，对应邮箱接收到修改密码时验证码**

<img src="img/img2.png" alt="修改密码验证码接收成功" style="margin: 0 auto">

3. **测试用例3**

```json
按照接口规定参数传入测试(忘记密码时验证码)
[GET]
{
    "flag": "forget",
    "email": "*********@qq.com"
}
```

**测试成功，对应邮箱接收到忘记密码时验证码**

<img src="img/img3.png" alt="修改密码验证码接收成功" style="margin: 0 auto">

4. **测试用例4**

```json
一个小时内连续请求发送验证码接口20次，验证频率限制是否生效
```

**测试成功，得到以下结果**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "请求过于频繁, 请于1228秒后重试"
}
```

5. **测试用例5**

```json
传入不存在的参数，测试接口是否能够正确处理异常
[GET]
{
    "ttt": "fdf",
    "ff": "fdfd",
    "fdfdf": "fdfd"
}
```

**测试成功，得到以下结果**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱是必传的"
}
```

6. **测试用例6**

```json
不传入任何参数，测试接口是否能够正常处理异常
```

**测试成功，得到以下结果**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱是必传的"
}
```

7. **测试用例7**

```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```



### 1.2 注册接口

1. **测试用例1**

```json
按照接口规定参数传入
[POST]
{
	"username": "coderchen01",
    "email": "*********@qq.com",
    "captcha": "54013",  # 验证码接口测试中得到的验证码
    "password": "********",
    "nickname": "coder"
}
```

**测试成功，得到结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "用户创建成功"
}
```

2. **测试用例2**

```json
传入已存在邮箱或者用户名，测试接口是否能够正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名或邮箱已存在"
}
```

3. **测试用例3**

```json
传入未知的参数，测试接口是否能够正确处理异常
[POST]
{
    "fdfd": "fdfdfd",
    "gggg": "fdfdfd",
    "fdff": "fdfdfd"
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "注册内容不合法"
}
```

4. **测试用例4**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[POST]
{
    "username": "coderzhen01",
    "email": "*******@qq.com",
    "nickname": "******",
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

5. **测试用例5**

```json
传入错误格式验证码，测试接口是否能够正常处理异常
[POST]
{
    "username": "coderchen01",
    "email": "*********@qq.com",
    "captcha": "fgft45",  # 正确格式为五位数字
    "password": "********",
    "nickname": "coder"
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "验证码格式错误，为5位数字"
}
```

6. **测试用例6**

```json
传入错误验证码，测试接口是否能够处理异常
[POST]
{
    "username": "coderchen01",
    "email": "*********@qq.com",
    "captcha": "12345",
    "password": "********",
    "nickname": "coder"
}
```

**测试失败！！！错误结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "验证码过期"
}
```

**错误原因：**

验证码与邮箱的映射储存在redis中，使用时间戳差值来实现验证码过期。在处理验证验证码是否正确的逻辑时，通过邮箱来查询与其对应的验证码。如果没有获取到则说明验证码错误，获取到了则对比时间戳。**此处错在不能够通过没有获取到验证码来断定验证码错误，获取到了验证码也应该近一步验证，否则如果用户不是第一次接收验证码，那么在验证时，是一定能够获取到验证码的**

**错误源码：**

```python
   def validate(self, key_name):
        raw_value = self.client.hget(key_name, self.email)

        if raw_value is not None:
            value = json.loads(raw_value)
            current_timestamp = int(time.time())
            difference_timestamp = current_timestamp - value['add_timestamp']

            if difference_timestamp > 5 * 60:
                return {
                    'result': '验证码过期',
                    'flag': False
                }

            if self.captcha == value['captcha']:
                return {
                    'result': '验证成功',
                    'flag': True
                }
            
        return {
            'result': '验证码错误',
            'flag': False
        }
```

**修改后:**

```python
    def validate(self, key_name):
        raw_value = self.client.hget(key_name, self.email)
        
        if raw_value is not None:
            value = json.loads(raw_value)
            current_timestamp = int(time.time())
            difference_timestamp = current_timestamp - value['add_timestamp']
            
            if self.captcha == value['captcha']:
                result = {
                    'result': '验证成功',
                    'flag': True
                }
                
                if difference_timestamp > 5 * 60:
                    result = {
                        'result': '验证码过期',
                        'flag': False
                    }
                    
                return result
            
        return {
            'result': '验证码错误',
            'flag': False
        }
```

**修改后，再次测试**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "验证码错误"
}
```

7. **测试用例7**

```json
传入过期验证码，测试接口是否能够正常处理异常
[POST]
{
	"username": "coderchen01",
    "email": "*********@qq.com",
    "captcha": "54013",
    "password": "********",
    "nickname": "coder"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "验证码过期"
}
```

8. **测试用例8**

```json
传入残缺的参数，测试接口是否能够正确处理异常
[POST]
{
	"username": "coderchen01",
    "email": "*********@qq.com",
    "captcha": "54013",
    "password": "********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "昵称是必传的"
}
```

9. **测试用例9**

```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

10. **测试用例10**

```json
用户名，密码，昵称等传入超长字符串，测试接口是否能够正常处理
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名不合法，为6到16位字母、数字和合法符号"
}
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "密码不合法，为6到16位字母、数字和合法符号"
}
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "昵称不合法, 不得超过20个字符"
}
```

**检测用户是否存在请求**

1. **测试用例1**

```json
按照规定参数传入接口，测试接口是否正常处理
[GET]
检测用户名是否存在
{
    "username": "fdfdf"
}
检测邮箱是否存在
{
    "email": "19343443@qq.com"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "用户名不存在，可创建"
}
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "该邮箱未绑定其他用户，可绑定新用户"
}
```

2. **测试用例2**

```json
同时传入用户名和邮箱，测试接口是否正常处理异常
[GET]
{
    "username": "fdfdfe5",
    "email": "14535345@qq.com"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名和邮箱不能同时传入或请求参数不合法"
}
```

3. **测试用例3**

```json
不传入任何参数，测试接口是否正常处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "传入参数不能为空"
}
```

4. **测试用例4**

```json
传入错误格式邮箱，检测接口是否能够正确处理异常
[GET]
{
    "email": "fd453434@qqcom"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名和邮箱不能同时传入或请求参数不合法"
}
```

5. **测试用例5**

```json
传入不必要参数，测试接口是否能够正确处理异常
[GET]
{
	"fdf": "fdfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名和邮箱不能同时传入或请求参数不合法"
}
```



### 1.3 登录接口

1. **测试用例1**

```json
按照规定参数形式传入，测试接口是否是否正常处理
[POST]
(用户名登录)
{
    "username": "coderzhen01",
    "password": "**********"
}
(邮箱登录)
{
    "email": "********@qq.com",
    "password": "*********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": {
        "username": "coderzhen01",
        "email": "********@qq.com",
        "nickname": "******",
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTk0ODkyNDEzLCJqdGkiOiIyMDRkNWFiMDJmMzc0MGQwOTJhM2M2YWNmMzI4OWJiNyIsInVzZXJfaWQiOjd9.YaIg5cctxrPT6E4A_XaI_kvdeRGJnvt-olob91Qs70M"
    },
    "success_msg": "登录成功"
}
```

2. **测试用例2**

```json
同时传入用户名和邮箱，测试接口是否正常处理异常
[POST]
{
    "username": "coderzhen01",
    "email": "********@qq.com",
    "password": "**********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱或用户名不能同时传入"
}
```

3. **测试用例3**

```json
传入错误的密码，测试接口是否正常处理异常
[POST]
{
    "username": "coderzhen01",
    "password": "412245646"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "账号或密码错误"
}
```

4. **测试用例4**

```json
传入其他不必要参数，测试接口是否能够正常处理异常
[POST]
{
	"fdfd": "fdfd",
    "dfd": "fdfdf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "账号或密码是必传的"
}
```

5. **测试用例5**

```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[POST]
{
    "username": "coderchen01",
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



### 1.4 找回密码接口

1. **测试用例1**

```json
按照规范参数传入数据，测试接口是否能够正常处理
[PATCH]
{
    "email": "**********@qq.com",
    "captcha": "98486",
    "new_password": "********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "找回密码成功"
}
```

2. **测试用例2**

```json
传入错误验证码，测试接口是否能够正常处理异常
[PATCH]
{
    "email": "**********@qq.com",
    "captcha": "98586",
    "new_password": "********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "验证码错误"
}
```

3. **测试用例3**

```json
传入过期验证码，测试接口是否能够正常处理异常
[PATCH]
{
    "email": "**********@qq.com",
    "captcha": "98486",
    "new_password": "********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "验证码过期"
}
```

4. **测试用例4**

```json
传入不必要参数，测试接口是否能够正常处理异常
[PATCH]
{
	"fdf": "fdfdf",
    "fdfs": "dfsere"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱是必传的"
}
```

5. **测试用例5**

```json
传入错误的邮箱格式，测试接口是否能够正常处理异常
[PATCH]
{
    "email": "23434343qq.com",
    "captcha": "34356",
    "new_password": "**********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱格式不合法或不支持的邮箱"
}
```

6. **测试用例6**

```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

7. **测试用例7**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[PATCH]
{
    "email": "fdfdfdf@qq.com",
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



### 1.5 修改密码接口

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[PATCH]
用户名验证
{
	"username": "coderf",
    "password": "***********",
    "new_password": "********"
}
邮箱验证
{
    "email": "***@qq.com",
    "password": "*******",
    "new_password": "*******"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "账号或密码修改成功"
}
```

2. **测试用例2**

```json
同时传入用户名和邮箱，检测接口是否能够正确处理异常
[PATCH]
{
    "username": "coderf",
    "email": "********@qq.com",
    "password": "********",
    "new_password": "**********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱和用户名不能同时传入"
}
```

3. **测试用例3**

```json
传入不必要的参数，测试接口是否能够正常处理异常
[PATCH]
{
    "fdfd": "fdfdf",
    "fdghg": "fedgrt",
    "fdfdfdf": "fdfdf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "密码是必须的"
}
```

4. **测试用例4**

```json
传入错误邮箱格式，测试接口是否能够正确处理异常
[PATCH]
{
    "email": "fd34*qq.com",
    "password": "fdfdfd",
    "new_password": "Fdfdf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱格式错误或不支持的邮箱"
}
```

5. **测试用例5**

```json
传入错误密码格式，测试接口是否能够正常处理
[PATCH]
{
    "username": "fdfd",
    "password": "fdfddddddgjdkgjsdklgjsdlkgjklg",
    "new_password": "fdfdfdfdf8887…………（I(*"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "密码不合法，为6到16位字母、数字和合法符号"
}
```

6. **测试用例6**

```json
输入错误格式用户名，测试接口是否能够正常处理
[PATCH]
{
    "username": "ererteiuf90suf0ugj(*)*(*(*&*()*(U)))",
    "password": "fdfdfdf",
    "new_password": "fdfdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名不合法，为6到16位字母、数字和合法符号"
}
```

7. **测试用例7**

```json
输入错误密码，测试接口是否正确处理异常
[PATCH]
{
    "username": "coderf",
    "password": "fdgghdhg",
    "new_password": "*********"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "原密码错误"
}
```

8. **测试用例8**

```json
尝试给未注册的用户修改密码，测试接口是否能够正常处理
[PATCH]
{
	"username": "coderjfdf",
    "password": "dfggdgdfg",
    "new_password": "gdgdfgfdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户不存在"
}
```

9. **测试用例9**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

10. **测试用例10**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[PATCH]
{
    "email": "fdfdfdf@qq.com",
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



### 1.6 修改邮箱接口

1. **测试用例1**

```json
按照规范参数传入，测试接口是否能够正常处理
[PATCH]
用户名验证
{
	"username": "coderf",
    "password": "********",
    "new_email": "*********@qq.com",
    "captcha": "87951"
}
邮箱验证
{
    "email": "**********@qq.com",
    "password": "**********",
    "new_email": "*****@qq.com",
    "captcha": "87951"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "修改邮件成功"
}
```

2. **测试用例2**

```json
同时传入用户名和邮箱，测试接口是否能够正常处理异常
[PATCH]
{
    "username": "coderf",
    "password": "********",
    "email": "**********@qq.com",
    "new_email": "***@qq.com",
    "captcha": "87951"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名与邮箱不能同时传入"
}
```

3. **测试用例3**

```json
传入错误格式得登录邮箱，测试接口是否能够正常处理异常
[PATCH]
{
    "email": "343434@qcom",
    "password": "f********",
    "new_email": "**@qq.com",
    "cpatcha": "88888"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱格式错误或不支持的邮箱"
}
```

4. **测试用例4**

```json
传入错误格式的新邮箱，测试接口是否能够正确处理异常
[PATCH]
{
    "username": "coderf",
    "password": "********",
    "new_email": "fdfdfdqq.com",
    "captcha": "88900"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "新邮箱格式错误或不支持的邮箱"
}
```

5. **测试用例5**

```json
传入错误格式得密码，测试接口是否能够正常处理异常
[PATCH]
{
    "username": "dfdfii",
    "password": "dfdffdfdgdgdgdfgdgsdfgsdfgsdfgsdf",
    "new_email": "3434356345@qq.com",
    "captcha": "43434"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "密码不合法，为6到16位字母、数字和合法符号"
}
```

6. **测试用例6**

```json
传入错误格式得用户名，测试接口是否正常处理异常
[PATCH]
{
    "username": "fdfdfdfdfdfdfd())(fdfdfd",
    "password": "ffdfdfddfd",
    "captcha": "89090",
    "new_email": "fdfdfdf@qq.com"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名不合法，为6到16位字母、数字和合法符号"
}
```

7. **测试用例7**

```json
传入错误格式验证码，测试接口是否能够正常处理异常
[PATCH]
{
    "username": "coderf",
    "password": "********",
    "new_email": "**********@qq.com",
    "captcha": "89f990"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "验证码格式错误，为5位数字"
}
```

8. **测试用例8**

```json
传入错误的密码，测试接口是否能够正确处理
[PATCH]
{
    "username": "coderf",
    "password": "******",
    "new_email": "******@qq.com",
    "captcha": "99090"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户验证失败，密码错误"
}
```

9. **测试用例9**

```json
使用已注册的邮箱作为新邮箱，测试接口是否能够正确处理
[PATCH]
{
    "username": "coderf",
    "password": "**********",
    "new_email": "*********@qq.com",
    "captcha": "98809"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "新邮件已绑定到其他用户"
}
```

10. **测试用例10**

```json
为不存在的用户修改邮箱，测试接口是否能够正确处理
[PATCH]
{
    "username": "fdffdf",
    "password": "dffdsfd",
    "email": "******@qq.com",
    "captcha": "90909"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "账户不存在"
}
```

11. **测试用例11**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

12. **测试用例12**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[PATCH]
{
    "email": "fdfdfdf@qq.com",
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



### 1.7 注销用户

1. **测试用例1**

```json
按规定参数传入，测试接口是否能够正常处理
[DELETE]
用户名验证
{
    "username": "coderf",
    "password": "********"
}
邮箱验证
{
	"email": "******@qq.com",
    "password": "*******"
}

强制删除需加入force字段，此测试在后续人脸库，AI技能接口库，任务接口测试后进行。
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "用户注销成功"
}
```

2. **测试用例2**

```json
同时传入邮箱和用户名，测试接口是否能够正确处理异常
[DELTE]
{
    "username": "cdoefdfd",
    "email": "*******@qq.com",
    "password": "fdfdfdfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名和邮箱不能同时传入"
}
```

3. **测试用例3**

```json
传入错误格式邮箱，测试接口是否正确处理异常
[DELETE]
{
    "email": "fdfdf@qqomc",
    "password": "fdfdfdfdf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "邮箱格式错误或不支持的邮箱"
}
```

4. **测试用例4**

```json
传入错误格式用户名，测试接口是否正确处理异常
[DELETE]
{
    "username": "fdfddddddddddddddddddd",
    "password": "fdfdfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "用户名不合法，为6到16位字母、数字和合法符号"
}
```

5. **测试用例5**

```json
传入不必要参数，测试接口是否正确处理异常
[DELETE]
{
    "fdfd": "Fdfgdgd",
    "fdfdg": "fgdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "账号或密码是必须的"
}
```

6. **测试用例6**

```json
传入未注册的用户，测试接口是否正确处理异常
{
    "username": "fdggghdd",
    "password": "gdghh"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "该用户未注册"
}
```

7. **测试用例7**

```json
传入错误格式密码，测试接口是否正确处理异常
[DELETE]
{
    "username": "fdgfdgdg",
    "password": "dgd鼓捣鼓捣"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "密码不合法，为6到16位字母、数字和合法符号"
}
```

8. **测试用例8**

```json
传入错误密码，测试接口是否正常处理异常
[DELETE]
{
    "username": "coderchen01",
    "password": "fdghhghd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "密码错误"
}
```

9. **测试用例9**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

10. **测试用例10**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "email": "fdfdfdf@qq.com",
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```




## 2. 人脸管理接口

### 2.1人脸库接口

#### 2.1.1 创建

1. **测试用例1**

```json
按照规定参数传入，测试接口是否能够正常处理
[POST]
{
    "face_group_id": "face_group_test",
    "name": "test_group",
    "description": "测试接口"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "创建人脸库成功"
}
```

2. **测试用例2**

```json
传入错误参数，测试接口是否能够正常处理
[POST]
{
    "fdggd": "gdgedterte",
    "dgdgd": "gdere"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID是必须的"
}
```

3. **测试用例3**

```json
传入错误格式ID，测试接口是否能够正常处理
[POST]
{
    "face_group_id": "*)(*))",
    "name": "fdgdgdf",
    "description": "gdgdgf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID不合法，为6-20位字母、数字或下划线"
}
```

4. **测试用例4**

```json
传入缺少参数的数据，测试接口是否正常处理
[POST]
{
    "face_group_id": "test_te"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库名称是必须的"
}
```

5. **测试用例5**

```json
传入错误格式名称，测试接口是否正常处理异常
[POST]
{
    "face_group_id": "fdfdfddf",
    "name": "fdfjgklgjdkljgdkljgljdfffffffffffffffffffffffffllgj"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库名称不得超过30个字符"
}
```
6. **测试用例6**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

7. **测试用例7**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "face_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

**查询人脸库是否存在接口**

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[GET]
{
    "face_group_id": "fedgdgdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "人脸库不存在，可创建"
}
```

2. **测试用例2**

```json
不传入参数，测试接口是否正确处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID是必须的"
}
```

3. **测试用例3**

```json
传入多于数据，测试接口是否正确处理
[GET]
{
    "face_group_id": "fedgdgdgd",
    "ffdgfdg": "fgdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "人脸库不存在，可创建"
}
接口忽略了，多于的参数
```

#### 2.1.2 查询


1. **测试用例1**

```json
无需传入参数，测试接口是否正常
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "face_group_id": "face_group_test",
            "name": "test_group",
            "description": "测试接口",
            "add_time": "2020-07-10 23:26:30"
        },
        {
            "face_group_id": "test_te",
            "name": "fdfce",
            "description": "",
            "add_time": "2020-07-10 23:51:57"
        }
    ],
    "success_msg": "人脸库数据请求成功"
}
```

2. **测试用例2**

```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

#### 2.1.3 修改

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[PATCH]
{
    "face_group_id": "test_te",
    "name": "fdfd",
    "description": "fdgdgdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "人脸库信息修改成功"
}
```

2. **测试用例2**

```json
只修改一个字段测试
[PATCH]
{
    "face_group_id": "test_te",
    "name": "fdfdfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "人脸库信息修改成功"
}
```

3. **测试用例3**

```json
只传入人脸库ID，测试接口是否能够正确处理异常
[PATCH]
{
    "face_group_id": "test_te"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "请传入须修改数据"
}
```

4. **测试用例4**

```json
传入不存在的人脸库ID，测试接口是否正确处理异常
[PATCH]
{
    "face_group_id": "fdfgdfdf",
    "name": "Gdgdgh"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "无指定人脸库"
}
```

5. **测试用例5**

```json
传入错误格式得人脸库ID，测试接口是否能够处理异常
[PATCH]
{
    "face_group_id": "*(()*()Fd)",
    "name": "fdgdgdfg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID不合法，为6-20位字母、数字或下划线"
}
```

6. **测试用例6**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

7. **测试用例7**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "face_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

#### 2.1.4 删除

1. **测试用例1**

```json
按规定参数传入，测试接口是否正常
[DELETE]
{
    "face_group_id": "test_te"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "删除人脸库成功"
}
```

1. **测试用例1**

```json
传入不正确参数，测试接口是否正确处理异常
[DELETE]
{
    "tetsty": "test_te"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID是必须的"
}
```

2. **测试用例2**

```json
传入错误格式人脸库ID，测试接口是否正确处理异常
[DELETE]
{
    "face_group_id": "fdfgdfdf*)()"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID不合法，为6-20位字母、数字或下划线"
}
```

3. **测试用例3**

```json
传入不存在的人脸库ID，测试接口是否正确处理异常
[DELETE]
{
    "face_group_id": "dfgdghdghd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "不存在该人脸库"
}
```

4. **测试用例4**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

5. **测试用例5**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "face_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



### 2.2 人脸接口

#### 2.2.1 创建

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[POST]
{
	"face_id": "face_test",
    "face_group_id": "face_group_test",
    "name": "***",
    "face_image": "BASE64"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "人脸添加成功"
}
```
2. **测试用例2**

```json
传入已存在的人脸ID，测试接口是否正确处理异常
[POST]
{
	"face_id": "face_test",
    "face_group_id": "face_group_test",
    "name": "***",
    "face_image": "BASE64"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸已存在"
}
```
3. **测试用例3**

```json
传入错误格式的人脸ID，测试接口是否正确处理异常
[POST]
{
    "face_id": "fisdo*()()",
    "face_group_id": "face_group_test",
    "name": "***",
    "face_image": "BASE64"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸ID不合法，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**

```json
传入错误格式人脸库ID，测试接口是否正确处理异常
[POST]
{
    "face_id": "fisd56",
    "face_group_id": "))group_test",
    "name": "***",
    "face_image": "BASE64"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID不合法，为6-20位字母、数字或下划线"
}
```
5. **测试用例5**

```json
传入不存在的人脸库ID，测试接口是否正确处理异常
[POST]
{
    "face_id": "fisd56",
    "face_group_id": "group_test",
    "name": "***",
    "face_image": "BASE64"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库不存在，无法绑定人脸"
}
```
6. **测试用例6**

```json
传入缺失参数，测试接口是否正常处理异常
[POST]
{
	"face_id": "9809fd",
    "face_group_id": "gdghdghd",
    "name": "gdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸图片base64编码是必须的"
}
```
7. **测试用例7**

```json
传入不必要参数，测试接口是否正常处理异常
[POST]
{
	"fdgfdg": "gdghdfg",
    "gdgh": "gdghe"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸ID是必须的"
}
```
8. **测试用例8**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

9. **测试用例9**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[PATCH]
{
    "face_id": "fdfdfdfcom",
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

**检测人脸ID是否存在接口**

1. **测试用例1**

```json
传入规定参数，测试接口是否正常
[GET]
{
    "face_id": "fdfdfd
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "successs",
    "data": 0,
    "success_msg": "人脸不存在，可创建"
}
```
2. **测试用例2**

```json
不传入参数，测试接口是否正确处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸ID是必须的"
}
```
3. **测试用例3**

```json
传入错误格式ID，测试接口是否正常处理异常
[GET]
{
    "face_id": "()(f0edfg)"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸ID不合法，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```



#### 2.2.2 查询

1. **测试用例1**

```json
按照规定参数传入，测试接口是否成功
[GET]
{
    "face_group_id": "face_group_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "face_id": "face_test",
            "name": "***",
            "face_image": "BASE64",
            "add_time": "2020-07-11 11:12:47"
        },
		{
            "face_id": "face_tst",
            "name": "***",
            "face_image": "图片受损，请删除后重新创建",
            "add_time": "2020-07-11 11:12:47"
        }
    ],
    "success_msg": "数据请求成功"
}
```
2. **测试用例2**

```json
不传入参数，测试接口是否正确处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID是必须的"
}
```
3. **测试用例3**

```json
传入错误参数，测试接口是否正确处理异常
[GET]
{
    "fdfgdg": "gdghdf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID是必须的"
}
```
4. **测试用例4**

```json
传入错误格式人脸库ID，测试接口是否正常处理
[GET]
{
    "face_group_id": "dgd)_()_"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID不合法，为6-20位字母、数字或下划线"
}
```

5. **测试用例5**

```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```



#### 2.2.3 修改

1. **测试用例1**

```json
按照规定参数，测试接口是否正常
[PATCH]
{
    "face_id": "face_tst",
    "name": "***",
    "face_image": "BASE64"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "人脸信息更改成功"
}
```
2. **测试用例2**

```json
传入额外参数，测试接口是否正确处理
[PATCH]
{
    "face_id": "face_tst",
    "name": "***",
    "face_image": "BASE64",
    "fdgd": "fdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "人脸信息更改成功"
}
接口忽略多于参数
```

3. **测试用例3**

```json
传入错误格式人脸ID，测试接口是否正确处理
[PATCH]
{
    "face_id": "dgdgdg#",
    "name": "CEt
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸库ID，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**

```json
传入不存在的人脸ID，测试接口是否正常处理
[PATCH]
{
    "face_id": "fdfdf",
    "name": "dg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "不存在该人脸"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "face_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



#### 2.2.4 删除

1. **测试用例1**

```json
传入规定参数，测试接口是否正常
[DELETE]
{
    "face_id": "face_tst"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "人脸信息删除成功"
}
```
2. **测试用例2**

```json
传入错误参数，测试接口是否正常
[DELETE]
{
    "fgdgd": "fdgdgfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸ID是必须的"
}
```
3. **测试用例3**

```json
传入错误格式人脸ID，测试接口是否正常处理
[DELETE]
{
    "face_id": "dgdg(**)()"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "人脸ID不合法，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**

```json
传入不存在的人脸ID，测试接口是否正常处理
[DELETE]
{
    "face_id": "dfjdkfgljd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "不存在人脸"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "face_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



## 3. AI技能管理接口

### 3.1 AI技能库

#### 3.1.1 创建

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常处理
[POST]
{
    "ai_skill_group_id": "ai_skill_group_test",
    "name": "螺丝螺母检测",
    "description": "AI技能分组创建测试"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "接口库创建成功"
}
```
2. **测试用例2**

```json
传入错误格式ID，测试接口是否正确处理异常
[POST]
{
	"ai_skill_group_id": "90j)))",
    "name": "test",
    "description": "dgddg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能分组ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
传入未知参数，测试接口是否正常处理
[POST]
{
    "ai_skill_group_id": "dfdf90",
    "dgdg": "gdgdgfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能名称是必须的"
}
```
4. **测试用例4**

```json
传入已经存在的技能接口分组ID，测试接口是否正确处理异常
[POST]
{
	"ai_skill_group_id": "ai_skill_group_test",
    "name": "135",
    "description": "fdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "已存在接口库"
}
```
5. **测试用例5**

```json
传入空的技能分组名称，测试接口是否正常处理异常
[POST]
{
    "ai_skill_group_id": "getfdfdfe",
    "name": "",
    "description": "dgfdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能分组名称不能超过30个字符或为空"
}
```
6. **测试用例6**

```json
不传入技能分组描述
[POST]
{
    "ai_skill_group_id": "fd9f0d",
    "name": "fdfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "接口库创建成功"
}
```
7. **测试用例7**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

8. **测试用例8**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "face_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

**检测技能接口分组ID是否存在接口**

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[GET]
{
    "ai_skill_group_id": "fedgdgdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "技能接口分组不存在，可创建"
}
```

2. **测试用例2**

```json
不传入参数，测试接口是否正确处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口分组ID是必须的"
}
```

3. **测试用例3**

```json
传入多于数据，测试接口是否正确处理
[GET]
{
    "ai_skill_group_id": "fedgdgdgd",
    "ffdgfdg": "fgdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "技能接口分组不存在，可创建"
}
接口忽略了，多于的参数
```



#### 3.1.2 查询

1. **测试用例1**

```json
无需传入参数
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "ai_skill_group_id": "ai_skill_group_test",
            "name": "螺丝螺母检测",
            "description": "AI技能分组创建测试",
            "add_time": "2020-07-12 11:07:29"
        },
        {
            "ai_skill_group_id": "fd9f0d",
            "name": "fdfd",
            "description": "",
            "add_time": "2020-07-12 11:16:36"
        }
    ],
    "success_msg": "接口库数据请求成功"
}
```
2. **测试用例2**

```json
传入多于参数，测试接口是否正常处理
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "ai_skill_group_id": "ai_skill_group_test",
            "name": "螺丝螺母检测",
            "description": "AI技能分组创建测试",
            "add_time": "2020-07-12 11:07:29"
        },
        {
            "ai_skill_group_id": "fd9f0d",
            "name": "fdfd",
            "description": "",
            "add_time": "2020-07-12 11:16:36"
        }
    ],
    "success_msg": "接口库数据请求成功"
}
忽略多于参数
```
3. **测试用例3**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```



#### 3.1.3 修改

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常处理
[PATCH]
{
    "ai_skill_group_id": "fd9f0d",
    "name": "update"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "接口库信息更改成功"
}
```
2. **测试用例2**

```json
传入空的接口分组名称，测试接口是否正确处理异常
[PATCH]
{
    "ai_skill_group_id": "fd9f0d",
    "name": ""
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能分组名称不能超过30个字符或为空"
}
```
3. **测试用例3**

```json
传入未知参数，测试接口是否正常处理
[PATCH]
{
    "ai_skill_group_id": "fdgdgd",
    "fdfd": "dgdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "请传入须修改的参数"
}
```
4. **测试用例4**

```json
传入错误格式ID，测试接口是否正确处理异常
[PATCH]
{
    "ai_skill_group_id": "()*)P*)",
    "name": "fdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "接口分组ID不合法，为6-20位字母、数字或下划线"
}
```
5. **测试用例5**

```json
不传入必要参数，测试接口是否正确处理异常
[PATCH]
{
    "ffdfdfdf": "fdfdfdfg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "接口库ID是必须的"
}
```
6. **测试用例6**

```json
传入不存在的ID，测试接口是否正确处理异常
[PATCH]
{
    "ai_skill_group_id": "fd0f9d0fd9",
    "name": "dfgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "接口库不存在"
}
```
7. **测试用例7**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

8. **测试用例8**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "ai_skill_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

#### 3.1.4 删除

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[DELETE]
{
    "ai_skill_group_id": "fd9f0d"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "接口库删除成功"
}
```
2. **测试用例2**

```json
不传入参数，测试接口是否正常处理
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能分组ID是必须的"
}
```
3. **测试用例3**

```json
传入错误格式ID，测试接口是否正常处理
[PATCH]
{
	"ai_skill_group_id": "9090909)))"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能分组ID不合法，为6-20位字母、数字或下划线"
}
```

4. **测试用例4**

```json
传入不存在的ID，测试接口是否正确处理异常
[PATCH]
{
    "ai_skill_group_id": "fdfdf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "不存在的接口库"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "ai_skill_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```



### 3.2 技能接口

#### 3.2.1 创建

1. **测试用例1**

```json
按照规定参数，测试接口是否正常
[POST]
{
    "ai_skill_id": "ai_skill_test",
    "ai_skill_group_id": "ai_skill_group_test",
    "name": "螺丝螺母检测接口",
    "description": "技能测试",
    "ai_skill_url": "*****"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "AI技能接口创建完成"
}
```
2. **测试用例2**

```json
传入错误格式的技能ID，测试接口是否正确处理异常
[POST]
{
    "ai_skill_id": "fdd9090)()",
    "ai_skill_group_id": "ai_skill_group_test",
    "name": "螺丝螺母检测接口",
    "description": "技能测试",
    "ai_skill_url": "*****"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
传入缺失参数的数据，测试接口是否正常处理
[POST]
{
    "ai_skill_group_id": "ai_skill_group_test",
    "name": "螺丝螺母检测接口",
    "description": "技能测试",
    "ai_skill_url": "*****"
}
{
    "ai_skill_id": "fdd9090",
    "name": "螺丝螺母检测接口",
    "description": "技能测试",
    "ai_skill_url": "*****"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口ID是必须的"
}

```
4. **测试用例4**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能分组接口ID是必须的"
}
```

**测试成功，所得结果如下**

```json
传入已存在的技能接口ID，测试接口是否正常处理
[POST]

```
5. **测试用例5**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "AI技能接口已存在"
}
```

**测试成功，所得结果如下**

```json
{
    "ai_skill_id": "ai_skill_test",
    "ai_skill_group_id": "ai_skill_group_test",
    "name": "螺丝螺母检测接口",
    "description": "技能测试",
    "ai_skill_url": "*****"
}
```
6. **测试用例6*

```json
传入不存在的技能接口分组ID，测试接口是否正确处理异常
[POST]
{
    "ai_skill_id": "ai_skill_test",
    "ai_skill_group_id": "ai_skill_group_tet",
    "name": "螺丝螺母检测接口",
    "description": "技能测试",
    "ai_skill_url": "*****"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "不存在的技能接口库，无法绑定技能接口"
}
```
7. **测试用例7**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

8. **测试用例8**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "ai_skill_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

**检测技能接口ID是否存在接口**

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[GET]
{
    "ai_skill_id": "fedgdgdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "技能接口不存在，可创建"
}
```

2. **测试用例2**

```json
不传入参数，测试接口是否正确处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口ID是必须的"
}
```

3. **测试用例3**

```json
传入多于数据，测试接口是否正确处理
[GET]
{
    "ai_skill_id": "fedgdgdgd",
    "ffdgfdg": "fgdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "技能接口不存在，可创建"
}
接口忽略了，多于的参数
```

#### 3.2.2 查询

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常处理
[GET]
{
    "ai_skill_group_id": "ai_skill_group_id"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "ai_skill_id": "ai_skill_test",
            "name": "螺丝螺母检测接口",
            "description": "技能测试",
            "ai_skill_url": "**",
            "state": "接口正常",
            "add_time": "2020-07-12 14-44-38"
        }
    ],
    "success_msg": "AI技能接口请求成功"
}
```
2. **测试用例2**

```json
不传入参数，测试接口是否正常处理
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口分组是必须的"
}
```
3. **测试用例3**

```json
传入错误参数，测试接口是否正常处理
[GET]
{
    "dffd": "Fdgdg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口分组是必须的"
}
```
4. **测试用例4**

```json
传入多于参数，测试接口是否正确处理异常
[GET]
{
    "ai_skill_group_id": "ai_skill_group_test",
    "fdgdg": "gdgdgdgf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "ai_skill_id": "ai_skill_test",
            "name": "螺丝螺母检测接口",
            "description": "技能测试",
            "ai_skill_url": "**",
            "state": "接口正常",
            "add_time": "2020-07-12 14-44-38"
        }
    ],
    "success_msg": "AI技能接口请求成功"
}
忽略多于参数
```
5. **测试用例5**

```json
传入错误格式ID
[GET]
{
    "ai_skill_group_id": "fdf))"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口分组ID不合法，为6-20位字母、数字或下划线"
}
```
6. **测试用例6**

```json
传入不存在的ID
[GET]
{
    "ai_skill_group_id": "Fdgdgdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "不存在的接口库"
}
```
7. **测试用例7**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

#### 3.2.3 更新

1. **测试用例1**

```json
根据规定参数传入，测试接口是否正确处理
[PATCH]
{
    "ai_skill_id": "ai_skill_test",
    "name": "螺丝螺母"
}
{
    "ai_skill_id": "ai_skill_test",
    "description": "修改测试"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "AI技能接口信息更新成功"
}
```
2. **测试用例2**

```json
只传入ID
[PATCH]
{
    "ai_skill_id": "ai_skill_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "请传入须修改的数据"
}
```
3. **测试用例3**

```json
传入错误技能接口地址，测试接口是否正确处理异常
[PATCH]
{
    "ai_skill_id": "ai_skill_test",
    "ai_skill_url": "http:/;fjdkf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口地址格式错误"
}
```
4. **测试用例4**

```json
不传入参数，测试接口是否正确处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "AI技能接口ID是必须的"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "ai_skill_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

#### 3.2.4 删除

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[DELETE]
{
    "ai_skill_id": "ai_skill_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "AI技能接口删除成功"
}
```
2. **测试用例2**

```json
不传入参数测试
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口ID是必须的"
}
```
3. **测试用例3**

```json
传入错误格式ID测试
[DELETE]
{
    "ai_skill_id": "fd()())"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "技能接口ID不合法，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**

```json
传入不存在的ID
[DELETE]
{
	"ai_skill_id": "dfdigkjdlgj"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "AI技能接口不存在"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "ai_skill_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

## 4. 摄像头管理接口

### 4.1 摄像头分组

#### 4.1.1 创建

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[POST]
{
    "camera_group_id": "camera_group_test",
    "name": "测试摄像头分组",
    "description": "测试摄像头分组"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "成功创建摄像头分组"
}
```
2. **测试用例2**

```json
传入错误格式的摄像头分组ID，测试接口是否正确处理异常
[POST]
{
    "camera_group_id": "fd9fd09)))",
    "name": "test",
    "description": "test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
传入错误参数，测试接口是否正确处理异常
[POST]
{
    "cfdkl": "dgdgdg",
    "dgdgf": "gd909)()"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID是必须的"
}
```
4. **测试用例4**

```json
传入超出字符限制的参数，测试接口是否正常处理
[POST]
{
    "camera_group_id": "gdgdgdg",
    "name": "fgdkgjldgjlkdfgjkl;djgkl;djgkldfjhgkldhjgkl;jsdkfgjmdsl;gjaksdlghjkaslgjal;skhjgklasdngksdgnjklsdgjkdsjgkldsjgkl;jgkldsjg;asdjgklajgiosujgdsjgkksjglkjagkljekljtweklgjhhodujgodgjsdlkgjsdklgj",
    "description": "fdgdkgjl"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组名称不能超过30个字符或为空"
}
```
5. **测试用例5**

```json
传入已存在分组ID，测试接口是否正确处理
[POST]
{
    "camera_group_id": "camera_group_test",
    "name": "dffgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "分组ID已存在，请重新设置"
}
```
6. **测试用例6**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

7. **测试用例7**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "camera_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

**检测摄像头分组ID是否存在**

1. **测试用例1**

```json
按照规定参数，测试接口是否正确处理异常
[GET]
{
    "camera_group_id": "kdgjflsdjg"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "组ID不存在，可新建"
}
```
2. **测试用例2**

```json
不传入参数，测试接口是否正确处理异常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID是必须的"
}
```
3. **测试用例3**

```json
传入错误格式分组ID，测试接口是否正确处理异常
[GET]
{
    "camera_group_id": "dff90)))"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID不合法，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**

```json
传入错误参数，测试接口是否正确处理异常
[GET]
{
    "dgdgdg": "gdgkdjlgf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID是必须的"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

#### 4.1.2 查询

1. **测试用例1**

```json
无需参数，测试接口是否正常
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "name": "测试摄像头分组",
            "camera_group_id": "camera_group_test",
            "description": "测试摄像头分组",
            "add_time": "2020-07-12 20:46:55"
        }
    ],
    "success_msg": "摄像头组数据请求成功"
}
```
2. **测试用例2**

```json
传入参数，测试接口是否正常
[GET]
{
    "kfdlf": "dklgjdlj"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "name": "测试摄像头分组",
            "camera_group_id": "camera_group_test",
            "description": "测试摄像头分组",
            "add_time": "2020-07-12 20:46:55"
        }
    ],
    "success_msg": "摄像头组数据请求成功"
}
忽略多于参数
```
3. **测试用例3**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

#### 4.1.3 修改

1. **测试用例1**

```json
按照规定参数，测试接口是否正常
[PATCH]
{
    "camera_group_id": "camera_group_test",
    "name": "test",
    "description": "description_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "摄像头组信息修改成功"
}
```
2. **测试用例2**

```json
传入错误格式的摄像头分组ID，测试接口是否正确处理异常
[PATCH]
{
    "camera_group_id": "fkdslgfj)))",
    "name": "jfdkjf",
    "description": "fdkld"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
传入不存在的摄像头分组ID，测试接口是否正确处理异常
[PATCH]
{
    "camera_group_id": "kdfjkkdf",
    "name": "fdkfld"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组不存在"
}
```
4. **测试用例4**

```json
不传入修改参数，测试接口是否正常处理异常
[PATCH]
{
    "camera_group_id": "camera_group_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "请传入须修改参数"
}
```

5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "camera_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

#### 4.1.4 删除

1. **测试用例1**

```json
传入规定参数，测试接口是否正确处理
[DELETE]
{
    "camera_group_id": "camera_group_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "摄像头组删除成功"
}
```
2. **测试用例2**

```json
传入错误格式的摄像头分组ID，测试接口是否正常处理
[DELETE]
{
    "camera_group_id": "jfdkfgj))"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
不传入参数，测试接口是否正常处理
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID是必须的"
}
```
4. **测试用例4**

```json
传入不存在摄像头分组ID，测试接口是否正常处理
[DELETE]
{
    "camera_group_id": "f0d9f0df9KK"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组不存在"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[DELETE]
{
    "camera_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

### 4.2 摄像头接口

#### 4.2.1 创建

1. **测试用例1**

```json
传入规定参数，测试接口是否正常处理
[POST]
{
    "camera_id": "camera_test",
    "camera_group_id": "camera_group_test",
    "name": "测试摄像头",
    "description": "测试摄像头创建",
    "camera_url": "rtsp://admin:insight@666@192.168.31.112//Streaming/Channels/1"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "摄像头创建成功"
}
```
2. **测试用例2**

```json
传入错误格式摄像头ID，测试接口是否正常处理
[POST]
{
    "camera_id": "camera_fd))test",
    "camera_group_id": "camera_group_test",
    "name": "测试摄像头",
    "description": "测试摄像头创建",
    "camera_url": "rtsp://admin:insight@666@192.168.31.112//Streaming/Channels/1"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
不传入摄像头ID，测试接口是否正常处理异常
[POST]
{
    "camera_group_id": "camera_group_test",
    "name": "测试摄像头",
    "description": "测试摄像头创建",
    "camera_url": "rtsp://admin:insight@666@192.168.31.112//Streaming/Channels/1"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID是必须的"
}
```
4. **测试用例4**

```json
传入错误格式的摄像头分组ID，测试接口是否正常
[POST]
{
    "camera_id": "camera_fest",
    "camera_group_id": "camera_group_te)st",
    "name": "测试摄像头",
    "description": "测试摄像头创建",
    "camera_url": "rtsp://admin:insight@666@192.168.31.112//Streaming/Channels/1"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID不合法，为6-20位字母、数字或下划线"
}
```
5. **测试用例5**

```json
不传入摄像头分组ID，测试接口是否正常
[POST]
{
    "camera_id": "camera_fest",
    "name": "测试摄像头",
    "description": "测试摄像头创建",
    "camera_url": "rtsp://admin:insight@666@192.168.31.112//Streaming/Channels/1"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID是必须的"
}
```
6. **测试用例6**

```json
传入已存在的数据，测试接口是否正常
[POST]
{
    "camera_id": "camera_test",
    "camera_group_id": "camera_group_test",
    "name": "测试摄像头",
    "description": "测试摄像头创建",
    "camera_url": "rtsp://admin:insight@666@192.168.31.112//Streaming/Channels/1"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID已存在，请重新设置"
}
```
7. **测试用例7**

```json
传入错误格式的摄像头视频流地址，测试接口是否正常
[POST]
{
    "camera_id": "camera_",
    "camera_group_id": "camera_group_test",
    "name": "测试摄像头",
    "description": "测试摄像头创建",
    "camera_url": "rtsp:admin:insight@666@192.168.31.112//Streaming/Channels/1"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头视频流地址不合法，只支持RTSP或RTMP"
}
```
8. **测试用例8**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

9. **测试用例9**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[POST]
{
    "camera_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

**查询摄像头ID是否存在接口**

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[GET]
{
    "camera_id": "fdkljgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": 0,
    "success_msg": "摄像头ID不存在，可新建"
}
```
2. **测试用例2**

```json
不传入参数测试接口是否正常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID是必须的"
}
```
3. **测试用例3**

```json
传入错误格式ID，测试接口是否正常
[GET]
{
    "camera_id": "fdf)))"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID不合法，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

#### 4.2.2 查询

1. **测试用例1**

```json
按照规定参数，测试接口是否正常
[GET]
{
    "camera_group_id": "camera_group_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": [
        {
            "ai_skill_settings": [],
            "extraction_settings": null,
            "camera_id": "camera_test",
            "name": "测试摄像头",
            "description": "测试摄像头创建",
            "camera_url": "rtsp://admin:insight@666@192.168.31.112//Streaming/Channels/1",
            "state": "连接成功",
            "add_time": "2020-07-12 22:57:31"
        }
    ],
    "success_msg": "数据请求成功"
}
```
2. **测试用例2**

```json
不传入参数，测试接口是否正常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID是必须的"
}
```
3. **测试用例3**

```json
传入错误格式ID，测试接口是否正确
[GET]
{
    "camera_group_id": "fd9f0d))"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头分组ID不合法，为6-20位字母、数字或下划线"
}
```
4. **测试用例4**

```json
传入不存在的摄像头分组，测试接口是否正常
[GET]
{
    "camera_group_id": "fdfdfljdf"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "没有该摄像头分组"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

#### 4.2.3 修改

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[PATCH]
{
    "camera_id": "camera_test",
    "name": "test",
    "description": "tset",
    "camera_url": "****"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "摄像头信息修改成功"
}
```
2. **测试用例2**

```json
传入错误格式的摄像头ID，测试接口是否正常
[PATCH]
{
    "camera_id": "fdkf)))",
    "name": "dtgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
不传入摄像头ID，测试接口是否正常
[PATCH]
{
    "name": "dtgd",
    "description": "fdfdfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID是必须的"
}
```
4. **测试用例4**

```json
不传入修改参数，测试接口是否正常处理
[PATCH]
{
    "camera_id": "camera_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "请传入须修改参数"
}
```
5. **测试用例5**

```json
传入不存在摄像头ID，测试接口是否正常处理
[PATCH]
{
    "camera_id": "fdfidfd",
    "name": "dgdgdgd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "没有该摄像头，请新建"
}
```
6. **测试用例6**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

7. **测试用例7**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[PATCH]
{
    "camera_group_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

#### 4.2.4 删除

1. **测试用例1**

```json
按照规定参数传入，测试接口是否正常
[DELETE]
{
    "camera_id": "camera_test"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 1,
    "msg": "success",
    "data": null,
    "success_msg": "删除摄像头成功"
}
```
2. **测试用例2**

```json
不传入参数，测试接口是否正常
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID不合法，为6-20位字母、数字或下划线"
}
```
3. **测试用例3**

```json
传入不存在的摄像头ID，测试接口是否正常
[DELETE]
{
    "camera_id": "fdfdfdfd"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "没有该摄像头"
}
```
4. **测试用例4**

```json
传入错误格式摄像头ID，测试接口是否正常
[DELETE]
{
    "camera_id": "fdfdfdfd)"
}
```

**测试成功，所得结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "摄像头ID不合法，为6-20位字母、数字或下划线"
}
```
5. **测试用例5**
```json
用其他请求方法访问接口，测试接口是否正常处理
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "当前请求方法不被允许"
}
```

6. **测试用例6**

```json
传入错误JSON格式数据，测试接口是否能够正常处理异常
[PATCH]
{
    "camera_id": fdfdfd,
}
```

**测试成功，得到结果如下**

```json
{
    "code": 0,
    "msg": "error",
    "data": null,
    "error_msg": "JSON数据不合法"
}
```

EMAIL_CAPTCHA_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>insight 邮件</title>
    <style>
        html,
        body {
            margin: 0;
            padding: 0;
        }
        a {
            text-decoration: none;
        }
        body {
            font: 16px/1.5 "Microsoft YaHei", "微软雅黑", Verdana;
        }
        .header {
            background-color: #fff;
            border: 1px solid #E9E9E9;
            border-bottom: 0;
        }
        .main {
            background-color: #fff;
            border: 1px solid #E9E9E9;
            border-top: 0;
        }
        .text-captcha,
        .text-warning {
            display: inline-block;
            width: 100%;
            font-size: 20px;
            text-align: center;
        }

    </style>
</head>
<body>
    <table width="600" border="0" cellpadding="0" cellspacing="0" align="center" class="header">
        <tr>
            <td>
                <table width="100%"  border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td>
                            <h1 align="center"> insight - 验证码 </h1>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <table width="600" border="0"  cellpadding="0" cellspacing="0" align="center" class="main">
        <tr>
            <td>
                <table width="100%" border="0" cellspacing="50" cellpadding="0">
                    <tr>
                        <td>
                            <span class="text-captcha"> 您##text##的验证码是：##captcha## </span>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <span class="text-warning"> 五分钟内有效。 </span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

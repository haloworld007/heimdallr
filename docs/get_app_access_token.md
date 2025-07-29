# 获取应用访问令牌 (App Access Token)

## API 描述

调用此 API 以获取 `app_access_token`。`app_access_token` 用于验证发起 API 请求的应用身份。`app_access_token` 将在 7200 秒（2 小时）后过期。开发者应自行维护缓存机制来存储和刷新 `app_access_token`，以确保 API 请求能够成功发送。

**注意：**
此 API 在同一个 App ID 下的调用频率限制为每小时 600 次。

## 请求方法

`POST`

## 接口地址

`https://openapi.seatalk.io/auth/app_access_token`

## 请求参数

### 请求头

| 参数          | 类型   | 是否必填 | 描述           |
| :------------ | :----- | :------- | :------------- |
| `Content-Type`| string | 是       | 请求头格式 |

### 请求体

| 参数         | 类型   | 是否必填 | 描述           |
| :----------- | :----- | :------- | :------------- |
| `app_id`     | string | 是       | 应用的唯一标识 |
| `app_secret` | string | 是       | 应用的凭证     |

## 请求示例

```json
{
  "app_id": "123",
  "app_secret": "123456"
}
```

## 响应参数

| 参数             | 类型   | 描述                                     |
| :--------------- | :----- | :--------------------------------------- |
| `code`           | int    | 错误码，`0` 表示成功，其他值请参考错误码说明 |
| `app_access_token` | string | 为应用生成的访问令牌                     |
| `expire`         | int    | 生成的令牌过期时的时间戳（秒）           |

## 响应示例

```json
{
  "code": 0,
  "app_access_token": "123456",
  "expire": 1590581487
}
```

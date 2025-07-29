# 事件：收到机器人订阅者的消息

**API 更新**：自 2024 年 11 月 14 日起生效。
**在 SeaTalk 应用中向机器人发送图片、文件和视频的 1-1 聊天**：需要 SeaTalk 应用版本 3.50 或更高版本，该版本将于 2024 年 11 月 28 日发布，以获得完整功能。

## 事件描述
当机器人用户在 1 对 1 聊天中向机器人发送消息时，会触发此事件。

目前，此事件仅支持纯文本、图片、文件和视频类型的消息。不支持合并转发的消息类型。

发送给机器人的图片、文件和视频可以使用以 `https://openapi.seatalk.io/messaging/v2/file/` 开头的 URL 下载。有关更多信息，请参阅此文档。此端点的速率限制为 100 请求/分钟。

## 事件参数

### 请求头

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| `Content-Type` | `string` | 请求头格式 |
| `Signature` | `string` | 用于确保请求由 SeaTalk 发送的签名 |

### 请求体

| 参数 | 类型 | 描述 | 大小/长度限制 |
| --- | --- | --- | --- |
| `event_id` | `string` | 事件的 ID | |
| `event_type` | `string` | 事件的类型。在此情况下为 `message_from_bot_subscriber` | |
| `timestamp` | `uint64` | 此事件发生的时间 | |
| `app_id` | `string` | 接收事件通知的应用 ID | |
| `event` | `object` | 事件特定信息 | |
| ∟`seatalk_id` | `string` | 消息发送者的 SeaTalk ID | |
| ∟`employee_code` | `string` | 用户的员工编号 | |
| ∟`email` | `string` | - 消息发送者的电子邮件<br>- 如果消息发送者与机器人不属于同一组织，则返回空。 | |
| ∟`message` | `object` | 收到的消息 | |
| ∟`message_id` | `string` | 消息的 ID<br><br>**注意**：出于安全原因，单个消息在被不同应用访问时将具有不同的 `message_id`。 | |
| ∟`quoted_message_id` | `string` | 引用的消息 ID（如果消息引用了任何消息）<br><br>**注意**：<br>- 仅支持引用过去 7 天内发送的消息。<br>- 出于安全原因，单个消息在被不同应用访问时将具有不同的 `message_id`。 | |
| ∟`tag` | `string` | 消息类型。<br><br>允许的标签: `"text"`, `"combined_forwarded_chat_history"`, `"image"`, `"file"`, `"video"`<br><br>有关机器人支持的消息类型的更多详细信息，请参阅此文档。 | |
| ∟`text` | `object` | 文本消息对象 | |
| ∟`content` | `string` | 文本消息内容 | |
| ∟`image` | `object` | 图片对象 | |
| ∟`content` | `string` | 图片的 URL。需要有效的 API 令牌才能访问。<br><br>图片消息在 7 天后过期，之后无法使用该 URL 下载。 | 最大: 250 MB |
| ∟`file` | `object` | 文件对象 | |
| ∟`content` | `string` | 文件的 URL。需要有效的 API 令牌才能访问。<br><br>文件消息在 7 天后过期，之后无法使用该 URL 下载。 | 最大: 250 MB |
| ∟`filename` | `string` | 带扩展名的文件名；未指定扩展名的文件将作为未识别文件发送 | 最大: 100 字符 |
| ∟`video` | `object` | 视频对象 | |
| ∟`content` | `string` | 视频的 URL。需要有效的 API 令牌才能访问。<br><br>视频消息在 7 天后过期，之后无法使用该 URL 下载。 | 最大: 250 MB |

## 请求体示例
```json
{
    "event_id":"1234567",
    "event_type":"message_from_bot_subscriber",
    "timestamp":1611220944,
    "app_id":"abcdefghiklmn",
    "event":{
        "seatalk_id":"1239487273",
        "employee_code":"e_12345678",
        "email":"sample@seatalk.biz",
        "message":{
            "message_id": "rSwS8xiQOrLSSuXkvqSTlbF3ALBcU9naXQ0ntcisCEVVkeK1S6C9cfmo",
            "quoted_message_id": "rSwS8xiQOrLSSuXkvqSTlbF4ALBcU9naXQ3-h_79R6Bg91yP_9rUe7G4",
            "tag":"text",
            "text":{
                "content":"How can I request for leave?"
            }
        }
    }
}
```

## 消息对象
这些是消息对象的示例输出。
```json
// 文本
{
    "tag":"text",
    "text":{
        "content":"Hello world!",
    },
    "combined_forwarded_chat_history":null,
    "image":null,
    "video":null,
    "file":null
}

// 图片
{
    "tag":"image",
    "text":null,
    "combined_forwarded_chat_history":null,
    "image":{
        "content":"https://openapi.seatalk.io/messaging/v2/file/asjewnJHe7dfjsWK8LksdmsMN90JjsdwekjU1efwefscvLKJ"
    },
    "video":null,
    "file":null
}

// 视频
{
    "tag":"video",
    "text":null,
    "combined_forwarded_chat_history":null,
    "image":null,
    "video":{
        "content":"https://openapi.seatalk.io/messaging/v2/file/uieLdasuUWhebwrBksadfjBMSFIUEmwkefjhgjksdJKK8GJSFNsdjk"
    },
    "file":null
}

// 文件
{
    "tag":"file",
    "text":null,
    "combined_forwarded_chat_history":null,
    "image":null,
    "video":null,
    "file":{
        "content":"https://openapi.seatalk.io/messaging/v2/file/lskdfewnOKNFiewbeBKuKEKQW7JWEfjefnqwesdi8JFNekqlkfwqef",
        "filename": "sample.txt"
    }
}
```
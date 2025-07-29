# 服务端 API 事件回调

通过事件回调，您的应用可以在启用相关事件后，从 SeaTalk 接收事件通知。借助事件回调，您的应用可以与 SeaTalk 开放平台的各种开放能力集成，以实时响应不同的操作。例如，机器人在收到“机器人用户发送消息”事件通知后，可以立即在 1 对 1 聊天中向用户致以问候。

要为您的应用启用事件回调，您只需配置一个回调 URL。SeaTalk 开放平台将通过 HTTP POST 请求，以 JSON 格式将事件通知推送到您的应用。

为您的应用启用事件回调后，您的应用就可以监听来自 SeaTalk 的不同事件。您可以参考本文档最后一节中的示例代码，了解如何处理不同的回调事件。

## 回调 URL 验证

为了成功为您的应用配置回调 URL，该 URL 必须通过 SeaTalk 的验证测试。下图说明了回调 URL 的验证工作原理：

1.  当您在应用配置页面上单击保存回调 URL 时，将触发验证测试。
2.  SeaTalk 会向此 URL 发送一个带有“seatalk_challenge”参数的 HTTP POST 请求。
3.  收到请求后，您的服务器必须在 5 秒内以 HTTP 状态码 200 响应，并在响应体中原样包含“seatalk_challenge”参数的值。如果未收到响应，SeaTalk 最多会重试 3 次。
4.  如果 SeaTalk 在 5 秒内收到有效响应，则验证测试通过，并为您的应用成功配置回调 URL。
5.  但是，如果在验证过程中发生错误，验证测试将失败，您需要重试。URL 配置页面上会显示一条错误消息，以便您了解配置失败的原因。

### 验证请求 JSON

SeaTalk 将发送到您的回调 URL 进行验证的 HTTP POST 请求的正文如下（参考第 2 步）：

```json
{
  "event_id": "1098780",
  "event_type": "event_verification",
  "timestamp": 1611220944,
  "app_id": "NDYyMDU1MTY3NzQ1",
  "event": {
    "seatalk_challenge": "23j98gjbearh023hg"
  }
}
```

### 返回响应 JSON

收到 SeaTalk 的验证请求后，您的服务器应返回以下响应（参考第 3 步）：

```json
{
  "seatalk_challenge": "23j98gjbearh023hg"
}
```

### 验证失败的可能原因

1.  输入的 URL 无法访问
2.  URL 在 5 秒内没有响应（在 SeaTalk 重试 3 次后）
3.  URL 返回的响应包含无效信息或格式错误
4.  当前此应用下正在验证回调 URL
5.  发生内部错误

您可以参考本文档末尾的示例代码，了解如何处理回调 URL 验证测试。

## 启用事件

为您的应用成功配置回调 URL 后，您的应用现在可以监听事件，并在启用的事件发生时接收事件通知。

目前，在回调 URL 配置成功后，所有可用事件将自动为您的应用启用。

有关支持的事件的完整列表，请参阅[事件列表](https://open.seatalk.io/docs/list-of-events)。

未来将支持事件启用的自定义，一旦准备就绪，我们会在此处提供更新。或者，您也可以在 SeaTalk 上与我们联系。

## 响应事件

收到请求后，您的服务器必须在 5 秒内以 HTTP 状态码 200 响应。如果未收到响应，SeaTalk 最多会重试 3 次。

## 配置回调 URL

**第 1 步：** 前往 SeaTalk 开放平台的开发者门户，进入需要事件回调功能的应用的配置页面。

**第 2 步：** 单击左侧菜单栏上的“事件回调”，进入事件回调配置页面。

**第 3 步：** 单击 URL 文本框旁边的“编辑”图标，输入用于验证的 URL。

**第 4 步：** 单击“保存”以触发回调 URL 验证测试。

**第 5 步：** URL 验证成功后，您将看到已配置的 URL，并且下方会出现“事件”部分。

## 签名密钥

为确保事件通知的发送者是 SeaTalk 开放平台，系统会为您的应用分配一个签名密钥。您将在回调 URL 文本框下看到签名密钥，并且可以随时重置。

SeaTalk 开放平台会在回调请求的 HTTP 标头中包含一个 `Signature` 字段。当您在收到事件通知后需要验证其发送者身份时，请按以下步骤操作：

1.  将回调请求的完整正文和您应用的签名密钥连接起来，作为 SHA-256 函数的输入。
2.  使用标准 base16 和全小写对输出（哈希值）进行编码，以计算签名。
3.  将计算出的签名与回调请求 HTTP 标头中的签名进行比较，以验证发件人身份。如果它们相同，则此事件通知由 SeaTalk 开放平台发送。

例如，如果签名密钥是 `1234567812345678`，您的应用收到如下 HTTP 请求：

```http
POST / HTTP/1.1
Content-Type: application/json
Signature: 30c15f277e1d1847c4425ac4b3d7658457caf53da3005385db15a96ea1f2e0a4

{
  "event_id": "1098780",
  "event_type": "event_verification",
  "timestamp": 1611220944,
  "app_id": "NDYyMDU1MTY3NzQ1",
  "event": {
    "seatalk_challenge": "23j98gjbearh023hg"
  }
}
```

SHA-256 函数的输入将是：

```
{"event_id":"1098780","event_type":"event_verification","timestamp":1611220944,"app_id":"NDYyMDU1MTY3NzQ1","event":{"seatalk_challenge":"23j98gjbearh023hg"}}1234567812345678
```

计算出的签名将是：

```
// hashlib.sha256(request.body + signing_secret).hexdigest()
30c15f277e1d1847c4425ac4b3d7658457caf53da3005385db15a96ea1f2e0a4
```

由于计算出的签名与请求头中的签名相同，您可以确认该事件通知是由 SeaTalk 开放平台发送的。

## 示例代码

以下是一个机器人的回调处理程序的示例代码。该处理程序监听来自 SeaTalk 的事件，包括回调 URL 验证事件 (`event_verification`) 和其他与机器人相关的事件。该处理程序还验证事件通知是否确实由 SeaTalk 发送。

```python
import hashlib
import json
from typing import Dict, Any

from flask import Flask, request

# 设置
SIGNING_SECRET = b"xxxx"

# 事件列表
# 参考: https://open.seatalk.io/docs/list-of-events
EVENT_VERIFICATION = "event_verification"
NEW_BOT_SUBSCRIBER = "new_bot_subscriber"
MESSAGE_FROM_BOT_SUBSCRIBER = "message_from_bot_subscriber"
INTERACTIVE_MESSAGE_CLICK = "interactive_message_click"
BOT_ADDED_TO_GROUP_CHAT = "bot_added_to_group_chat"
BOT_REMOVED_FROM_GROUP_CHAT = "bot_removed_from_group_chat"
NEW_MENTIONED_MESSAGE_RECEIVED_FROM_GROUP_CHAT = "new_mentioned_message_received_from_group_chat"

app = Flask(__name__)


def is_valid_signature(signing_secret: bytes, body: bytes, signature: str) -> bool:
    # 参考: https://open.seatalk.io/docs/server-apis-event-callback
    return hashlib.sha256(body + signing_secret).hexdigest() == signature


@app.route("/bot-callback", methods=["POST"])
def bot_callback_handler():
    body: bytes = request.get_data()
    signature: str = request.headers.get("signature")
    # 1. 验证签名
    if not is_valid_signature(SIGNING_SECRET, body, signature):
        return ""
    # 2. 处理事件
    data: Dict[str, Any] = json.loads(body)
    event_type: str = data.get("event_type", "")
    if event_type == EVENT_VERIFICATION:
        return data.get("event")
    elif event_type == NEW_BOT_SUBSCRIBER:
        # 在此填写您自己的代码
        pass
    elif event_type == MESSAGE_FROM_BOT_SUBSCRIBER:
        # 在此填写您自己的代码
        pass
    elif event_type == INTERACTIVE_MESSAGE_CLICK:
        # 在此填写您自己的代码
        pass
    elif event_type == BOT_ADDED_TO_GROUP_CHAT:
        # 在此填写您自己的代码
        pass
    elif event_type == BOT_REMOVED_FROM_GROUP_CHAT:
        # 在此填写您自己的代码
        pass
    elif event_type == NEW_MENTIONED_MESSAGE_RECEIVED_FROM_GROUP_CHAT:
        # 在此填写您自己的代码
        pass
    else:
        pass
    return ""
```

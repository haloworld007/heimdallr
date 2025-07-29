# 入门指南

本页介绍了创建一个简单的 SeaTalk 机器人、设置事件回调、订阅机器人等步骤。完成本教程后，该机器人将能够在私聊中发送和接收消息。

在开始之前，我们建议您下载本教程中将使用的[示例代码](https://open.seatalk.io/docs/downloads/Getting-Started-Tutorial-Code.zip)。

## 1. 注册新机器人

访问 [open.seatalk.io](https://open.seatalk.io)，点击“开始构建”或“创建应用”，以启动应用创建向导。您也可以在您的应用列表中点击“创建应用”来启动。按照向导中的步骤完成应用的基本配置。

**第 1 步：基本应用信息**
[图片：应用创建向导第一步，填写应用名称和描述]

**第 2 步：服务和数据范围配置**
[图片：应用创建向导第二步，选择数据范围]

您的新应用默认状态为“未配置”。在“能力”部分找到“机器人”卡片，然后点击“启用”按钮。
[图片：在能力部分启用机器人]

成功启用某项能力后，它将出现在页面左侧的菜单中，并且您将被引导至新添加能力的配置菜单。此外，该能力的默认 API 权限将为您的应用启用。

## 2. 接收交互

### 2.1 准备机器人 API 回调

为了让 SeaTalk 开放平台（SOP）能够调用我们的服务，无论是为了验证我们的机器人还是接收事件，我们的机器人都需要提供一个 API。让我们首先创建一个 URI 为 `/callback` 的 API。

```go
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
)

func main() {
	c := make(chan os.Signal)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM, syscall.SIGHUP, syscall.SIGINT, syscall.SIGKILL, syscall.SIGQUIT)
	r := gin.Default()

	r.POST("/callback", func(ctx *gin.Context) {
		ctx.JSON(http.StatusOK, gin.H{
			"message": "Callback API",
		})
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: r,
	}

	go func() {
		log.Println("starting web, listening on", srv.Addr)
		err := srv.ListenAndServe()
		if err != nil && err != http.ErrServerClosed {
			log.Fatalln("failed starting web on", srv.Addr, err)
		}
	}()

	for {
		<-c
		log.Println("terminate service")
		ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
		defer cancel()

		log.Println("shutting down web on", srv.Addr)
		if err := srv.Shutdown(ctx); err != nil {
			log.Fatalln("failed shutdown server", err)
		}
		log.Println("web gracefully stopped")
		os.Exit(0)
	}
}
```

之后，用这个命令运行 Golang 代码：

```bash
go run main.go
```

### 2.2 验证回调请求

为了保护我们的资源免受未经身份验证和未经授权的实体的侵害，验证每个发送到我们机器人服务器的事件请求都来自 SOP 至关重要。为此，我们可以检查并验证请求头中的签名，SOP 会在每个回调 API 请求中发送该签名。

**请求头**
| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `Content-Type` | string | 请求头格式 |
| `Signature` | string | 用于确保请求由 SeaTalk 发送的签名 |

```go
package main

/* ... */
import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"io"

	"github.com/gin-gonic/gin"
)

func WithSOPSignatureValidation() gin.HandlerFunc {
	return func(ctx *gin.Context) {
		r := ctx.Request
		signature := r.Header.Get("signature")

		if signature == "" {
			ctx.JSON(http.StatusForbidden, nil)
			return
		}

		body, err := io.ReadAll(r.Body)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}

		hasher := sha256.New()
		// 将此替换为您的机器人签名密钥
		signingSecret := "YOUR SIGNING SECRET" 
		hasher.Write(append(body, []byte(signingSecret)...))
		targetSignature := hex.EncodeToString(hasher.Sum(nil))

		if signature != targetSignature {
			ctx.JSON(http.StatusForbidden, nil)
			return
		}

		r.Body = io.NopCloser(bytes.NewBuffer(body))
		ctx.Next()
	}
}

func main() {
	/* ... */
	r := gin.Default()
	r.Use(WithSOPSignatureValidation())
	/* ... */
}
```

要获取您的“签名密钥”，您可以在“事件回调 URL”页面上看到它（步骤 2.4.5）。现在我们的机器人将只接收来自 SOP 的请求。应用上述代码后，别忘了重新运行您的代码。

### 2.3 处理事件："event_verification"

在配置回调 URL 时（步骤 2.4），为了验证我们的机器人，SOP 服务器会向此端点发送一个请求。该请求包含 `seatalk_challenge` 令牌，我们需要将其作为响应再次发送回去。更多详情请参阅[服务端 API 事件回调](docs/server_api_event_callback.md)。

```go
package main

/* ... */

type SOPEventCallbackReq struct {
	EventID   string `json:"event_id"`
	EventType string `json:"event_type"`
	TimeStamp uint64 `json:"timestamp"`
	AppID     string `json:"app_id"`
	Event     Event  `json:"event"`
}

type SOPEventVerificationResp struct {
	SeatalkChallenge string `json:"seatalk_challenge"`
}

type Event struct {
	SeatalkChallenge string `json:"seatalk_challenge"`
}

func main() {
	/* ... */
	r := gin.Default()
	r.Use(WithSOPSignatureValidation())

	r.POST("/callback", func(ctx *gin.Context) {
		var reqSOP SOPEventCallbackReq
		if err := ctx.BindJSON(&reqSOP); err != nil {
			ctx.JSON(http.StatusInternalServerError, "something wrong")
			return
		}
		log.Printf("INFO: received event with event_type %s", reqSOP.EventType)

		switch reqSOP.EventType {
		case "event_verification":
			ctx.JSON(http.StatusOK, SOPEventVerificationResp{SeatalkChallenge: reqSOP.Event.SeatalkChallenge})
		default:
			log.Printf("ERROR: event %s not handled yet!", reqSOP.EventType)
			ctx.JSON(http.StatusOK, "Success")
		}
	})
	/* ... */
}
```

现在我们的机器人可以处理这个事件了。别忘了重新运行您的代码。

### 2.4 配置事件回调 URL

为了能够接收事件交互，您首先需要设置机器人事件回调 URL。现在，您可以尝试在本地计算机上运行 Golang 程序。但是，在此之前，您必须将您的 Localhost 暴露到互联网上。您可以使用 `ngrok` 之类的工具。

`ngrok` 通过将您的本地地址（127.0.0.1）和端口（例如：8080）转发到互联网来工作。安装 `ngrok` 后，您可以在终端中运行此命令：

```bash
ngrok http 8080
```
[图片：ngrok 界面，显示转发地址]

假设您已成功将本地服务器暴露到互联网，下一步是按照以下步骤配置 SOP 事件回调 URL。我们将使用 `https://a215-103-86-128-2.ngrok-free.app` 并附加我们的端点 `/callback`，使其变为 `https://a215-103-86-128-2.ngrok-free.app/callback`。

**步骤 2.4.1**: 进入 SeaTalk 开放平台的开发者门户，并进入需要事件回调功能的应用的配置页面。
**步骤 2.4.2**: 点击左侧菜单栏上的“事件回调”进入配置页面。
[图片：事件回调配置页面]
**步骤 2.4.3**: 点击 URL 文本框旁边的“编辑”图标。
[图片：编辑回调 URL]
**步骤 2.4.4**: 填写事件回调 URL，例如：`https://{{your_domain}}/callback`。
**步骤 2.4.5**: 点击“保存”以触发回调 URL 验证测试。
[图片：保存回调 URL 并显示签名密钥]
**步骤 2.4.6**: 成功配置回调 URL 后，支持的事件将自动为机器人启用。

太棒了！现在我们的机器人可以被 SOP 验证了。接下来，我们将更新我们的机器人，使其能够接收 SOP 发送的事件。完整的事件列表，请参阅[此文档](https://open.seatalk.io/docs/list-of-events)。

### 2.5 处理事件："message_from_bot_subscriber"

当订阅者向机器人发送消息时，机器人将收到此事件，并可以根据此消息构建响应。在此示例中，我们将只记录收到的消息。

**`message_from_bot_subscriber` 事件参数**

**请求体**
| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `event_id` | string | 事件的 ID |
| `event_type` | string | 事件的类型，此处为 `message_from_bot_subscriber` |
| `timestamp` | uint64 | 此事件发生的时间 |
| `app_id` | string | 接收事件通知的应用 ID |
| `event` | object | 事件特定信息 |
| `∟ employee_code` | string | 订阅者的 `employee_code` |
| `∟ message` | object | 收到的消息 |

```go
package main

/* ... */
type Event struct {
	SeatalkChallenge string  `json:"seatalk_challenge"`
	EmployeeCode     string  `json:"employee_code"`
	Message          Message `json:"message"`
}

type Message struct {
	Tag  string      `json:"tag"`
	Text TextMessage `json:"text"`
}

type TextMessage struct {
	Content   string `json:"content"`
	PlainText string `json:"plain_text"`
}

func main() {
	/* ... */
	r := gin.Default()
	r.Use(WithSOPSignatureValidation())

	r.POST("/callback", func(ctx *gin.Context) {
		var reqSOP SOPEventCallbackReq
		if err := ctx.BindJSON(&reqSOP); err != nil {
			ctx.JSON(http.StatusInternalServerError, "something wrong")
			return
		}
		log.Printf("INFO: received event with event_type %s", reqSOP.EventType)

		switch reqSOP.EventType {
		case "event_verification":
			ctx.JSON(http.StatusOK, SOPEventVerificationResp{SeatalkChallenge: reqSOP.Event.SeatalkChallenge})
		case "message_from_bot_subscriber":
			// 我们稍后将使用 employee_code 来响应用户消息
			log.Printf("INFO: message received: %s, with employee_code: %s", reqSOP.Event.Message.Text.Content, reqSOP.Event.EmployeeCode)
			ctx.JSON(http.StatusOK, "Success")
		default:
			log.Printf("ERROR: event %s not handled yet!", reqSOP.EventType)
			ctx.JSON(http.StatusOK, "Success")
		}
	})
	/* ... */
}
```

现在我们的机器人能够接收其订阅者发送的消息了。请尝试向您新创建的机器人发送消息，并确保服务器日志中包含该消息。别忘了重新运行您的代码。
[图片：服务器日志显示收到的消息]

## 3. 发起主动操作

### 3.1 处理认证

为了通过 SOP API 发起操作，必须对您的机器人进行身份验证。为此，我们需要为向 SOP API 发出的每个请求提供一个 `access_token`。可以通过调用“获取访问令牌” API 来获取此令牌，有效期为 7200 秒。请记住，必须有缓存机制，以防止为每个请求都获取新令牌。完整文档请参阅[获取应用访问令牌](docs/get_app_access_token.md)。

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

type AppAccessToken struct {
	AccessToken string `json:"access_token"`
	ExpireTime  uint64 `json:"expire"`
}

type SOPAuthAppResp struct {
	Code           int    `json:"code"`
	AppAccessToken string `json:"app_access_token"`
	Expire         uint64 `json:"expire"`
}

var (
	appAccessToken AppAccessToken
)

func GetAppAccessToken() AppAccessToken {
	timeNow := time.Now().Unix()

	accTokenIsEmpty := appAccessToken == AppAccessToken{}
	accTokenIsExpired := appAccessToken.ExpireTime < uint64(timeNow)

	if accTokenIsEmpty || accTokenIsExpired {
		// 替换为您的 App ID 和 App Secret
		body := []byte(fmt.Sprintf(`{"app_id": "%s", "app_secret": "%s"}`, "<<YOUR APP ID>>", "<<YOUR APP SECRET>>"))

		req, err := http.NewRequest("POST", "https://openapi.seatalk.io/auth/app_access_token", bytes.NewBuffer(body))
		if err != nil {
			log.Printf("ERROR: [GetAppAccessToken] failed to create an HTTP request: %v", err)
			return appAccessToken
		}
		req.Header.Add("Content-Type", "application/json")

		client := &http.Client{}
		res, err := client.Do(req)
		// ... 错误处理 ...
		defer res.Body.Close()
		
		resp := &SOPAuthAppResp{}
		if err := json.NewDecoder(res.Body).Decode(resp); err != nil {
			// ... 错误处理 ...
			return appAccessToken
		}

		if resp.Code != 0 {
			log.Printf("ERROR: [GetAppAccessToken] response code is not 0, error code %d", resp.Code)
			return appAccessToken
		}

		appAccessToken = AppAccessToken{
			AccessToken: resp.AppAccessToken,
			ExpireTime:  resp.Expire,
		}
	}

	return appAccessToken
}
```

**如何获取您的 App ID 和 App Secret：**
1.  前往 SeaTalk 开放平台网站并登录。
2.  点击“应用”标签页。
3.  点击您的应用名称进入详情页面。
4.  进入“基本信息和凭证”页面，向下滚动到“凭证”部分，您可以在此处复制 App ID 和 App Secret。

### 3.2 发送消息给订阅者

要向订阅者发送消息，我们的机器人需要调用 SOP API。在此示例中，我们将使用 API“发送消息给机器人订阅者”。

**请求体结构**
| 参数 | 类型 | 是否必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `employee_code` | string | 是 | 订阅者的 `employee_code` |
| `message` | object | 是 | 要发送的消息 |

**消息对象**
| 参数 | 类型 | 是否必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `tag` | string | 是 | 消息类型，此处为 `text` |
| `text` | object | 是 | 文本消息对象 |

完整文档请参阅[此处](https://open.seatalk.io/docs/messaging_send-message-to-bot-subscriber_)。

```go
type SOPSendMessageToUser struct {
	EmployeeCode string     `json:"employee_code"`
	Message      SOPMessage `json:"message"`
}

type SOPMessage struct {
	Tag  string     `json:"tag"`
	Text SOPTextMsg `json:"text,omitempty"`
}

type SOPTextMsg struct {
	Format  int8   `json:"format"` // 1: Markdown, 2: 纯文本
	Content string `json:"content"`
}

type SendMessageToUserResp struct {
	Code int `json:"code"`
}

func SendMessageToUser(ctx context.Context, message, employeeCode string) error {
	bodyJson, _ := json.Marshal(SOPSendMessageToUser{
		EmployeeCode: employeeCode,
		Message: SOPMessage{
			Tag: "text",
			Text: SOPTextMsg{
				Format:  2, // 纯文本消息
				Content: message,
			},
		},
	})

	req, err := http.NewRequest("POST", "https://openapi.seatalk.io/messaging/v2/single_chat", bytes.NewBuffer(bodyJson))
	if err != nil {
		return err
	}
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "Bearer "+GetAppAccessToken().AccessToken)

	client := &http.Client{}
	res, err := client.Do(req)
	// ... 错误处理 ...
	defer res.Body.Close()

	resp := &SendMessageToUserResp{}
	if err := json.NewDecoder(res.Body).Decode(resp); err != nil {
		return err
	}

	if resp.Code != 0 {
		return fmt.Errorf("something wrong, response code: %v", resp.Code)
	}

	return nil
}
```

现在，是时候将所有代码组合在一起了。使用完整的代码，我们的机器人将通过接收 `"message_from_bot_subscriber"` 事件并调用 `"Send Message to Bot Subscriber"` API，对每条用户消息回复“Hello World”。

**是时候测试我们的机器人了！**
现在去 SeaTalk，搜索您的机器人名称，然后向它发送任何消息。您应该会收到“Hello World”消息。
[图片：与机器人聊天的截图，机器人回复了 Hello World]

收到了吗？如果收到了，那么恭喜您！您已成功创建了您的第一个机器人！
如果没有收到任何消息？别担心，您可以查阅[错误码文档](https://open.seatalk.io/docs/reference_server-api-error-code)来排查错误。

## 4. 接下来做什么？

有兴趣为您的机器人开发更多功能吗？您可以前往[了解机器人能力](https://open.seatalk.io/docs/Understanding-Bot-Capabilities)查看 SOP 机器人支持的所有功能！

祝您好运！
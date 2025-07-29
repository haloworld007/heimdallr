# 获取 Jira Issue 详情 (`GET /issue/{issueIdOrKey}`)

## 概述

该接口用于根据 Issue 的 ID 或 Key 获取其详细信息。

如果提供的标识符不直接匹配任何 Issue，系统会进行一次不区分大小写的搜索，并检查 Issue 是否已被移动。如果找到匹配的 Issue，则返回其详细信息。

此操作可以匿名访问，但访问权限取决于项目的配置。

**权限要求**:

- 对 Issue 所在项目的“浏览项目”权限。
- 如果配置了问题级别的安全性，则需要有查看该问题的权限。

**OAuth 2.0 授权范围 (Scopes)**:

- **经典模式 (推荐)**: `read:jira-work`
- **精细模式**: `read:issue-meta:jira`, `read:issue-security-level:jira` 等。

---

## API 端点

### 请求方法

`GET`

### URL

`/rest/api/2/issue/{issueIdOrKey}`

---

## 请求参数

### 路径参数

| 参数           | 类型   | 是否必填 | 描述                                    |
| :------------- | :----- | :------- | :-------------------------------------- |
| `issueIdOrKey` | string | 是       | Issue 的 ID 或 Key (例如, `PROJ-123`)。 |

### 查询参数

| 参数            | 类型          | 描述                                                                                                                                                                                                                 |
| :-------------- | :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fields`        | array[string] | 指定要返回的字段列表，接受逗号分隔的值。例如 `fields=summary,comment`。<li>`*all`：返回所有字段。</li><li>`*navigable`：返回所有可导航字段。</li><li>`-description`：返回除描述外的所有字段。</li>默认返回所有字段。 |
| `fieldsByKeys`  | boolean       | 是否通过字段的 key (而不是 ID) 来引用 `fields` 参数中的字段。默认为 `false`。                                                                                                                                        |
| `expand`        | string        | 用于在响应中包含额外的关联信息，接受逗lema分隔的列表。例如：<li>`renderedFields`：返回 HTML 格式的字段值。</li><li>`changelog`：返回最近的更新历史。</li><li>`transitions`：返回该 Issue 所有可能的状态转换。</li>   |
| `properties`    | array[string] | 指定要返回的 Issue 属性列表，接受逗号分隔的值。例如 `properties=*all,-prop1`。                                                                                                                                       |
| `updateHistory` | boolean       | 是否将此 Issue 的项目添加到用户的“最近查看”列表中。默认为 `false`。                                                                                                                                                  |

---

## 响应

### 成功响应 (200 OK)

请求成功时返回。响应体为一个 `IssueBean` 对象，包含 Issue 的详细信息。

| 属性        | 类型   | 描述                                                       |
| :---------- | :----- | :--------------------------------------------------------- |
| `id`        | string | Issue 的 ID。                                              |
| `key`       | string | Issue 的 Key。                                             |
| `fields`    | object | 包含 Issue 各字段详细信息的对象。                          |
| `changelog` | object | （当 `expand` 包含 `changelog` 时）Issue 的变更历史。      |
| `editmeta`  | object | （当 `expand` 包含 `editmeta` 时）关于可编辑字段的元数据。 |
| ...         | ...    | 其他展开的属性。                                           |

### 错误响应

- **401 Unauthorized**: 未经授权的请求。
- **404 Not Found**: 未找到指定的 Issue。

---

## 示例

### 请求示例 (Node.js)

```javascript
// 此代码示例使用 'node-fetch' 库
const fetch = require('node-fetch');

const issueIdOrKey = 'PROJ-1';
const yourDomain = 'your-domain.atlassian.net';
const email = 'email@example.com';
const apiToken = '<api_token>'; // 你的 Jira API Token

fetch(`https://${yourDomain}/rest/api/2/issue/${issueIdOrKey}`, {
  method: 'GET',
  headers: {
    Authorization: `Basic ${Buffer.from(`${email}:${apiToken}`).toString('base64')}`,
    Accept: 'application/json',
  },
})
  .then((response) => {
    console.log(`Response: ${response.status} ${response.statusText}`);
    return response.json(); // 使用 .json() 解析响应体
  })
  .then((data) => console.log(JSON.stringify(data, null, 2)))
  .catch((err) => console.error(err));
```

### 响应示例 (200 OK)

```json
{
  "fields": {
    "watcher": {
      "isWatching": false,
      "self": "https://your-domain.atlassian.net/rest/api/2/issue/EX-1/watchers",
      "watchCount": 1
    },
    "attachment": [
      {
        "author": {
          "accountId": "5b10a2844c20165700ede21g",
          "accountType": "atlassian",
          "active": false,
          "avatarUrls": {
            "16x16": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=16&s=16",
            "24x24": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=24&s=24",
            "32x32": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=32&s=32",
            "48x48": "https://avatar-management--avatars.server-location.prod.public.atl-paas.net/initials/MK-5.png?size=48&s=48"
          },
          "displayName": "Mia Krystof",
          "key": "",
          "name": "",
          "self": "https://your-domain.atlassian.net/rest/api/2/user?accountId=5b10a2844c20165700ede21g"
        },
        "content": "https://your-domain.atlassian.net/jira/rest/api/3/attachment/content/10001",
        "created": "2023-06-24T19:24:50.000+0000",
        "filename": "debuglog.txt",
        "id": 10001,
        "mimeType": "text/plain",
        "self": "https://your-domain.atlassian.net/rest/api/2/attachments/10001",
        "size": 2460
      }
    ],
    "sub-tasks": [
      {
        "id": "10000",
        "outwardIssue": {
          "fields": {
            "status": {
              "iconUrl": "https://your-domain.atlassian.net/images/icons/statuses/open.png",
              "name": "Open"
            }
          },
          "id": "10003",
          "key": "ED-2",
          "self": "https://your-domain.atlassian.net/rest/api/2/issue/ED-2"
        },
        "type": {
          "id": "10000",
          "inward": "Parent",
          "name": "",
          "outward": "Sub-task"
        }
      }
    ],
    "description": "Main order flow broken",
    "project": {
      "avatarUrls": {
        "16x16": "https://your-domain.atlassian.net/secure/projectavatar?size=xsmall&pid=10000",
        "24x24": "https://your-domain.atlassian.net/secure/projectavatar?size=small&pid=10000",
        "32x32": "https://your-domain.atlassian.net/secure/projectavatar?size=medium&pid=10000",
        "48x48": "https://your-domain.atlassian.net/secure/projectavatar?size=large&pid=10000"
      },
      "id": "10000",
      "insight": {
        "lastIssueUpdateTime": "2021-04-22T05:37:05.000+0000",
        "totalIssueCount": 100
      },
      "key": "EX",
      "name": "Example",
      "projectCategory": {
        "description": "First Project Category",
        "id": "10000",
        "name": "FIRST",
        "self": "https://your-domain.atlassian.net/rest/api/2/projectCategory/10000"
      },
      "self": "https://your-domain.atlassian.net/rest/api/2/project/EX",
      "simplified": false,
      "style": "classic"
    },
    "comment": [
      {
        "author": {
          "accountId": "5b10a2844c20165700ede21g",
          "active": false,
          "displayName": "Mia Krystof",
          "self": "https://your-domain.atlassian.net/rest/api/2/user?accountId=5b10a2844c20165700ede21g"
        },
        "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque eget venenatis elit. Duis eu justo eget augue iaculis fermentum. Sed semper quam laoreet nisi egestas at posuere augue semper.",
        "created": "2021-01-17T12:34:00.000+0000",
        "id": "10000",
        "self": "https://your-domain.atlassian.net/rest/api/2/issue/10010/comment/10000",
        "updateAuthor": {
          "accountId": "5b10a2844c20165700ede21g",
          "active": false,
          "displayName": "Mia Krystof",
          "self": "https://your-domain.atlassian.net/rest/api/2/user?accountId=5b10a2844c20165700ede21g"
        },
        "updated": "2021-01-18T23:45:00.000+0000",
        "visibility": {
          "identifier": "Administrators",
          "type": "role",
          "value": "Administrators"
        }
      }
    ],
    "issuelinks": [
      {
        "id": "10001",
        "outwardIssue": {
          "fields": {
            "status": {
              "iconUrl": "https://your-domain.atlassian.net/images/icons/statuses/open.png",
              "name": "Open"
            }
          },
          "id": "10004L",
          "key": "PR-2",
          "self": "https://your-domain.atlassian.net/rest/api/2/issue/PR-2"
        },
        "type": {
          "id": "10000",
          "inward": "depends on",
          "name": "Dependent",
          "outward": "is depended by"
        }
      },
      {
        "id": "10002",
        "inwardIssue": {
          "fields": {
            "status": {
              "iconUrl": "https://your-domain.atlassian.net/images/icons/statuses/open.png",
              "name": "Open"
            }
          },
          "id": "10004",
          "key": "PR-3",
          "self": "https://your-domain.atlassian.net/rest/api/2/issue/PR-3"
        },
        "type": {
          "id": "10000",
          "inward": "depends on",
          "name": "Dependent",
          "outward": "is depended by"
        }
      }
    ],
    "worklog": [
      {
        "author": {
          "accountId": "5b10a2844c20165700ede21g",
          "active": false,
          "displayName": "Mia Krystof",
          "self": "https://your-domain.atlassian.net/rest/api/2/user?accountId=5b10a2844c20165700ede21g"
        },
        "comment": "I did some work here.",
        "id": "100028",
        "issueId": "10002",
        "self": "https://your-domain.atlassian.net/rest/api/2/issue/10010/worklog/10000",
        "started": "2021-01-17T12:34:00.000+0000",
        "timeSpent": "3h 20m",
        "timeSpentSeconds": 12000,
        "updateAuthor": {
          "accountId": "5b10a2844c20165700ede21g",
          "active": false,
          "displayName": "Mia Krystof",
          "self": "https://your-domain.atlassian.net/rest/api/2/user?accountId=5b10a2844c20165700ede21g"
        },
        "updated": "2021-01-18T23:45:00.000+0000",
        "visibility": {
          "identifier": "276f955c-63d7-42c8-9520-92d01dca0625",
          "type": "group",
          "value": "jira-developers"
        }
      }
    ],
    "updated": 1,
    "timetracking": {
      "originalEstimate": "10m",
      "originalEstimateSeconds": 600,
      "remainingEstimate": "3m",
      "remainingEstimateSeconds": 200,
      "timeSpent": "6m",
      "timeSpentSeconds": 400
    }
  },
  "id": "10002",
  "key": "ED-1",
  "self": "https://your-domain.atlassian.net/rest/api/2/issue/10002"
}
```

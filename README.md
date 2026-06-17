# Auto Like

一个用于向特定平台发送批量点赞请求的 Python 高并发脚本。

## 功能特性

- **多线程并发** — 支持自定义线程数，默认 50 线程
- **连接池优化** — 大连接池 (100) 提升请求吞吐
- **线程安全统计** — 实时追踪成功/失败次数、成功率、QPS
- **进度显示** — 每 10% 输出进度，每 1000 次成功请求显示状态
- **可配置延迟** — 随机延迟 0.1~0.5 秒，可自行调整

## 依赖安装

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install requests psutil
```

## 使用方法

```bash
python auto_like.py
```

运行后根据提示输入：
1. **点赞次数** — 要发送的总请求数
2. **线程数** — 并发线程数（默认 50）

## 配置说明

在 `auto_like.py` 顶部配置区可修改以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `BASE_URL` | `https://apiv4.720yun.com` | API 基础地址 |
| `PRODUCT_ID` | `edvkb9d7r8y` | 目标产品 ID |
| `APP_KEY` | — | 应用密钥 |
| `APP_AUTHORIZATION` | `""` | 授权令牌（如需要请填写） |
| `COOKIES` | — | Cookie 信息（如接口需要） |
| `DEFAULT_THREAD_COUNT` | `50` | 默认线程数 |
| `MIN_DELAY` / `MAX_DELAY` | `0.1` / `0.5` | 请求间随机延迟范围（秒） |
| `CONNECTION_POOL_SIZE` | `100` | HTTP 连接池大小 |

## 许可证

[MIT License](LICENSE) - Copyright (c) 2026 凉秋

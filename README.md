# Train Tools — Vue + pywebview + FastAPI 桌面应用模版

Vue 3 + Vite 前端，FastAPI 后端，pywebview 桌面窗口封装。可构建为单文件 exe 或目录分发。

## 前置要求

- Python >= 3.14（通过 `uv` 管理）
- Node.js >= 22
- make 4.x（通过 chocolatey 安装）

## 快速开始

```bash
# 本地开发调试（自动安装依赖）
make desktop

# 构建单文件 exe → dist/train-tools.exe
make build

# 构建目录分发 → dist/train-tools/
make build-dir
```

## 命令

| make 目标       | 说明                            |
|----------------|--------------------------------|
| `desktop`      | 启动 Vite + API + pywebview 桌面窗口 |
| `build`        | 构建单文件 exe                   |
| `build-dir`    | 构建目录分发                     |
| `dev-backend`  | 仅启动 API（uvicorn --reload）   |
| `dev-frontend` | 仅启动 Vite dev server          |
| `clean`        | 清理 node_modules、dist、__pycache__ |

## 环境管理

```bash
uv sync          # 安装 Python 依赖
uv lock          # 更新锁定文件
uv run python    # 在虚拟环境中运行
```

## 目录结构

```
├── backend/           FastAPI 后端 + pywebview 桌面入口
├── frontend/          Vue 3 + Vite 前端
├── scripts/           构建脚本 (dev/build/build-dir)
├── .gitignore         版本忽略规则
├── Makefile           快捷命令
├── pyproject.toml     uv 依赖配置
└── uv.lock            uv 锁定文件
```

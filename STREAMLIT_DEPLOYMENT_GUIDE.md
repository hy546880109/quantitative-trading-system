# Streamlit Cloud 部署指南

## 📋 部署概述

本指南将帮助你将量化交易系统部署到 Streamlit Cloud，实现云端在线访问。

### ✅ 部署优势

- 🌐 **免费托管**: Streamlit Cloud 提供免费的应用托管服务
- 🔄 **自动部署**: 连接GitHub仓库，自动同步更新
- 📊 **真实数据**: 云端支持 TuShare 和 Yahoo Finance 数据源
- 📱 **移动访问**: 已优化的移动端适配，随时随地访问
- 🔒 **安全可靠**: Streamlit官方托管，安全稳定

---

## 🚀 快速部署步骤

### 步骤 1: 准备 GitHub 仓库

你的代码已经推送到 GitHub，仓库地址：
```
https://github.com/hy546880109/quantitative-trading-system
```

### 步骤 2: 访问 Streamlit Cloud

1. 打开浏览器访问: **https://share.streamlit.io**
2. 使用 GitHub 账号登录（推荐）
3. 授权 Streamlit 访问你的 GitHub 仓库

### 步骤 3: 创建新应用

点击 **"New app"** 按钮，填写以下信息：

| 配置项 | 填写内容 |
|--------|---------|
| **Repository** | `hy546880109/quantitative-trading-system` |
| **Branch** | `main` |
| **Main file path** | `gui.py` |
| **App name (optional)** | `量化交易系统` 或自定义 |

### 步骤 4: 高级设置（可选）

点击 **"Advanced settings"**，可配置：

#### 环境变量（重要）

如果需要使用 TuShare 数据源，添加环境变量：

```
Key: TUSHARE_TOKEN
Value: 你的TuShare Token（从 https://tushare.pro 获取）
```

#### Python 版本

推荐使用：`Python 3.11`

#### 依赖文件

默认使用：`requirements.txt`（已配置）

### 步骤 5: 部署应用

1. 点击 **"Deploy"** 按钮
2. 等待部署完成（首次部署约2-5分钟）
3. 部署成功后，获得访问链接

---

## 📝 部署配置详解

### requirements.txt

已配置以下依赖：

```txt
pandas>=1.5.0          # 数据处理
numpy>=1.21.0          # 数值计算
tushare>=1.2.0         # TuShare数据源
streamlit>=1.28.0      # Streamlit框架
matplotlib>=3.5.0      # 图表绘制
plotly>=5.0.0          # 交互式图表
yfinance>=1.2.0        # Yahoo Finance数据源
pytest>=7.0.0          # 测试框架
```

### .streamlit/config.toml

已优化云端配置：

```toml
[server]
enableCORS = false            # 云端必需
enableXsrfProtection = true   # 安全保护
headless = true               # 无头模式

[browser]
gatherUsageStats = false      # 禁用统计
serverAddress = "0.0.0.0"     # 云端监听

[runner]
fixMatplotlib = true          # 修复matplotlib兼容性
```

---

## 🔧 部署后配置

### 1. 添加 TuShare Token（可选）

如果需要使用 TuShare 真实A股数据：

#### 方法 A: 通过环境变量（推荐）

1. 在 Streamlit Cloud 应用页面点击 **"Settings"**
2. 选择 **"Secrets"** 标签
3. 添加以下内容：

```toml
TUSHARE_TOKEN = "你的token值"
```

4. 点击 **"Save"**，应用会自动重启

#### 方法 B: 通过代码配置

在 `gui.py` 中读取环境变量：

```python
import os
token = os.environ.get('TUSHARE_TOKEN')
```

### 2. 自定义应用 URL

Streamlit Cloud 默认提供随机 URL，可以自定义：

格式：`https://[你的应用名]-[随机ID].streamlit.app`

在应用设置中修改应用名称。

---

## 📊 功能测试清单

部署完成后，测试以下功能：

### ✅ 基础功能测试

- [ ] 应用成功启动
- [ ] 侧边栏显示正常
- [ ] 界面布局正确
- [ ] 移动端适配生效（手机访问测试）

### ✅ 数据源测试

- [ ] **模拟数据**: 加载成功，K线图显示
- [ ] **Yahoo Finance**: 选择美股（如 AAPL），数据加载成功
- [ ] **TuShare**: 如已配置token，测试A股数据加载

### ✅ 回测功能测试

- [ ] 选择策略（如 MA策略）
- [ ] 调整参数
- [ ] 运行回测成功
- [ ] 结果图表显示
- [ ] 交易记录表格显示

### ✅ 移动端测试

- [ ] 手机浏览器访问
- [ ] 侧边栏正常展开/折叠
- [ ] 按钮易于点击
- [ ] 图表正常显示
- [ ] 表格可滚动

---

## 🔄 更新与维护

### 自动部署机制

Streamlit Cloud 支持**自动部署**：

1. 本地修改代码
2. 推送到 GitHub: `git push origin main`
3. Streamlit Cloud 自动检测更新
4. 自动重新部署应用（约1-2分钟）

### 手动重启

如需立即重启应用：

1. 在应用页面点击 **"Settings"**
2. 点击 **"Reboot app"**

### 查看日志

遇到问题时，查看部署日志：

1. 点击 **"Settings"**
2. 选择 **"Logs"** 标签
3. 查看实时运行日志

---

## 🐛 常见问题解决

### 问题 1: 部署失败 - 依赖安装错误

**症状**: 日志显示 `pip install` 失败

**解决方案**:
```bash
# 检查 requirements.txt 格式
# 确保每个依赖单独一行
# 不要包含系统级依赖（如 apt-get）
```

### 问题 2: 应用启动后白屏

**症状**: 应用启动但界面不显示

**解决方案**:
```bash
# 检查 gui.py 是否有语法错误
# 查看日志中的错误信息
# 测试本地运行: streamlit run gui.py
```

### 问题 3: TuShare Token 不生效

**症状**: 提示 "请提供TuShare Token"

**解决方案**:
```toml
# 在 Secrets 中正确配置：
TUSHARE_TOKEN = "你的实际token值"

# 不要写成：
TUSHARE_TOKEN = "'你的token值'"  # 多了引号
```

### 问题 4: Yahoo Finance 数据加载慢

**症状**: 加载美股数据等待时间长

**原因**: Yahoo Finance API 国际访问较慢

**解决方案**:
- 使用模拟数据测试功能
- 或配置 TuShare 使用A股数据
- 增加超时等待时间

### 问题 5: 移动端布局异常

**症状**: 手机访问界面错乱

**解决方案**:
- 清除浏览器缓存
- 确认已部署最新版本（包含移动端适配）
- 使用 Chrome DevTools 模拟测试

---

## 💡 性能优化建议

### 1. 减少数据加载时间

```python
# 在 gui.py 中添加缓存
@st.cache_data
def load_stock_data(symbol, start, end):
    # 数据加载逻辑
    return data
```

### 2. 优化图表渲染

```python
# 使用 Plotly 而非 Matplotlib（已实现）
# Plotly 在云端渲染更快
```

### 3. 减少依赖包

```txt
# 只保留必需依赖
# 移除未使用的包以加快部署
```

---

## 🌐 访问链接示例

部署成功后，你会获得类似链接：

```
https://quantitative-trading-system-xyz123.streamlit.app
```

### 分享链接

你可以将链接分享给他人，无需安装即可使用你的量化交易系统！

---

## 📞 技术支持

### Streamlit 官方文档

- [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-cloud)
- [部署常见问题](https://docs.streamlit.io/streamlit-cloud/troubleshooting)

### 项目相关

- GitHub 仓库: https://github.com/hy546880109/quantitative-trading-system
- 移动端测试指南: `MOBILE_ADAPTATION_TEST.md`
- 数据源配置: `DATA_SOURCE_GUIDE.md`

---

## ✅ 部署成功检查

完成部署后，确认以下事项：

- [ ] 获得云端访问链接
- [ ] 应用正常运行
- [ ] 模拟数据功能可用
- [ ] Yahoo Finance 功能可用（如需要）
- [ ] TuShare 功能可用（如已配置）
- [ ] 移动端访问正常
- [ ] 已分享链接给需要的人

---

## 🎉 部署完成！

你的量化交易系统现在已经在云端运行，可以：

1. 📊 **在线回测**: 无需本地安装，随时随地访问
2. 📱 **移动访问**: 手机、平板完美适配
3. 🔄 **自动更新**: 推送代码即可自动部署
4. 🔗 **分享协作**: 分享链接给团队或朋友

---

**部署日期**: 2026-04-04
**Streamlit Cloud 版本**: 最新版
**Python 版本**: 3.11（推荐）

---

## 📸 部署截图指南

### 部署界面示例

1. **New App 页面**:
   - Repository: 选择你的GitHub仓库
   - Branch: main
   - Main file: gui.py

2. **Settings 页面**:
   - Secrets: 配置环境变量
   - Theme: 自动继承 .streamlit/config.toml

3. **Logs 页面**:
   - 查看实时运行日志
   - 调试错误信息

---

## 🔐 安全建议

### 不要硬编码 Token

❌ **错误做法**:
```python
token = "your_hardcoded_token"  # 不要这样！
```

✅ **正确做法**:
```python
import os
token = os.environ.get('TUSHARE_TOKEN')  # 从环境变量读取
```

### Secrets 管理

- TuShare Token 等敏感信息放在 Secrets 中
- 不要提交 `.env` 文件到 GitHub
- 使用 `.gitignore` 排除敏感文件

---

祝你部署成功！如有问题，查看日志或参考 Streamlit 官方文档。
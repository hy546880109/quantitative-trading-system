# 真实数据源配置指南

## 🎯 概述

量化交易系统支持三种数据源：

| 数据源 | 费用 | 速度 | 数据质量 | 推荐场景 |
|--------|------|------|----------|----------|
| **模拟数据** | 免费 | 最快 | 随机生成 | 策略验证、学习测试 |
| **Yahoo Finance** | 免费 | 较慢（有限流） | 真实数据 | 美股、少量A股 |
| **TuShare** | 免费/付费 | 快 | 高质量A股数据 | **实盘回测（推荐）** |

---

## 🚀 快速启动（推荐）

### 方式1: 命令行启动
```bash
cd /Users/hy/Documents/03_AutomationScripts/quantitative-trading-system
chmod +x start.sh
./start.sh
```

### 方式2: 直接运行
```bash
streamlit run gui.py
```

浏览器自动打开: http://localhost:8501

---

## 📊 配置TuShare数据源（推荐）

### 第一步：注册TuShare账号

1. 访问 https://tushare.pro/register
2. 注册账号（免费）
3. 登录后，进入【个人中心】→【接口Token】
4. 复制你的Token（类似：`1234567890abcdef...`）

### 第二步：在系统中使用

启动Streamlit后：
1. 侧边栏选择数据源: **TuShare**
2. 粘贴你的Token
3. 选择股票代码和日期范围
4. 点击**加载数据**

### TuShare权限说明

| 权限级别 | 积分要求 | 可用接口 | 说明 |
|---------|---------|---------|------|
| **免费用户** | 0分 | 日线、指数 | 基础需求够用 |
| 初级用户 | 2000分 | 分钟线 | 需要积分 |
| 高级用户 | 5000分 | 实时数据 | 需要付费或贡献 |

---

## 🌐 配置Yahoo Finance

### 无需配置，直接使用

1. 侧边栏选择数据源: **Yahoo Finance**
2. 选择股票代码
3. 点击**加载数据**

### 注意事项

- ⚠️ **有速率限制**：短时间内请求过多会被限流
- ⚠️ **A股代码转换**：系统自动将`.SH`转为`.SS`（Yahoo格式）
- ✅ **美股数据完善**：AAPL、TSLA、NVDA等

---

## 🔧 测试数据源

运行测试脚本验证数据源是否正常：

```bash
python3 test_data_source.py
```

根据提示输入TuShare Token（可选）

---

## 💡 常见问题

### Q1: 为什么Web版本（GitHub Pages）只能用模拟数据？

**A**: 浏览器安全限制。Web版本是纯前端HTML/JavaScript，受CORS策略限制，无法直接访问第三方API。Streamlit版本使用Python后端，无此限制。

**解决方案**：
- ✅ 使用Streamlit版本（推荐）
- 🔧 为Web版本添加后端API（需服务器部署）

### Q2: Yahoo Finance提示"Too Many Requests"怎么办？

**A**: 被限流了。解决方案：
1. 等待几分钟再试
2. 使用TuShare（更稳定）
3. 使用模拟数据测试策略

### Q3: TuShare积分不够怎么办？

**A**: 免费用户每日有足够额度用于日线数据回测。如需分钟线：
1. 在TuShare社区贡献代码/文档赚积分
2. 购买专业版

### Q4: 可以同时使用多个数据源吗？

**A**: 可以！不同股票可以用不同数据源：
- A股 → TuShare（数据更准）
- 美股 → Yahoo Finance（免费）

---

## 📞 支持

遇到问题？
1. 查看日志输出
2. 运行测试脚本：`python3 test_data_source.py`
3. GitHub Issue: https://github.com/hy546880109/quantitative-trading-system/issues

---

## 🎓 学习资源

- TuShare文档: https://tushare.pro/document/2
- Yahoo Finance API: https://pypi.org/project/yfinance/
- Streamlit教程: https://docs.streamlit.io/

---

**祝量化交易顺利！** 📈
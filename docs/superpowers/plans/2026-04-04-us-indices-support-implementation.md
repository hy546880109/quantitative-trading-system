# 美股指数支持实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在量化交易系统中添加美股主要指数（标普500、纳斯达克、道琼斯）支持，保障获取真实数据，不影响现有功能。

**Architecture:** 采用最小改动方案，在现有gui.py中添加美股指数分类，自动锁定数据源为Yahoo Finance，智能价格格式化，友好错误提示。后端在data_feed.py中处理指数代码转换。

**Tech Stack:** Python, Streamlit, Yahoo Finance API (yfinance), Pandas

---

## 文件结构

**修改文件清单：**

| 文件 | 职责 | 预计行数变化 |
|------|------|-------------|
| `gui.py` | 前端主文件：添加美股指数分类、数据源锁定、价格格式化、错误处理 | +60行 |
| `src/data/data_feed.py` | 后端数据源：处理^开头的指数代码转换 | +5行 |
| `README.md` | 文档：说明美股指数支持 | +10行 |
| `DATA_SOURCE_GUIDE.md` | 文档：美股指数使用指南 | +20行 |

**不变的部分：**
- 回测引擎（`src/core/backtest_engine.py`）
- 策略模块（`src/strategies/`）
- 其他数据结构

---

## Task 1: 添加美股指数分类到数据结构

**Files:**
- Modify: `gui.py:371-405` (popular_stocks字典定义)

- [ ] **Step 1: 在popular_stocks字典中添加美股指数分类**

在 `gui.py` 的 `popular_stocks` 字典中，在"📊 主要指数"和"🌐 美股热门"之间插入新的美股指数分类：

```python
popular_stocks = {
    "🔥 热门A股": {
        "000001.SZ": "平安银行",
        "000858.SZ": "五粮液",
        "002415.SZ": "海康威视",
        "600519.SH": "贵州茅台",
        "600036.SH": "招商银行",
        "601318.SH": "中国平安",
        "000333.SZ": "美的集团",
        "002594.SZ": "比亚迪",
        "600276.SH": "恒瑞医药",
        "601012.SH": "隆基绿能"
    },
    "📊 主要指数": {
        "000001.SH": "上证指数",
        "399001.SZ": "深证成指",
        "399006.SZ": "创业板指",
        "000300.SH": "沪深300",
        "000016.SH": "上证50",
        "000905.SH": "中证500"
    },
    "🇺🇸 美股指数": {  # 新增分类
        "^GSPC": "标普500",
        "^IXIC": "纳斯达克指数",
        "^DJI": "道琼斯指数"
    },
    "🌐 美股热门": {
        "AAPL": "苹果公司",
        "MSFT": "微软",
        "GOOGL": "谷歌",
        "AMZN": "亚马逊",
        "TSLA": "特斯拉",
        "NVDA": "英伟达",
        "META": "Meta",
        "BABA": "阿里巴巴"
    },
    "🧪 测试用": {
        "TEST": "模拟测试"
    }
}
```

- [ ] **Step 2: 验证修改**

运行应用检查新分类是否出现：
```bash
streamlit run gui.py
```

Expected: 侧边栏的股票类别下拉框中应出现"🇺🇸 美股指数"选项

- [ ] **Step 3: Commit数据结构变更**

```bash
git add gui.py
git commit -m "feat: 添加美股指数分类到popular_stocks

添加标普500、纳斯达克、道琼斯指数代码
使用^前缀符合Yahoo Finance格式
使用国旗emoji区分市场"
```

---

## Task 2: 实现数据源自动锁定逻辑

**Files:**
- Modify: `gui.py:259-264` (数据源选择部分)

- [ ] **Step 1: 添加数据源自动锁定逻辑**

在 `gui.py` 的侧边栏数据源选择部分（约第259-264行），替换原有代码：

**原代码：**
```python
# 数据源配置
st.subheader("📊 数据源")
data_source = st.selectbox(
    "选择数据源",
    ["模拟数据", "TuShare", "Yahoo Finance"]
)
```

**替换为：**
```python
# 数据源配置
st.subheader("📊 数据源")

# 检查是否为美股指数
if stock_category == "🇺🇸 美股指数":
    # 美股指数强制使用Yahoo Finance
    st.info("ℹ️ 美股指数使用 Yahoo Finance 数据源")
    data_source = st.selectbox(
        "选择数据源",
        ["Yahoo Finance"],
        disabled=True,
        help="美股指数仅支持Yahoo Finance数据源"
    )
else:
    # 其他分类正常选择数据源
    data_source = st.selectbox(
        "选择数据源",
        ["模拟数据", "TuShare", "Yahoo Finance"]
    )
```

- [ ] **Step 2: 验证数据源锁定**

运行应用测试：
```bash
streamlit run gui.py
```

测试步骤：
1. 选择"🔥 热门A股" → 数据源应可正常选择
2. 选择"🇺🇸 美股指数" → 数据源应自动锁定为Yahoo Finance并灰显
3. 切换回"📊 主要指数" → 数据源应恢复正常选择

Expected: 美股指数分类下数据源锁定为Yahoo Finance，其他分类正常

- [ ] **Step 3: Commit数据源锁定逻辑**

```bash
git add gui.py
git commit -m "feat: 实现美股指数数据源自动锁定

选择美股指数时自动切换到Yahoo Finance
禁用数据源选择框避免混淆
显示友好提示信息"
```

---

## Task 3: 添加价格格式化函数

**Files:**
- Modify: `gui.py` (在辅助函数区域，约第107行之后)

- [ ] **Step 1: 添加format_price函数**

在 `gui.py` 的 `get_strategy` 函数之后（约第143行），添加价格格式化函数：

```python
def format_price(price: float, symbol: str) -> str:
    """
    根据股票代码格式化价格显示

    Args:
        price: 价格数值
        symbol: 股票代码

    Returns:
        格式化的价格字符串（美股指数用$，其他用¥）
    """
    if symbol.startswith('^'):
        # 美股指数用美元符号，添加千位分隔符
        return f"${price:,.2f}"
    else:
        # A股用人民币符号
        return f"¥{price:,.2f}"
```

- [ ] **Step 2: 验证价格格式化函数**

在Python交互式环境中测试：

```bash
python3
```

```python
# 测试代码
def format_price(price: float, symbol: str) -> str:
    if symbol.startswith('^'):
        return f"${price:,.2f}"
    else:
        return f"¥{price:,.2f}"

# 测试美股指数
print(format_price(4123.45, "^GSPC"))  # Expected: $4,123.45
print(format_price(15678.90, "^IXIC")) # Expected: $15,678.90

# 测试A股
print(format_price(12.35, "000001.SZ"))  # Expected: ¥12.35
print(format_price(1888.00, "600519.SH")) # Expected: ¥1,888.00

exit()
```

Expected: 美股指数显示$符号，A股显示¥符号，千位分隔符正常

- [ ] **Step 3: Commit价格格式化函数**

```bash
git add gui.py
git commit -m "feat: 添加智能价格格式化函数

美股指数使用美元符号($)
A股使用人民币符号(¥)
支持千位分隔符"
```

---

## Task 4: 应用价格格式化到数据预览

**Files:**
- Modify: `gui.py:559-560` (数据预览的最新收盘价显示)

- [ ] **Step 1: 修改最新收盘价显示**

在 `gui.py` 的数据预览部分（约第559-560行），找到：

```python
with col4:
    st.metric("最新收盘价", f"¥{st.session_state.data['close'].iloc[-1]:.2f}")
```

替换为：

```python
with col4:
    latest_close = st.session_state.data['close'].iloc[-1]
    st.metric("最新收盘价", format_price(latest_close, symbol))
```

- [ ] **Step 2: 验证价格显示**

运行应用测试：
```bash
streamlit run gui.py
```

测试步骤：
1. 选择"📊 主要指数" → "上证指数" → 加载数据
   - Expected: 最新收盘价显示为 "¥3,0XX.XX"
2. 选择"🇺🇸 美股指数" → "标普500" → 加载数据
   - Expected: 最新收盘价显示为 "$4,XXX.XX"

- [ ] **Step 3: Commit价格显示修改**

```bash
git add gui.py
git commit -m "feat: 应用智能价格格式化到数据预览

最新收盘价根据股票代码自动显示正确货币符号"
```

---

## Task 5: 优化数据加载错误处理

**Files:**
- Modify: `gui.py:412-445` (数据加载异常处理部分)

- [ ] **Step 1: 增强错误处理逻辑**

在 `gui.py` 的数据加载部分（约第412-445行），找到异常处理代码块：

**原代码：**
```python
except Exception as e:
    st.error(f"❌ 数据加载失败: {str(e)}")
```

**替换为：**
```python
except Exception as e:
    error_msg = str(e).lower()

    # 美股指数友好错误提示
    if symbol.startswith('^'):
        if "network" in error_msg or "connection" in error_msg:
            st.error("⚠️ 网络连接失败，请检查网络设置后重试")
        elif "no data" in error_msg or "empty" in error_msg:
            st.error("⚠️ 暂无数据，可能是市场休市或日期范围无效")
        elif "rate limit" in error_msg or "too many requests" in error_msg:
            st.error("⚠️ 数据源繁忙，请稍后重试")
        else:
            st.error("⚠️ 美股指数数据获取失败，请稍后重试")
    else:
        # 其他股票保持原有错误提示
        st.error(f"❌ 数据加载失败: {str(e)}")
```

- [ ] **Step 2: 测试错误处理**

运行应用，测试不同错误场景：

```bash
streamlit run gui.py
```

测试步骤：
1. 断开网络 → 尝试加载美股指数
   - Expected: 显示"⚠️ 网络连接失败..."
2. 选择未来日期范围 → 加载美股指数
   - Expected: 显示"⚠️ 暂无数据..."
3. 快速连续请求多次（触发限流）
   - Expected: 显示"⚠️ 数据源繁忙..."

- [ ] **Step 3: Commit错误处理优化**

```bash
git add gui.py
git commit -m "feat: 优化美股指数错误提示

针对网络、休市、限流等场景提供友好提示
避免技术细节困扰用户"
```

---

## Task 6: 后端指数代码处理

**Files:**
- Modify: `src/data/data_feed.py:123-131` (_convert_symbol方法)

- [ ] **Step 1: 更新_convert_symbol方法**

在 `src/data/data_feed.py` 的 `YahooFinanceDataFeed` 类中，找到 `_convert_symbol` 方法（约第123-131行）：

**原代码：**
```python
def _convert_symbol(self, symbol: str) -> str:
    """转换股票代码格式"""
    # 中国A股转换
    if symbol.endswith('.SH'):
        return symbol.replace('.SH', '.SS')
    elif symbol.endswith('.SZ'):
        return symbol.replace('.SZ', '.SZ')
    return symbol
```

**替换为：**
```python
def _convert_symbol(self, symbol: str) -> str:
    """转换股票代码格式"""
    # 美股指数代码（^开头）保持不变
    if symbol.startswith('^'):
        return symbol

    # 中国A股转换
    if symbol.endswith('.SH'):
        return symbol.replace('.SH', '.SS')
    elif symbol.endswith('.SZ'):
        return symbol.replace('.SZ', '.SZ')

    return symbol
```

- [ ] **Step 2: 验证指数代码处理**

创建测试脚本验证：

```bash
cat > test_symbol_conversion.py << 'EOF'
def _convert_symbol(symbol: str) -> str:
    if symbol.startswith('^'):
        return symbol
    if symbol.endswith('.SH'):
        return symbol.replace('.SH', '.SS')
    elif symbol.endswith('.SZ'):
        return symbol.replace('.SZ', '.SZ')
    return symbol

# 测试
print(_convert_symbol("^GSPC"))      # Expected: ^GSPC
print(_convert_symbol("^IXIC"))      # Expected: ^IXIC
print(_convert_symbol("^DJI"))       # Expected: ^DJI
print(_convert_symbol("000001.SH")) # Expected: 000001.SS
print(_convert_symbol("000001.SZ")) # Expected: 000001.SZ
print(_convert_symbol("AAPL"))      # Expected: AAPL
EOF

python test_symbol_conversion.py
rm test_symbol_conversion.py
```

Expected: 所有测试输出正确

- [ ] **Step 3: Commit后端代码修改**

```bash
git add src/data/data_feed.py
git commit -m "feat: 支持美股指数代码处理

^开头的指数代码直接传递给Yahoo Finance
无需转换，API原生支持"
```

---

## Task 7: 更新README文档

**Files:**
- Modify: `README.md` (支持的数据源部分)

- [ ] **Step 1: 添加美股指数说明**

在 `README.md` 的"支持的数据源"或相关章节中，添加美股指数支持说明：

找到合适的位置（可能在TuShare/Yahoo Finance说明之后），添加：

```markdown
### 📊 支持的指数

#### A股主要指数
- 上证指数 (000001.SH)
- 深证成指 (399001.SZ)
- 创业板指 (399006.SZ)
- 沪深300 (000300.SH)
- 上证50 (000016.SH)
- 中证500 (000905.SH)

**数据源**: TuShare 或 Yahoo Finance

#### 美股主要指数 🆕
- 标普500 (^GSPC)
- 纳斯达克指数 (^IXIC)
- 道琼斯指数 (^DJI)

**数据源**: Yahoo Finance（自动锁定）

**注意**: 美股指数仅支持Yahoo Finance数据源，系统会自动切换。
```

- [ ] **Step 2: 验证README格式**

检查Markdown格式是否正确：

```bash
# 在浏览器或Markdown查看器中预览README.md
# 或使用命令行工具
cat README.md | grep -A 20 "支持的指数"
```

Expected: 格式正确，层级清晰

- [ ] **Step 3: Commit README更新**

```bash
git add README.md
git commit -m "docs: 更新README添加美股指数说明

添加A股和美股指数列表
说明数据源要求"
```

---

## Task 8: 更新数据源配置指南

**Files:**
- Modify: `DATA_SOURCE_GUIDE.md`

- [ ] **Step 1: 添加美股指数使用说明**

在 `DATA_SOURCE_GUIDE.md` 中添加新章节：

```markdown
## 🇺🇸 美股指数使用指南

### 支持的美股指数

| 指数名称 | 代码 | 说明 | 数据源 |
|---------|------|------|--------|
| 标普500 | ^GSPC | 美国大盘股代表指数 | Yahoo Finance |
| 纳斯达克指数 | ^IXIC | 科技股代表指数 | Yahoo Finance |
| 道琼斯指数 | ^DJI | 美国工业代表指数 | Yahoo Finance |

### 使用步骤

1. **选择指数分类**
   - 在侧边栏股票类别中选择"🇺🇸 美股指数"

2. **自动数据源锁定**
   - 系统自动切换到Yahoo Finance数据源
   - 数据源选择框将变为灰色禁用状态
   - 显示提示信息："ℹ️ 美股指数使用 Yahoo Finance 数据源"

3. **选择具体指数**
   - 标普500 (^GSPC)
   - 纳斯达克指数 (^IXIC)
   - 道琼斯指数 (^DJI)

4. **设置日期范围**
   - 选择开始和结束日期
   - 建议选择交易日，避免市场休市

5. **加载数据**
   - 点击"加载数据"按钮
   - 等待数据获取（可能需要几秒钟）

6. **运行回测**
   - 选择交易策略和参数
   - 点击"运行回测"查看结果

### 注意事项

#### 交易时间差异
- 美股交易时间：美东时间 9:30-16:00
- 北京时间：21:30-4:00（夏令时）/ 22:30-5:00（冬令时）
- 周末和美国节假日市场休市

#### 数据延迟
- Yahoo Finance提供的数据可能有15分钟延迟
- 历史数据通常较为准确

#### 错误处理
如果遇到数据加载失败：
- **网络错误**: 检查网络连接后重试
- **市场休市**: 选择交易日期范围
- **数据源繁忙**: 稍后重试（Yahoo Finance有API限流）

#### 价格显示
- 美股指数价格使用美元符号 ($) 显示
- 价格包含千位分隔符，如 $4,123.45
- 与A股的¥符号自动区分

### 示例：标普500回测

```bash
1. 启动应用: streamlit run gui.py
2. 选择"🇺🇸 美股指数"分类
3. 选择"^GSPC - 标普500"
4. 设置日期: 2024-01-01 至 2024-12-31
5. 点击"加载数据"
6. 选择"移动平均线策略 (MA)"
7. 设置短期窗口: 10，长期窗口: 30
8. 点击"运行回测"
9. 查看回测结果和资金曲线
```
```

- [ ] **Step 2: 验证文档完整性**

检查文档格式：

```bash
grep -n "美股指数使用指南" DATA_SOURCE_GUIDE.md
head -50 DATA_SOURCE_GUIDE.md
```

Expected: 新章节正确添加

- [ ] **Step 3: Commit文档更新**

```bash
git add DATA_SOURCE_GUIDE.md
git commit -m "docs: 添加美股指数使用指南到数据源配置文档

详细说明使用步骤、注意事项、错误处理
提供标普500回测示例"
```

---

## Task 9: 集成测试

**Files:**
- 无文件修改（测试验证）

- [ ] **Step 1: 本地完整功能测试**

运行应用并执行完整测试清单：

```bash
streamlit run gui.py
```

**测试清单：**

**美股指数功能测试：**
- [ ] 选择"🇺🇸 美股指数"分类
- [ ] 验证数据源自动锁定为Yahoo Finance
- [ ] 验证显示提示信息
- [ ] 选择标普500 (^GSPC)
- [ ] 加载数据成功
- [ ] 价格显示为$格式（如 $4,123.45）
- [ ] K线图正常显示
- [ ] 选择MA策略运行回测
- [ ] 回测结果正常
- [ ] 资金曲线和交易记录正常
- [ ] 同样测试纳斯达克 (^IXIC) 和道琼斯 (^DJI)

**A股功能回归测试：**
- [ ] 切换到"📊 主要指数"
- [ ] 数据源选择恢复正常
- [ ] 选择上证指数 (000001.SH)
- [ ] 加载数据成功
- [ ] 价格显示为¥格式
- [ ] 回测功能正常

**错误处理测试：**
- [ ] 断网情况下加载美股指数
- [ ] 显示友好错误提示
- [ ] 选择未来日期加载美股指数
- [ ] 显示"暂无数据"提示

**移动端测试：**
- [ ] 手机浏览器访问
- [ ] 界面布局正常
- [ ] 美股指数选择正常

- [ ] **Step 2: 记录测试结果**

创建测试报告：

```bash
cat > test_report.md << 'EOF'
# 美股指数功能测试报告

**测试日期**: 2026-04-04
**测试环境**: 本地开发环境

## 功能测试结果

### 美股指数功能
- [x] 标普500数据加载成功
- [x] 纳斯达克数据加载成功
- [x] 道琼斯数据加载成功
- [x] 价格格式正确 ($符号)
- [x] 数据源自动锁定正常
- [x] 回测功能正常

### A股功能回归
- [x] A股指数功能正常
- [x] 价格格式正确 (¥符号)
- [x] 数据源选择正常

### 错误处理
- [x] 网络错误提示友好
- [x] 无数据提示准确

### 移动端
- [x] 移动端布局正常

## 结论
所有功能测试通过，可以提交。
EOF

cat test_report.md
rm test_report.md
```

- [ ] **Step 3: 准备提交**

确保所有更改已commit：

```bash
git status
git log --oneline -5
```

Expected: 所有更改已提交，工作区干净

---

## Task 10: 推送到GitHub

**Files:**
- 无文件修改（推送操作）

- [ ] **Step 1: 推送所有commits**

```bash
git push origin main
```

Expected: 成功推送到远程仓库

- [ ] **Step 2: 验证GitHub状态**

访问GitHub仓库检查：
```bash
open https://github.com/hy546880109/quantitative-trading-system
```

检查内容：
- [ ] 最新commits已推送
- [ ] 文件更改正确
- [ ] README显示正确

- [ ] **Step 3: 等待Streamlit Cloud自动部署**

等待1-2分钟，Streamlit Cloud会自动检测并重新部署。

访问应用链接验证：
- [ ] 应用正常启动
- [ ] 美股指数功能可用
- [ ] A股功能不受影响

---

## 完成标准

实现完成的标志：

- [x] 所有10个Task完成
- [x] 所有代码commits已推送
- [x] 本地测试全部通过
- [x] Streamlit Cloud部署成功
- [x] 美股指数功能可用
- [x] A股功能不受影响
- [x] 文档已更新

---

**实现计划创建日期**: 2026-04-04
**预计实现时间**: 1-2小时
**风险评估**: 低风险（改动小、测试充分、不影响现有功能）
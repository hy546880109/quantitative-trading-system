# 移动端分辨率适配测试指南

## 📱 适配功能概述

本项目已完成移动端分辨率适配优化,支持多种设备尺寸:

### 支持的设备类型

- **手机设备** (< 480px): iPhone、Android手机
- **平板设备** (480px - 768px): iPad、Android平板
- **桌面设备** (768px - 1920px): 笔记本、台式机
- **高分辨率设备** (> 1920px): 4K显示器、大屏幕

## 🎯 主要优化内容

### 1. Streamlit GUI (gui.py)

**优化内容**:
- ✅ 响应式标题尺寸 (1.5rem - 3rem)
- ✅ 优化侧边栏布局 (移动端100%宽度)
- ✅ 优化指标卡片字体大小
- ✅ 优化数据表格字体和间距
- ✅ 增大按钮触摸区域 (min-height: 44px)
- ✅ 优化图表高度 (移动端400px)
- ✅ 支持横屏模式优化
- ✅ 支持高分辨率屏幕

**CSS媒体查询**:
```css
@media only screen and (max-width: 768px)  // 平板
@media only screen and (max-width: 480px)  // 手机
@media screen and (orientation: landscape)  // 横屏
@media only screen and (min-width: 1920px) // 高分辨率
```

### 2. HTML Web界面 (web/index.html)

**优化内容**:
- ✅ 侧边栏自适应宽度 (320px → 100%)
- ✅ 指标网格自适应列数 (6列 → 2列 → 1列)
- ✅ 表格字体和间距优化
- ✅ 触摸友好的按钮尺寸
- ✅ 横屏模式优化布局
- ✅ 打印样式优化

### 3. 简化版HTML (web/index_simple.html)

**优化内容**:
- ✅ 同index.html的完整适配
- ✅ 更紧凑的布局优化

## 🧪 测试方法

### 方法1: Chrome DevTools 模拟

1. **打开应用**:
   ```bash
   # Streamlit应用
   streamlit run gui.py

   # 或HTML界面
   # 在浏览器打开 web/index.html
   ```

2. **启动DevTools**:
   - 按 `F12` 或 `Cmd+Option+I` (Mac)
   - 点击设备工具栏图标 📱

3. **选择设备测试**:
   - iPhone 12 Pro (390px)
   - iPhone SE (375px)
   - iPad Air (820px)
   - Samsung Galaxy S20 (360px)
   - 或自定义宽度

4. **测试横屏模式**:
   - 点击旋转图标 🔄 切换横屏/竖屏

### 方法2: 真实设备测试

1. **局域网访问**:
   ```bash
   # 启动Streamlit (局域网模式)
   streamlit run gui.py --server.address 0.0.0.0

   # 查看本机IP
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **手机访问**:
   - 确保手机和电脑在同一WiFi
   - 浏览器访问: `http://你的IP:8501`

### 方法3: BrowserStack 测试

访问 [BrowserStack](https://www.browserstack.com/) 进行跨设备测试。

## ✅ 测试检查清单

### 手机竖屏 (< 480px)

- [ ] 标题文字清晰可见
- [ ] 侧边栏占满屏幕宽度
- [ ] 指标卡片单列排列
- [ ] 表格数据可滚动查看
- [ ] 按钮足够大,易于点击
- [ ] 图表高度适中 (400px)
- [ ] 输入框高度 ≥ 44px

### 平板竖屏 (480px - 768px)

- [ ] 标题大小适中
- [ ] 侧边栏占满宽度
- [ ] 指标卡片双列排列
- [ ] 表格字体清晰
- [ ] 按钮易于点击
- [ ] 图表显示正常

### 平板横屏

- [ ] 侧边栏30%宽度,固定左侧
- [ ] 主内容区域70%宽度
- [ ] 图表宽度充分利用

### 高分辨率 (> 1920px)

- [ ] 侧边栏宽度400px
- [ ] 指标网格6列排列
- [ ] 标题字体3rem
- [ ] 指标字体2rem

## 📊 响应式断点总结

| 断点 | 设备类型 | 侧边栏宽度 | 指标列数 | 标题大小 |
|------|---------|-----------|---------|---------|
| < 480px | 手机 | 100% | 1列 | 1.5rem |
| 480-768px | 平板竖屏 | 100% | 2列 | 2rem |
| 768px横屏 | 平板横屏 | 30% | 6列 | 2.5rem |
| 768-1920px | 桌面 | 320px | 6列 | 2.5rem |
| > 1920px | 高分辨率 | 400px | 6列 | 3rem |

## 🔧 优化技术细节

### 触摸友好性

根据Apple Human Interface Guidelines:
- 最小触摸目标: **44px × 44px**
- 所有按钮、输入框已优化

### 图表响应式

- 移动端: 400px高度 (节省空间)
- 桌面端: 600-700px高度 (详细展示)

### 表格优化

- 移动端字体: 0.8rem
- 横向滚动支持
- 紧凑间距: padding 6px

## 🎨 CSS优化示例

```css
/* 手机设备优化 */
@media (max-width: 480px) {
    .stButton button {
        min-height: 44px;  /* 触摸友好 */
        width: 100%;       /* 占满宽度 */
    }

    .stDataFrame table {
        font-size: 0.85rem;  /* 移动端字体 */
    }

    .js-plotly-plot {
        height: 400px !important;  /* 适中高度 */
    }
}
```

## 📝 注意事项

1. **Streamlit限制**:
   - Streamlit本身有一定的响应式支持
   - 我们通过CSS进一步优化

2. **测试覆盖**:
   - 建议测试主流设备尺寸
   - 关注用户常用设备

3. **性能优化**:
   - 响应式CSS不影响性能
   - 图表在移动端可能加载稍慢

## 🚀 快速启动测试

```bash
# 1. 启动应用
streamlit run gui.py

# 2. 打开浏览器DevTools (F12)

# 3. 切换设备模拟模式

# 4. 测试不同尺寸:
#    - 375px (iPhone SE)
#    - 390px (iPhone 12)
#    - 768px (iPad)
#    - 1920px (桌面)
```

## 📖 相关文档

- [响应式Web设计基础](https://web.dev/responsive-web-design-basics/)
- [Apple HIG - 触摸目标](https://developer.apple.com/design/human-interface-guidelines/ios/user-interaction/standard-controls/)
- [MDN - 媒体查询](https://developer.mozilla.org/zh-CN/docs/Web/CSS/Media_Queries)

---

**适配完成日期**: 2026-04-04
**测试建议**: 在真实移动设备上进行实际测试,确保最佳用户体验
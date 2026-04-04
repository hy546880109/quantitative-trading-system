#!/bin/bash
# 量化交易系统启动脚本

echo "🚀 启动量化交易系统..."
echo ""
echo "📊 数据源说明："
echo "  - 模拟数据: 默认选项，无需配置"
echo "  - Yahoo Finance: 免费但有限流，选择后直接使用"
echo "  - TuShare: 需要token，访问 https://tushare.pro 注册获取"
echo ""
echo "💡 提示: 首次运行可能需要安装依赖: pip install -r requirements.txt"
echo ""

streamlit run gui.py --server.port 8501 --server.address localhost
"""
数据源测试脚本
验证TuShare和Yahoo Finance是否能正常获取数据
"""
import sys
sys.path.insert(0, '.')
from src.data.data_feed import DataFeed
from datetime import datetime, timedelta

def test_yahoo_finance():
    """测试Yahoo Finance数据源"""
    print("=" * 60)
    print("测试 Yahoo Finance 数据源")
    print("=" * 60)

    try:
        feed = DataFeed('yahoo')

        # 测试美股
        print("\n📈 测试美股: AAPL (苹果)")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        bars = feed.fetch_daily_data(
            'AAPL',
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )

        if bars:
            print(f"✅ 获取到 {len(bars)} 条数据")
            print(f"   最新: 日期={bars[-1].datetime}, 收盘价=${bars[-1].close:.2f}")
        else:
            print("❌ 未获取到数据（可能被限流，稍后重试）")

        # 测试A股
        print("\n📈 测试A股: 600519.SH (贵州茅台)")
        bars = feed.fetch_daily_data(
            '600519.SH',
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )

        if bars:
            print(f"✅ 获取到 {len(bars)} 条数据")
            print(f"   最新: 日期={bars[-1].datetime}, 收盘价=¥{bars[-1].close:.2f}")
        else:
            print("❌ 未获取到数据")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_tushare(token):
    """测试TuShare数据源"""
    print("\n" + "=" * 60)
    print("测试 TuShare 数据源")
    print("=" * 60)

    try:
        feed = DataFeed('tushare', token)

        # 测试个股
        print("\n📈 测试个股: 000001.SZ (平安银行)")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        bars = feed.fetch_daily_data(
            '000001.SZ',
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )

        if bars:
            print(f"✅ 获取到 {len(bars)} 条数据")
            print(f"   最新: 日期={bars[-1].datetime}, 收盘价=¥{bars[-1].close:.2f}")
        else:
            print("❌ 未获取到数据")

        # 测试指数
        print("\n📈 测试指数: 000001.SH (上证指数)")
        bars = feed.fetch_daily_data(
            '000001.SH',
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )

        if bars:
            print(f"✅ 获取到 {len(bars)} 条数据")
            print(f"   最新: 日期={bars[-1].datetime}, 收盘价={bars[-1].close:.2f}")
        else:
            print("❌ 未获取到数据")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    print("🔍 数据源测试工具\n")

    # 测试Yahoo Finance（免费）
    test_yahoo_finance()

    # 测试TuShare（需要token）
    print("\n" + "=" * 60)
    tushare_token = input("测试TuShare数据源？输入token（回车跳过）: ").strip()
    if tushare_token:
        test_tushare(tushare_token)
    else:
        print("⏭️  跳过TuShare测试")
        print("💡 获取TuShare token: https://tushare.pro")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
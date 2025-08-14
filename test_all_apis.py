import requests
import json
from datetime import datetime

# 基础URL
BASE_URL = "http://127.0.0.1:5000"

def test_api(api_name, url, method="GET", data=None, expected_status=200, is_file_download=False):
    """测试API端点"""
    print(f"\n=== 测试 {api_name} ===")
    print(f"URL: {url}")
    print(f"方法: {method}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ 不支持的方法: {method}")
            return False
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ 状态码正确")
            
            # 检查是否是文件下载
            content_type = response.headers.get('content-type', '')
            if is_file_download or 'application/vnd.openxmlformats-officedocument' in content_type or 'application/octet-stream' in content_type:
                print("响应类型: 文件下载")
                print(f"文件大小: {len(response.content)} 字节")
                print(f"Content-Type: {content_type}")
                if 'content-disposition' in response.headers:
                    print(f"文件名: {response.headers['content-disposition']}")
            else:
                # 尝试解析JSON响应
                try:
                    if content_type.startswith('application/json'):
                        result = response.json()
                        print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    else:
                        print("响应类型: HTML/其他")
                        print(f"响应长度: {len(response.text)} 字符")
                except:
                    print("响应类型: 非JSON")
            
            return True
        else:
            print(f"❌ 状态码错误，期望 {expected_status}，实际 {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 请确保Flask应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 请求错误: {str(e)}")
        return False

def test_all_apis():
    """测试所有API端点"""
    print("🚀 开始全面API测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"基础URL: {BASE_URL}")
    
    # 测试结果统计
    total_tests = 0
    passed_tests = 0
    
    # 1. 基础页面路由测试
    print("\n" + "="*50)
    print("📄 基础页面路由测试")
    print("="*50)
    
    routes = [
        ("首页", "/"),
        ("客户管理", "/customers"),
        ("房间管理", "/rooms"),
        ("合同管理", "/contracts"),
        ("收款管理", "/payments"),
        ("租金计划", "/rent_plans"),
        ("统计分析", "/statistics"),
        ("数据导入", "/import"),
    ]
    
    for name, route in routes:
        total_tests += 1
        if test_api(name, f"{BASE_URL}{route}"):
            passed_tests += 1
    
    # 2. API端点测试
    print("\n" + "="*50)
    print("🔌 API端点测试")
    print("="*50)
    
    # 统计API
    total_tests += 1
    if test_api("统计数据", f"{BASE_URL}/api/stats"):
        passed_tests += 1
    
    total_tests += 1
    if test_api("活动记录", f"{BASE_URL}/api/activities"):
        passed_tests += 1
    
    # 客户API
    total_tests += 1
    if test_api("客户列表API", f"{BASE_URL}/api/customers"):
        passed_tests += 1
    
    # 房间API
    total_tests += 1
    if test_api("房间列表API", f"{BASE_URL}/api/rooms"):
        passed_tests += 1
    
    total_tests += 1
    if test_api("可用房间API", f"{BASE_URL}/api/rooms/available"):
        passed_tests += 1
    
    # 合同API
    total_tests += 1
    if test_api("合同列表API", f"{BASE_URL}/api/contracts"):
        passed_tests += 1
    
    # 租金计划API
    total_tests += 1
    if test_api("租金计划API", f"{BASE_URL}/api/rent_plans"):
        passed_tests += 1
    
    # 统计API
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    total_tests += 1
    if test_api("月度计划统计", f"{BASE_URL}/api/statistics/monthly_plans?year={current_year}&month={current_month}"):
        passed_tests += 1
    
    total_tests += 1
    if test_api("房间计划统计", f"{BASE_URL}/api/statistics/room_plans"):
        passed_tests += 1
    
    # 3. 数据导出测试
    print("\n" + "="*50)
    print("📊 数据导出测试")
    print("="*50)
    
    export_types = [
        ("客户数据导出", "customers"),
        ("房间数据导出", "rooms"),
        ("合同数据导出", "contracts"),
        ("租金计划导出", "rent_plans"),
    ]
    
    for name, export_type in export_types:
        total_tests += 1
        if test_api(name, f"{BASE_URL}/export/{export_type}", is_file_download=True):
            passed_tests += 1
    
    # CSV导出测试
    total_tests += 1
    if test_api("月度计划CSV导出", f"{BASE_URL}/export/csv/monthly_plans?year={current_year}&month={current_month}"):
        passed_tests += 1
    
    total_tests += 1
    if test_api("统计分析CSV导出", f"{BASE_URL}/export/csv/statistics_summary"):
        passed_tests += 1
    
    # 4. 模板下载测试
    print("\n" + "="*50)
    print("📋 模板下载测试")
    print("="*50)
    
    total_tests += 1
    if test_api("Excel导入模板", f"{BASE_URL}/download_template", is_file_download=True):
        passed_tests += 1
    
    # 5. 测试结果统计
    print("\n" + "="*50)
    print("📈 测试结果统计")
    print("="*50)
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {(passed_tests / total_tests * 100):.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有API测试通过！")
    else:
        print("⚠️  部分API测试失败，请检查相关功能")
    
    return passed_tests == total_tests

def test_specific_functionality():
    """测试特定功能"""
    print("\n" + "="*50)
    print("🔍 特定功能测试")
    print("="*50)
    
    # 测试搜索功能
    print("\n--- 搜索功能测试 ---")
    test_api("房间搜索", f"{BASE_URL}/rooms?search=A101")
    test_api("客户搜索", f"{BASE_URL}/customers?search=测试")
    
    # 测试筛选功能
    print("\n--- 筛选功能测试 ---")
    test_api("收款筛选", f"{BASE_URL}/payments?company=测试公司1")
    test_api("收款排序", f"{BASE_URL}/payments?sort=asc")
    
    # 测试分页功能（如果有的话）
    print("\n--- 分页功能测试 ---")
    test_api("分页测试", f"{BASE_URL}/customers?page=1&per_page=10")

if __name__ == "__main__":
    print("开始API测试...")
    print("请确保Flask应用正在运行在 http://127.0.0.1:5000")
    
    # 测试所有API
    success = test_all_apis()
    
    # 测试特定功能
    test_specific_functionality()
    
    print("\n" + "="*50)
    print("🏁 API测试完成")
    print("="*50)

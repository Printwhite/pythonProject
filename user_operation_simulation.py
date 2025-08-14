import requests
import time
import random
from datetime import datetime, date, timedelta
import json

class RentalManagementSimulator:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def simulate_user_journey(self):
        """模拟完整的用户操作流程"""
        print("🚀 开始模拟真实用户操作流程...")
        print("=" * 60)
        
        # 1. 用户登录系统（查看首页）
        self.test_homepage_access()
        
        # 2. 查看客户管理
        self.test_customer_management()
        
        # 3. 添加新客户
        self.test_add_customer()
        
        # 4. 查看房间管理
        self.test_room_management()
        
        # 5. 添加新房间
        self.test_add_room()
        
        # 6. 创建租赁合同
        self.test_create_contract()
        
        # 7. 查看合同管理
        self.test_contract_management()
        
        # 8. 记录收款
        self.test_record_payment()
        
        # 9. 查看收款管理
        self.test_payment_management()
        
        # 10. 查看租金计划
        self.test_rent_plan_management()
        
        # 11. 查看统计分析
        self.test_statistics()
        
        # 12. 数据导出功能
        self.test_export_functions()
        
        # 13. 数据导入功能
        self.test_import_functions()
        
        # 14. 编辑和删除操作
        self.test_edit_delete_operations()
        
        # 15. 搜索和筛选功能
        self.test_search_filter_functions()
        
        print("=" * 60)
        self.print_summary()
        
    def test_homepage_access(self):
        """测试首页访问"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("首页访问", True, "页面加载成功")
            else:
                self.log_test("首页访问", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("首页访问", False, f"连接错误: {str(e)}")
    
    def test_customer_management(self):
        """测试客户管理页面"""
        try:
            response = self.session.get(f"{self.base_url}/customers")
            if response.status_code == 200:
                self.log_test("客户管理页面", True, "页面加载成功")
            else:
                self.log_test("客户管理页面", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("客户管理页面", False, f"连接错误: {str(e)}")
    
    def test_add_customer(self):
        """测试添加客户"""
        try:
            # 获取添加客户页面
            response = self.session.get(f"{self.base_url}/customers/add")
            if response.status_code != 200:
                self.log_test("添加客户页面", False, f"页面加载失败: {response.status_code}")
                return
            
            # 模拟添加客户数据
            customer_data = {
                "customer_id": f"C{random.randint(100, 999)}",
                "company_name": f"测试公司{random.randint(1000, 9999)}",
                "contact_person": f"联系人{random.randint(1, 100)}",
                "contact_phone": f"138{random.randint(10000000, 99999999)}",
                "contact_email": f"test{random.randint(1000, 9999)}@example.com",
                "advance_cost": random.randint(5000, 30000)
            }
            
            # 提交添加客户请求
            response = self.session.post(f"{self.base_url}/customers/add", data=customer_data)
            if response.status_code == 302:  # 重定向到客户列表
                self.log_test("添加客户", True, f"成功添加客户: {customer_data['company_name']}")
            else:
                self.log_test("添加客户", False, f"添加失败: {response.status_code}")
                
        except Exception as e:
            self.log_test("添加客户", False, f"操作错误: {str(e)}")
    
    def test_room_management(self):
        """测试房间管理页面"""
        try:
            response = self.session.get(f"{self.base_url}/rooms")
            if response.status_code == 200:
                self.log_test("房间管理页面", True, "页面加载成功")
            else:
                self.log_test("房间管理页面", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("房间管理页面", False, f"连接错误: {str(e)}")
    
    def test_add_room(self):
        """测试添加房间"""
        try:
            # 获取添加房间页面
            response = self.session.get(f"{self.base_url}/rooms/add")
            if response.status_code != 200:
                self.log_test("添加房间页面", False, f"页面加载失败: {response.status_code}")
                return
            
            # 模拟添加房间数据
            room_data = {
                "room_number": f"TEST{random.randint(100, 999)}",
                "area": random.randint(80, 500),
                "floor": f"{random.randint(1, 10)}层",
                "unit_price": random.randint(40, 80),
                "status": "空置"
            }
            
            # 提交添加房间请求
            response = self.session.post(f"{self.base_url}/rooms/add", data=room_data)
            if response.status_code == 302:  # 重定向到房间列表
                self.log_test("添加房间", True, f"成功添加房间: {room_data['room_number']}")
            else:
                self.log_test("添加房间", False, f"添加失败: {response.status_code}")
                
        except Exception as e:
            self.log_test("添加房间", False, f"操作错误: {str(e)}")
    
    def test_create_contract(self):
        """测试创建合同"""
        try:
            # 获取添加合同页面
            response = self.session.get(f"{self.base_url}/contracts/add")
            if response.status_code != 200:
                self.log_test("添加合同页面", False, f"页面加载失败: {response.status_code}")
                return
            
            # 模拟合同数据
            start_date = date.today()
            end_date = start_date + timedelta(days=365)
            
            contract_data = {
                "contract_number": f"HT{datetime.now().strftime('%Y%m%d')}{random.randint(100, 999)}",
                "customer_id": "1",  # 假设客户ID为1
                "room_id": "1",      # 假设房间ID为1
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "unit_price": random.randint(40, 80),
                "payment_frequency": "按月支付",
                "deposit_contract": random.randint(30000, 100000),
                "deposit_received": random.randint(30000, 100000),
                "payment_day": random.randint(1, 28),
                "payment_method": "银行转账",
                "invoice_method": "电子发票"
            }
            
            # 提交添加合同请求
            response = self.session.post(f"{self.base_url}/contracts/add", data=contract_data)
            if response.status_code == 302:  # 重定向到合同列表
                self.log_test("创建合同", True, f"成功创建合同: {contract_data['contract_number']}")
            else:
                self.log_test("创建合同", False, f"创建失败: {response.status_code}")
                
        except Exception as e:
            self.log_test("创建合同", False, f"操作错误: {str(e)}")
    
    def test_contract_management(self):
        """测试合同管理页面"""
        try:
            response = self.session.get(f"{self.base_url}/contracts")
            if response.status_code == 200:
                self.log_test("合同管理页面", True, "页面加载成功")
            else:
                self.log_test("合同管理页面", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("合同管理页面", False, f"连接错误: {str(e)}")
    
    def test_record_payment(self):
        """测试记录收款"""
        try:
            # 获取添加收款页面
            response = self.session.get(f"{self.base_url}/payments/add")
            if response.status_code != 200:
                self.log_test("添加收款页面", False, f"页面加载失败: {response.status_code}")
                return
            
            # 模拟收款数据
            payment_data = {
                "contract_id": "1",  # 假设合同ID为1
                "rent_plan_id": "1", # 假设租金计划ID为1
                "amount": random.randint(3000, 15000),
                "payment_date": date.today().strftime("%Y-%m-%d"),
                "payment_method": "银行转账",
                "remarks": f"测试收款{random.randint(1000, 9999)}"
            }
            
            # 提交添加收款请求
            response = self.session.post(f"{self.base_url}/payments/add", data=payment_data)
            if response.status_code == 302:  # 重定向到收款列表
                self.log_test("记录收款", True, f"成功记录收款: ¥{payment_data['amount']}")
            else:
                self.log_test("记录收款", False, f"记录失败: {response.status_code}")
                
        except Exception as e:
            self.log_test("记录收款", False, f"操作错误: {str(e)}")
    
    def test_payment_management(self):
        """测试收款管理页面"""
        try:
            response = self.session.get(f"{self.base_url}/payments")
            if response.status_code == 200:
                self.log_test("收款管理页面", True, "页面加载成功")
            else:
                self.log_test("收款管理页面", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("收款管理页面", False, f"连接错误: {str(e)}")
    
    def test_rent_plan_management(self):
        """测试租金计划页面"""
        try:
            response = self.session.get(f"{self.base_url}/rent_plans")
            if response.status_code == 200:
                self.log_test("租金计划页面", True, "页面加载成功")
            else:
                self.log_test("租金计划页面", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("租金计划页面", False, f"连接错误: {str(e)}")
    
    def test_statistics(self):
        """测试统计分析页面"""
        try:
            response = self.session.get(f"{self.base_url}/statistics")
            if response.status_code == 200:
                self.log_test("统计分析页面", True, "页面加载成功")
            else:
                self.log_test("统计分析页面", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("统计分析页面", False, f"连接错误: {str(e)}")
    
    def test_export_functions(self):
        """测试数据导出功能"""
        export_types = ["customers", "rooms", "contracts", "rent_plans"]
        
        for export_type in export_types:
            try:
                response = self.session.get(f"{self.base_url}/export/{export_type}")
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/vnd.openxmlformats-officedocument' in content_type:
                        self.log_test(f"导出{export_type}", True, "Excel文件生成成功")
                    else:
                        self.log_test(f"导出{export_type}", False, "文件格式错误")
                else:
                    self.log_test(f"导出{export_type}", False, f"导出失败: {response.status_code}")
            except Exception as e:
                self.log_test(f"导出{export_type}", False, f"导出错误: {str(e)}")
    
    def test_import_functions(self):
        """测试数据导入功能"""
        try:
            # 测试导入页面
            response = self.session.get(f"{self.base_url}/import")
            if response.status_code == 200:
                self.log_test("数据导入页面", True, "页面加载成功")
            else:
                self.log_test("数据导入页面", False, f"页面加载失败: {response.status_code}")
                
            # 测试模板下载
            response = self.session.get(f"{self.base_url}/download_template")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/vnd.openxmlformats-officedocument' in content_type:
                    self.log_test("模板下载", True, "Excel模板下载成功")
                else:
                    self.log_test("模板下载", False, "模板格式错误")
            else:
                self.log_test("模板下载", False, f"下载失败: {response.status_code}")
                
        except Exception as e:
            self.log_test("数据导入功能", False, f"导入功能错误: {str(e)}")
    
    def test_edit_delete_operations(self):
        """测试编辑和删除操作"""
        try:
            # 测试编辑客户页面（假设客户ID为1）
            response = self.session.get(f"{self.base_url}/customers/1/edit")
            if response.status_code == 200:
                self.log_test("编辑客户页面", True, "页面加载成功")
            else:
                self.log_test("编辑客户页面", False, f"页面加载失败: {response.status_code}")
                
            # 测试编辑房间页面（假设房间ID为1）
            response = self.session.get(f"{self.base_url}/rooms/1/edit")
            if response.status_code == 200:
                self.log_test("编辑房间页面", True, "页面加载成功")
            else:
                self.log_test("编辑房间页面", False, f"页面加载失败: {response.status_code}")
                
            # 测试编辑合同页面（假设合同ID为1）
            response = self.session.get(f"{self.base_url}/contracts/1/edit")
            if response.status_code == 200:
                self.log_test("编辑合同页面", True, "页面加载成功")
            else:
                self.log_test("编辑合同页面", False, f"页面加载失败: {response.status_code}")
                
        except Exception as e:
            self.log_test("编辑操作", False, f"编辑功能错误: {str(e)}")
    
    def test_search_filter_functions(self):
        """测试搜索和筛选功能"""
        try:
            # 测试API端点
            api_endpoints = [
                "/api/stats",
                "/api/activities",
                "/api/customers",
                "/api/rooms",
                "/api/contracts",
                "/api/payments",
                "/api/rent_plans"
            ]
            
            for endpoint in api_endpoints:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_test(f"API{endpoint}", True, f"返回{len(data) if isinstance(data, list) else 'JSON'}数据")
                    except:
                        self.log_test(f"API{endpoint}", True, "返回数据")
                else:
                    self.log_test(f"API{endpoint}", False, f"请求失败: {response.status_code}")
                    
        except Exception as e:
            self.log_test("搜索筛选功能", False, f"API功能错误: {str(e)}")
    
    def print_summary(self):
        """打印测试总结"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print("\n📊 用户操作模拟测试总结")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"通过率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        print("\n🎯 测试场景覆盖:")
        scenarios = [
            "页面访问测试",
            "数据添加操作",
            "数据编辑操作", 
            "数据导出功能",
            "数据导入功能",
            "API接口测试",
            "搜索筛选功能"
        ]
        
        for scenario in scenarios:
            scenario_tests = [r for r in self.test_results if scenario.lower() in r["test_name"].lower()]
            if scenario_tests:
                passed = len([r for r in scenario_tests if r["success"]])
                total = len(scenario_tests)
                status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
                print(f"  {status} {scenario}: {passed}/{total}")

def main():
    print("🏢 租赁管理系统 - 真实用户操作模拟测试")
    print("=" * 60)
    
    # 检查Flask应用是否运行
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        if response.status_code != 200:
            print("❌ Flask应用未正常运行，请先启动应用")
            return
    except:
        print("❌ 无法连接到Flask应用，请确保应用在 http://127.0.0.1:5000 运行")
        return
    
    # 创建模拟器并运行测试
    simulator = RentalManagementSimulator()
    simulator.simulate_user_journey()

if __name__ == "__main__":
    main()

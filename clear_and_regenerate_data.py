#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, Customer, Room, Contract, RentPlan, generate_rent_plans
from datetime import datetime, timedelta
import random

def clear_all_data():
    """清空所有数据"""
    with app.app_context():
        try:
            print("🗑️ 开始清空所有数据...")
            
            # 删除所有租金计划
            RentPlan.query.delete()
            print("✅ 已清空租金计划数据")
            
            # 删除所有合同
            Contract.query.delete()
            print("✅ 已清空合同数据")
            
            # 删除所有房间
            Room.query.delete()
            print("✅ 已清空房间数据")
            
            # 删除所有客户
            Customer.query.delete()
            print("✅ 已清空客户数据")
            
            # 提交更改
            db.session.commit()
            print("✅ 所有数据清空完成！")
            
        except Exception as e:
            print(f"❌ 清空数据失败: {str(e)}")
            db.session.rollback()
            raise

def generate_test_data():
    """生成新的测试数据"""
    with app.app_context():
        try:
            print("🔄 开始生成新的测试数据...")
            
            # 生成客户数据
            customers_data = [
                {"customer_id": "C001", "company_name": "北京科技有限公司", "contact_person": "张三", "contact_phone": "13800138001", "contact_email": "zhangsan@tech.com"},
                {"customer_id": "C002", "company_name": "上海贸易有限公司", "contact_person": "李四", "contact_phone": "13800138002", "contact_email": "lisi@trade.com"},
                {"customer_id": "C003", "company_name": "广州制造有限公司", "contact_person": "王五", "contact_phone": "13800138003", "contact_email": "wangwu@manufacture.com"},
                {"customer_id": "C004", "company_name": "深圳互联网公司", "contact_person": "赵六", "contact_phone": "13800138004", "contact_email": "zhaoliu@internet.com"},
                {"customer_id": "C005", "company_name": "杭州软件公司", "contact_person": "钱七", "contact_phone": "13800138005", "contact_email": "qianqi@software.com"},
                {"customer_id": "C006", "company_name": "成都餐饮连锁", "contact_person": "孙八", "contact_phone": "13800138006", "contact_email": "sunba@restaurant.com"},
                {"customer_id": "C007", "company_name": "武汉教育机构", "contact_person": "周九", "contact_phone": "13800138007", "contact_email": "zhoujiu@education.com"},
                {"customer_id": "C008", "company_name": "南京咨询公司", "contact_person": "吴十", "contact_phone": "13800138008", "contact_email": "wushi@consulting.com"}
            ]
            
            customers = []
            for customer_data in customers_data:
                customer = Customer(**customer_data)
                db.session.add(customer)
                customers.append(customer)
            
            db.session.commit()
            print(f"✅ 已生成 {len(customers)} 个客户")
            
            # 生成房间数据
            floors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            room_numbers = [f"{floor}{room:02d}" for floor in floors for room in range(1, 21)]
            
            rooms = []
            for room_number in room_numbers:
                floor = str(int(room_number[0]))  # 转换为字符串
                area = random.uniform(50, 200)  # 50-200平方米
                unit_price = random.uniform(80, 150)  # 80-150元/平方米/月
                status = random.choice(['空置', '已租'])
                
                room = Room(
                    room_number=room_number,
                    floor=floor,
                    area=round(area, 2),
                    unit_price=round(unit_price, 2),
                    status=status
                )
                db.session.add(room)
                rooms.append(room)
            
            db.session.commit()
            print(f"✅ 已生成 {len(rooms)} 个房间")
            
            # 生成合同数据
            payment_frequencies = ['月付', '季付', '半年付', '年付']
            contract_statuses = ['有效', '已到期', '已终止']
            
            contracts = []
            for i in range(50):  # 生成50个合同
                customer = random.choice(customers)
                room = random.choice(rooms)
                
                # 随机生成租期
                start_date = datetime.now().date() + timedelta(days=random.randint(-365, 365))
                duration_months = random.randint(6, 36)  # 6个月到3年
                end_date = start_date + timedelta(days=duration_months * 30)
                
                payment_frequency = random.choice(payment_frequencies)
                payment_day = random.randint(1, 28)  # 避免月末问题
                status = random.choice(contract_statuses)
                
                # 计算月租金
                # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
                monthly_rent = round(room.area * room.unit_price * 365 / 12, 2)
                yearly_rent = round(monthly_rent * 12, 2)
                contract_amount = round(yearly_rent * (duration_months / 12), 2)
                
                # 计算第一期收款日期
                first_payment_start = start_date
                first_payment_end = start_date + timedelta(days=30)
                
                # 计算总期数
                if payment_frequency == '月付':
                    total_periods = duration_months
                elif payment_frequency == '季付':
                    total_periods = duration_months // 3
                elif payment_frequency == '半年付':
                    total_periods = duration_months // 6
                else:  # 年付
                    total_periods = duration_months // 12
                
                # 计算下次收款日期
                next_payment_date = first_payment_start + timedelta(days=payment_day)
                
                contract = Contract(
                    contract_number=f"HT{datetime.now().year}{i+1:04d}",
                    customer_id=customer.id,
                    room_id=room.id,
                    start_date=start_date,
                    end_date=end_date,
                    unit_price=room.unit_price,
                    monthly_rent=round(monthly_rent, 2),
                    yearly_rent=round(yearly_rent, 2),
                    contract_amount=round(contract_amount, 2),
                    payment_frequency=payment_frequency,
                    received_amount=0.0,
                    deposit_contract=monthly_rent * 2,  # 保证金为2个月租金
                    deposit_received=monthly_rent * 2,
                    payment_day=payment_day,
                    payment_method="银行转账",
                    invoice_method="增值税专用发票",
                    first_payment_start=first_payment_start,
                    first_payment_end=first_payment_end,
                    total_periods=total_periods,
                    next_payment_date=next_payment_date,
                    remarks="自动生成的测试合同",
                    status=status
                )
                db.session.add(contract)
                contracts.append(contract)
                
                # 更新房间状态
                if status == '有效':
                    room.status = '已租'
            
            db.session.commit()
            print(f"✅ 已生成 {len(contracts)} 个合同")
            
            # 为有效合同生成租金计划
            active_contracts = [c for c in contracts if c.status == '有效']
            print(f"📋 为 {len(active_contracts)} 个有效合同生成租金计划...")
            
            for contract in active_contracts:
                generate_rent_plans(contract)
                print(f"   - 合同 {contract.contract_number}: 生成了 {len(contract.rent_plans)} 个租金计划")
            
            db.session.commit()
            print("✅ 租金计划生成完成！")
            
            # 统计信息
            print("\n📊 数据生成统计:")
            print(f"   - 客户: {len(customers)} 个")
            print(f"   - 房间: {len(rooms)} 个")
            print(f"   - 合同: {len(contracts)} 个")
            print(f"   - 有效合同: {len(active_contracts)} 个")
            print(f"   - 租金计划: {RentPlan.query.count()} 个")
            
        except Exception as e:
            print(f"❌ 生成数据失败: {str(e)}")
            db.session.rollback()
            raise

def main():
    """主函数：清空数据并重新生成"""
    try:
        print("🚀 开始清空数据并重新生成...")
        
        # 清空所有数据
        clear_all_data()
        
        # 生成新的测试数据
        generate_test_data()
        
        print("\n🎉 数据重新生成完成！")
        print("💡 您现在可以访问 http://127.0.0.1:5000 查看新的数据")
        
    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")

if __name__ == "__main__":
    main()

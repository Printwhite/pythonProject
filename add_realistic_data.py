from app import app, db, Customer, Room, Contract, RentPlan, Payment, Invoice
from datetime import datetime, date, timedelta
import calendar
import random

def add_realistic_data():
    print("🔄 清空现有数据...")
    Invoice.query.delete()
    Payment.query.delete()
    RentPlan.query.delete()
    Contract.query.delete()
    Customer.query.delete()
    Room.query.delete()
    db.session.commit()
    
    print("📊 添加真实业务数据...")
    
    # 添加房间 - 模拟真实办公楼
    rooms = [
        # A栋 - 小户型办公室
        Room(room_number="A101", area=80, floor="1层", unit_price=45.0, status="已出租"),
        Room(room_number="A102", area=100, floor="1层", unit_price=48.0, status="已出租"),
        Room(room_number="A103", area=120, floor="1层", unit_price=50.0, status="已出租"),
        Room(room_number="A201", area=80, floor="2层", unit_price=46.0, status="已出租"),
        Room(room_number="A202", area=100, floor="2层", unit_price=49.0, status="已出租"),
        Room(room_number="A203", area=120, floor="2层", unit_price=51.0, status="空置"),
        Room(room_number="A301", area=80, floor="3层", unit_price=47.0, status="已出租"),
        Room(room_number="A302", area=100, floor="3层", unit_price=50.0, status="已出租"),
        Room(room_number="A303", area=120, floor="3层", unit_price=52.0, status="空置"),
        
        # B栋 - 中型办公室
        Room(room_number="B101", area=150, floor="1层", unit_price=55.0, status="已出租"),
        Room(room_number="B102", area=180, floor="1层", unit_price=58.0, status="已出租"),
        Room(room_number="B103", area=200, floor="1层", unit_price=60.0, status="已出租"),
        Room(room_number="B201", area=150, floor="2层", unit_price=56.0, status="已出租"),
        Room(room_number="B202", area=180, floor="2层", unit_price=59.0, status="已出租"),
        Room(room_number="B203", area=200, floor="2层", unit_price=61.0, status="空置"),
        
        # C栋 - 大型办公室
        Room(room_number="C101", area=300, floor="1层", unit_price=65.0, status="已出租"),
        Room(room_number="C102", area=400, floor="1层", unit_price=68.0, status="已出租"),
        Room(room_number="C201", area=300, floor="2层", unit_price=66.0, status="已出租"),
        Room(room_number="C202", area=400, floor="2层", unit_price=69.0, status="空置"),
    ]
    
    for room in rooms:
        db.session.add(room)
    db.session.commit()
    print(f"✅ 添加了 {len(rooms)} 个房间")
    
    # 添加客户 - 模拟真实公司
    customers = [
        # 科技公司
        Customer(customer_id="C001", company_name="北京智联科技有限公司", contact_person="张明", contact_phone="13800138001", contact_email="zhang.ming@zhilian.com", advance_cost=15000.0),
        Customer(customer_id="C002", company_name="上海云创软件有限公司", contact_person="李华", contact_phone="13800138002", contact_email="li.hua@yunsoft.com", advance_cost=20000.0),
        Customer(customer_id="C003", company_name="深圳数字科技有限公司", contact_person="王芳", contact_phone="13800138003", contact_email="wang.fang@digital.com", advance_cost=18000.0),
        
        # 贸易公司
        Customer(customer_id="C004", company_name="广州国际贸易有限公司", contact_person="陈强", contact_phone="13800138004", contact_email="chen.qiang@trade.com", advance_cost=12000.0),
        Customer(customer_id="C005", company_name="杭州电商贸易有限公司", contact_person="刘伟", contact_phone="13800138005", contact_email="liu.wei@ecommerce.com", advance_cost=16000.0),
        
        # 咨询公司
        Customer(customer_id="C006", company_name="成都管理咨询有限公司", contact_person="赵敏", contact_phone="13800138006", contact_email="zhao.min@consulting.com", advance_cost=10000.0),
        Customer(customer_id="C007", company_name="武汉财务咨询有限公司", contact_person="孙丽", contact_phone="13800138007", contact_email="sun.li@finance.com", advance_cost=8000.0),
        
        # 制造公司
        Customer(customer_id="C008", company_name="苏州精密制造有限公司", contact_person="周杰", contact_phone="13800138008", contact_email="zhou.jie@precision.com", advance_cost=25000.0),
        Customer(customer_id="C009", company_name="东莞电子制造有限公司", contact_person="吴婷", contact_phone="13800138009", contact_email="wu.ting@electronics.com", advance_cost=22000.0),
        
        # 服务公司
        Customer(customer_id="C010", company_name="南京物流服务有限公司", contact_person="郑波", contact_phone="13800138010", contact_email="zheng.bo@logistics.com", advance_cost=9000.0),
    ]
    
    for customer in customers:
        db.session.add(customer)
    db.session.commit()
    print(f"✅ 添加了 {len(customers)} 个客户")
    
    # 添加合同 - 模拟真实租赁合同
    contracts = []
    
    # 合同配置
    contract_configs = [
        # (合同编号, 客户ID, 房间ID, 开始日期, 结束日期, 单价, 付款频率, 保证金, 付款日)
        ("HT2024001", 1, 1, date(2024, 1, 1), date(2026, 12, 31), 45.0, "按月支付", 50000.0, 5),
        ("HT2024002", 2, 4, date(2024, 2, 1), date(2026, 1, 31), 46.0, "按月支付", 60000.0, 10),
        ("HT2024003", 3, 7, date(2024, 3, 1), date(2026, 2, 28), 47.0, "按月支付", 70000.0, 15),
        ("HT2024004", 4, 10, date(2024, 4, 1), date(2025, 3, 31), 55.0, "按季度支付", 80000.0, 20),
        ("HT2024005", 5, 11, date(2024, 5, 1), date(2025, 4, 30), 58.0, "按月支付", 90000.0, 25),
        ("HT2024006", 6, 14, date(2024, 6, 1), date(2025, 5, 31), 56.0, "按月支付", 85000.0, 30),
        ("HT2024007", 7, 16, date(2024, 7, 1), date(2025, 6, 30), 65.0, "按季度支付", 120000.0, 5),
        ("HT2024008", 8, 17, date(2024, 8, 1), date(2025, 7, 31), 68.0, "按月支付", 150000.0, 10),
        ("HT2024009", 9, 19, date(2024, 9, 1), date(2025, 8, 31), 66.0, "按月支付", 130000.0, 15),
        ("HT2024010", 10, 2, date(2024, 10, 1), date(2025, 3, 31), 48.0, "按月支付", 40000.0, 20),
        ("HT2024011", 1, 5, date(2024, 11, 1), date(2025, 10, 31), 49.0, "按月支付", 55000.0, 25),
        ("HT2024012", 2, 8, date(2024, 12, 1), date(2025, 11, 30), 50.0, "按月支付", 60000.0, 30),
    ]
    
    for config in contract_configs:
        contract_number, customer_id, room_id, start_date, end_date, unit_price, payment_frequency, deposit_contract, payment_day = config
        
        # 获取房间信息计算租金
        room = Room.query.get(room_id)
        # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
        monthly_rent = round(unit_price * room.area * 365 / 12, 2)
        yearly_rent = round(monthly_rent * 12, 2)
        
        # 计算合同总金额（按合同期限）
        months_diff = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
        if end_date.day > start_date.day:
            months_diff += 1
        contract_amount = monthly_rent * months_diff
        
        # 计算第一期收款日期
        first_payment_start = start_date
        if payment_frequency == "按月支付":
            first_payment_end = start_date.replace(day=min(start_date.day + 30, 28))
        elif payment_frequency == "按季度支付":
            first_payment_end = start_date.replace(month=min(start_date.month + 3, 12))
        else:
            first_payment_end = start_date.replace(month=min(start_date.month + 1, 12))
        
        # 计算总期数
        if payment_frequency == "按月支付":
            total_periods = months_diff
        elif payment_frequency == "按季度支付":
            total_periods = max(1, months_diff // 3)
        else:
            total_periods = max(1, months_diff // 12)
        
        # 计算下次收款日期
        next_payment_date = start_date.replace(day=payment_day)
        if next_payment_date < start_date:
            if start_date.month == 12:
                next_payment_date = start_date.replace(year=start_date.year + 1, month=1, day=payment_day)
            else:
                next_payment_date = start_date.replace(month=start_date.month + 1, day=payment_day)
        
        contract = Contract(
            contract_number=contract_number,
            customer_id=customer_id,
            room_id=room_id,
            start_date=start_date,
            end_date=end_date,
            unit_price=unit_price,
            monthly_rent=monthly_rent,
            yearly_rent=yearly_rent,
            contract_amount=contract_amount,
            payment_frequency=payment_frequency,
            deposit_contract=deposit_contract,
            deposit_received=deposit_contract,
            payment_day=payment_day,
            payment_method="银行转账",
            invoice_method="电子发票",
            first_payment_start=first_payment_start,
            first_payment_end=first_payment_end,
            total_periods=total_periods,
            next_payment_date=next_payment_date
        )
        contracts.append(contract)
    
    for contract in contracts:
        db.session.add(contract)
    db.session.commit()
    print(f"✅ 添加了 {len(contracts)} 个合同")
    
    # 获取当前年月
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    # 添加租金计划 - 模拟真实的租金收取情况
    rent_plans = []
    
    for contract in contracts:
        room = Room.query.get(contract.room_id)
        # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
        monthly_rent = round(contract.unit_price * room.area * 365 / 12, 2)
        
        # 计算合同开始月份到当前月份的所有租金计划
        start_year = contract.start_date.year
        start_month = contract.start_date.month
        end_year = contract.end_date.year
        end_month = contract.end_date.month
        
        # 生成从合同开始到当前月份的所有租金计划
        current_plan_year = start_year
        current_plan_month = start_month
        
        while (current_plan_year < current_year) or (current_plan_year == current_year and current_plan_month <= current_month):
            # 跳过合同开始日期之前的月份
            if current_plan_year == start_year and current_plan_month < start_month:
                current_plan_month += 1
                if current_plan_month > 12:
                    current_plan_month = 1
                    current_plan_year += 1
                continue
            
            # 跳过合同结束日期之后的月份
            if current_plan_year == end_year and current_plan_month > end_month:
                break
            
            # 计算实际天数（考虑合同开始和结束日期）
            if current_plan_year == start_year and current_plan_month == start_month:
                start_day = contract.start_date.day
            else:
                start_day = 1
                
            if current_plan_year == end_year and current_plan_month == end_month:
                end_day = contract.end_date.day
            else:
                end_day = calendar.monthrange(current_plan_year, current_plan_month)[1]
            
            # 计算实际租金（按天数比例）
            total_days = calendar.monthrange(current_plan_year, current_plan_month)[1]
            actual_days = end_day - start_day + 1
            actual_rent = round((monthly_rent / total_days) * actual_days, 2)
            
            # 确定租金状态
            if current_plan_year < current_year or (current_plan_year == current_year and current_plan_month < current_month):
                # 历史月份 - 已收款
                status = "已收"
                received_amount = actual_rent
            elif current_plan_year == current_year and current_plan_month == current_month:
                # 当前月份 - 根据合同ID模拟不同状态
                if contract.id % 3 == 0:
                    status = "已收"
                    received_amount = actual_rent
                elif contract.id % 3 == 1:
                    status = "部分收款"
                    received_amount = actual_rent * 0.7
                else:
                    status = "未收"
                    received_amount = 0
            else:
                # 未来月份 - 未收款
                status = "未收"
                received_amount = 0
            
            # 确保付款日期在有效范围内
            max_days = calendar.monthrange(current_plan_year, current_plan_month)[1]
            payment_day = min(contract.payment_day, max_days)
            
            rent_plan = RentPlan(
                contract_id=contract.id,
                year=current_plan_year,
                month=current_plan_month,
                start_day=start_day,
                end_day=end_day,
                amount=actual_rent,
                due_date=date(current_plan_year, current_plan_month, payment_day),
                status=status,
                received_amount=received_amount,
                days=actual_days
            )
            db.session.add(rent_plan)
            rent_plans.append(rent_plan)
            
            # 移动到下个月
            current_plan_month += 1
            if current_plan_month > 12:
                current_plan_month = 1
                current_plan_year += 1
    
    db.session.commit()
    print(f"✅ 添加了 {len(rent_plans)} 个租金计划")
    
    # 添加收款记录 - 模拟真实的收款情况
    payments = []
    payment_methods = ["银行转账", "现金", "支票", "支付宝", "微信支付"]
    
    for rent_plan in rent_plans:
        if rent_plan.status in ["已收", "部分收款"] and rent_plan.received_amount > 0:
            # 模拟收款日期（在到期日前后几天内）
            days_offset = random.randint(-10, 5)  # 提前10天到延后5天
            payment_date = rent_plan.due_date + timedelta(days=days_offset)
            
            # 如果是一次性收款
            if rent_plan.status == "已收":
                payment = Payment(
                    contract_id=rent_plan.contract_id,
                    rent_plan_id=rent_plan.id,
                    amount=rent_plan.received_amount,
                    payment_date=payment_date,
                    payment_method=random.choice(payment_methods),
                    remarks=f"{rent_plan.year}年{rent_plan.month}月租金"
                )
                db.session.add(payment)
                db.session.flush()
                
                # 生成发票
                invoice = Invoice(
                    contract_id=rent_plan.contract_id,
                    payment_id=payment.id,
                    invoice_number=f"INV{rent_plan.year}{rent_plan.month:02d}{rent_plan.contract_id:03d}",
                    amount=rent_plan.received_amount,
                    invoice_date=payment_date,
                    remarks="增值税普通发票"
                )
                db.session.add(invoice)
                payments.append(payment)
            
            # 如果是部分收款，可能分多次收款
            elif rent_plan.status == "部分收款":
                # 模拟分2-3次收款
                num_payments = random.randint(2, 3)
                remaining_amount = rent_plan.received_amount
                
                for i in range(num_payments):
                    if remaining_amount <= 0:
                        break
                    
                    # 每次收款金额
                    if i == num_payments - 1:
                        payment_amount = remaining_amount
                    else:
                        payment_amount = remaining_amount * random.uniform(0.3, 0.6)
                    
                    payment_date_offset = random.randint(-15, 0)
                    payment_date = rent_plan.due_date + timedelta(days=payment_date_offset + i * 5)
                    
                    payment = Payment(
                        contract_id=rent_plan.contract_id,
                        rent_plan_id=rent_plan.id,
                        amount=payment_amount,
                        payment_date=payment_date,
                        payment_method=random.choice(payment_methods),
                        remarks=f"{rent_plan.year}年{rent_plan.month}月租金（第{i+1}次）"
                    )
                    db.session.add(payment)
                    db.session.flush()
                    
                    # 生成发票
                    invoice = Invoice(
                        contract_id=rent_plan.contract_id,
                        payment_id=payment.id,
                        invoice_number=f"INV{rent_plan.year}{rent_plan.month:02d}{rent_plan.contract_id:03d}-{i+1}",
                        amount=payment_amount,
                        invoice_date=payment_date,
                        remarks="增值税普通发票"
                    )
                    db.session.add(invoice)
                    payments.append(payment)
                    
                    remaining_amount -= payment_amount
    
    db.session.commit()
    print(f"✅ 添加了 {len(payments)} 个收款记录")
    
    # 更新房间状态
    for contract in contracts:
        room = Room.query.get(contract.room_id)
        if room:
            room.status = "已出租"
    
    db.session.commit()
    
    print("\n🎉 真实业务数据添加完成！")
    print(f"📅 当前时间: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 数据统计:")
    print(f"   - 房间总数: {len(rooms)} 个")
    print(f"   - 客户总数: {len(customers)} 个")
    print(f"   - 合同总数: {len(contracts)} 个")
    print(f"   - 租金计划: {len(rent_plans)} 个")
    print(f"   - 收款记录: {len(payments)} 个")
    
    # 显示一些业务统计
    total_monthly_rent = sum(plan.amount for plan in rent_plans if plan.year == current_year and plan.month == current_month)
    total_received = sum(plan.received_amount for plan in rent_plans if plan.year == current_year and plan.month == current_month)
    occupancy_rate = len([r for r in rooms if r.status == "已出租"]) / len(rooms) * 100
    
    print(f"\n📈 业务概览:")
    print(f"   - 本月应收租金: ¥{total_monthly_rent:,.2f}")
    print(f"   - 本月已收租金: ¥{total_received:,.2f}")
    print(f"   - 房间出租率: {occupancy_rate:.1f}%")

if __name__ == '__main__':
    with app.app_context():
        add_realistic_data()

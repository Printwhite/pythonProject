from app import app, db, Customer, Room, Contract, RentPlan, Payment, Invoice
from datetime import datetime, date, timedelta
import calendar

def add_test_data_v2():
    print("清空现有数据...")
    Invoice.query.delete()
    Payment.query.delete()
    RentPlan.query.delete()
    Contract.query.delete()
    Customer.query.delete()
    Room.query.delete()
    db.session.commit()
    
    print("添加测试数据...")
    
    # 添加房间
    rooms = [
        Room(room_number="A101", area=100, floor="1层", unit_price=50.0, status="已出租"),
        Room(room_number="A102", area=120, floor="1层", unit_price=55.0, status="已出租"),
        Room(room_number="A201", area=150, floor="2层", unit_price=60.0, status="已出租"),
        Room(room_number="A202", area=180, floor="2层", unit_price=65.0, status="空置"),
        Room(room_number="B101", area=200, floor="1层", unit_price=70.0, status="已出租"),
    ]
    
    for room in rooms:
        db.session.add(room)
    db.session.commit()
    print(f"添加了 {len(rooms)} 个房间")
    
    # 添加客户
    customers = [
        Customer(customer_id="C001", company_name="测试公司1", contact_person="张三", contact_phone="13800138001", contact_email="test1@example.com", advance_cost=5000.0),
        Customer(customer_id="C002", company_name="测试公司2", contact_person="李四", contact_phone="13800138002", contact_email="test2@example.com", advance_cost=8000.0),
        Customer(customer_id="C003", company_name="测试公司3", contact_person="王五", contact_phone="13800138003", contact_email="test3@example.com", advance_cost=6000.0),
    ]
    
    for customer in customers:
        db.session.add(customer)
    db.session.commit()
    print(f"添加了 {len(customers)} 个客户")
    
    # 添加合同
    contracts = [
        Contract(contract_number="CT001", customer_id=1, room_id=1, start_date=date(2024, 1, 1), end_date=date(2025, 12, 31), unit_price=50.0, payment_frequency="按月支付", deposit_contract=50000.0, deposit_received=50000.0, payment_day=5, payment_method="银行转账", invoice_method="电子发票"),
        Contract(contract_number="CT002", customer_id=2, room_id=2, start_date=date(2024, 2, 1), end_date=date(2025, 1, 31), unit_price=55.0, payment_frequency="按季度支付", deposit_contract=60000.0, deposit_received=60000.0, payment_day=10, payment_method="银行转账", invoice_method="电子发票"),
        Contract(contract_number="CT003", customer_id=3, room_id=3, start_date=date(2024, 3, 1), end_date=date(2025, 2, 28), unit_price=60.0, payment_frequency="按月支付", deposit_contract=70000.0, deposit_received=70000.0, payment_day=15, payment_method="银行转账", invoice_method="电子发票"),
        Contract(contract_number="CT004", customer_id=1, room_id=5, start_date=date(2024, 4, 1), end_date=date(2025, 3, 31), unit_price=70.0, payment_frequency="按月支付", deposit_contract=80000.0, deposit_received=80000.0, payment_day=20, payment_method="银行转账", invoice_method="电子发票"),
    ]
    
    for contract in contracts:
        db.session.add(contract)
    db.session.commit()
    print(f"添加了 {len(contracts)} 个合同")
    
    # 获取当前年月
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    # 添加上月和本月的租金计划
    rent_plans = []
    for contract in contracts:
        room = Room.query.get(contract.room_id)
        # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
        monthly_rent = round(contract.unit_price * room.area * 365 / 12, 2)
        
        # 添加上月数据
        last_month = current_month - 1 if current_month > 1 else 12
        last_year = current_year if current_month > 1 else current_year - 1
        
        # 上月租金计划 - 已收款
        last_month_plan = RentPlan(
            contract_id=contract.id,
            year=last_year,
            month=last_month,
            start_day=1,
            end_day=calendar.monthrange(last_year, last_month)[1],
            amount=monthly_rent,
            due_date=date(last_year, last_month, contract.payment_day),
            status="已收",
            received_amount=monthly_rent,
            days=calendar.monthrange(last_year, last_month)[1]
        )
        db.session.add(last_month_plan)
        rent_plans.append(last_month_plan)
        
        # 本月租金计划 - 部分已收款
        current_month_plan = RentPlan(
            contract_id=contract.id,
            year=current_year,
            month=current_month,
            start_day=1,
            end_day=calendar.monthrange(current_year, current_month)[1],
            amount=monthly_rent,
            due_date=date(current_year, current_month, contract.payment_day),
            status="部分收款" if contract.id % 2 == 0 else "未收",
            received_amount=monthly_rent * 0.7 if contract.id % 2 == 0 else 0,
            days=calendar.monthrange(current_year, current_month)[1]
        )
        db.session.add(current_month_plan)
        rent_plans.append(current_month_plan)
        
        # 添加下月租金计划 - 未收款
        next_month = current_month + 1 if current_month < 12 else 1
        next_year = current_year if current_month < 12 else current_year + 1
        
        next_month_plan = RentPlan(
            contract_id=contract.id,
            year=next_year,
            month=next_month,
            start_day=1,
            end_day=calendar.monthrange(next_year, next_month)[1],
            amount=monthly_rent,
            due_date=date(next_year, next_month, contract.payment_day),
            status="未收",
            received_amount=0,
            days=calendar.monthrange(next_year, next_month)[1]
        )
        db.session.add(next_month_plan)
        rent_plans.append(next_month_plan)
    
    db.session.commit()
    print(f"添加了 {len(rent_plans)} 个租金计划")
    
    # 添加收款记录
    payments = []
    for rent_plan in rent_plans:
        if rent_plan.status in ["已收", "部分收款"] and rent_plan.received_amount > 0:
            payment = Payment(
                contract_id=rent_plan.contract_id,
                rent_plan_id=rent_plan.id,
                amount=rent_plan.received_amount,
                payment_date=rent_plan.due_date - timedelta(days=5),
                payment_method="银行转账",
                remarks=f"{rent_plan.year}年{rent_plan.month}月租金"
            )
            db.session.add(payment)
            db.session.flush()  # 获取payment的ID
            
            invoice = Invoice(
                contract_id=rent_plan.contract_id,
                payment_id=payment.id,
                invoice_number=f"INV{rent_plan.year}{rent_plan.month:02d}{rent_plan.contract_id:03d}",
                amount=rent_plan.received_amount,
                invoice_date=payment.payment_date,
                remarks="增值税普通发票"
            )
            db.session.add(invoice)
            payments.append(payment)
    
    db.session.commit()
    print(f"添加了 {len(payments)} 个收款记录")
    
    print("测试数据添加完成！")
    print(f"当前时间: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"上月: {last_year}年{last_month}月")
    print(f"本月: {current_year}年{current_month}月")
    print(f"下月: {next_year}年{next_month}月")

if __name__ == '__main__':
    with app.app_context():
        add_test_data_v2()

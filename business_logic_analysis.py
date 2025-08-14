from app import app, db, Customer, Room, Contract, RentPlan, Payment, Invoice
from datetime import datetime, date, timedelta

def analyze_business_logic():
    with app.app_context():
        print("=== 租赁管理系统业务逻辑分析 ===\n")
        
        # 1. 数据完整性检查
        print("1. 数据完整性检查:")
        customers = Customer.query.all()
        rooms = Room.query.all()
        contracts = Contract.query.all()
        rent_plans = RentPlan.query.all()
        payments = Payment.query.all()
        invoices = Invoice.query.all()
        
        print(f"   - 客户数量: {len(customers)}")
        print(f"   - 房间数量: {len(rooms)}")
        print(f"   - 合同数量: {len(contracts)}")
        print(f"   - 租金计划数量: {len(rent_plans)}")
        print(f"   - 收款记录数量: {len(payments)}")
        print(f"   - 发票数量: {len(invoices)}")
        
        # 2. 房间状态一致性检查
        print("\n2. 房间状态一致性检查:")
        occupied_rooms = [r for r in rooms if r.status == '已出租']
        vacant_rooms = [r for r in rooms if r.status == '空置']
        
        print(f"   - 已出租房间: {len(occupied_rooms)} 个")
        print(f"   - 空置房间: {len(vacant_rooms)} 个")
        
        # 检查每个已出租房间是否有对应合同
        rooms_without_contracts = []
        for room in occupied_rooms:
            room_contracts = Contract.query.filter_by(room_id=room.id).all()
            if not room_contracts:
                rooms_without_contracts.append(room)
        
        if rooms_without_contracts:
            print(f"   ⚠️  发现 {len(rooms_without_contracts)} 个已出租房间没有对应合同:")
            for room in rooms_without_contracts:
                print(f"      - {room.room_number}")
        else:
            print("   ✅ 所有已出租房间都有对应合同")
        
        # 3. 合同状态检查
        print("\n3. 合同状态检查:")
        active_contracts = [c for c in contracts if c.status == '有效']
        inactive_contracts = [c for c in contracts if c.status != '有效']
        
        print(f"   - 有效合同: {len(active_contracts)} 个")
        print(f"   - 无效合同: {len(inactive_contracts)} 个")
        
        # 检查合同日期有效性
        today = date.today()
        expired_contracts = [c for c in active_contracts if c.end_date < today]
        future_contracts = [c for c in active_contracts if c.start_date > today]
        
        if expired_contracts:
            print(f"   ⚠️  发现 {len(expired_contracts)} 个已过期但状态仍为有效的合同")
        if future_contracts:
            print(f"   ℹ️  发现 {len(future_contracts)} 个未来生效的合同")
        
        # 4. 租金计划检查
        print("\n4. 租金计划检查:")
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_plans = [p for p in rent_plans if p.year == current_year and p.month == current_month]
        overdue_plans = [p for p in rent_plans if p.due_date < today and p.status != '已收']
        
        print(f"   - 本月租金计划: {len(current_month_plans)} 个")
        print(f"   - 逾期未收计划: {len(overdue_plans)} 个")
        
        # 检查租金计划金额计算
        total_expected = sum(p.amount for p in current_month_plans)
        total_received = sum(p.received_amount for p in current_month_plans)
        collection_rate = (total_received / total_expected * 100) if total_expected > 0 else 0
        
        print(f"   - 本月应收总额: {total_expected:.2f} 元")
        print(f"   - 本月已收总额: {total_received:.2f} 元")
        print(f"   - 本月收款率: {collection_rate:.1f}%")
        
        # 5. 收款记录检查
        print("\n5. 收款记录检查:")
        total_payment_amount = sum(p.amount for p in payments)
        total_invoice_amount = sum(i.amount for i in invoices)
        
        print(f"   - 收款记录总金额: {total_payment_amount:.2f} 元")
        print(f"   - 发票记录总金额: {total_invoice_amount:.2f} 元")
        
        if abs(total_payment_amount - total_invoice_amount) > 0.01:
            print("   ⚠️  收款金额与发票金额不匹配")
        else:
            print("   ✅ 收款金额与发票金额匹配")
        
        # 6. 业务规则检查
        print("\n6. 业务规则检查:")
        
        # 检查房间重复出租
        duplicate_rentals = []
        for room in rooms:
            active_room_contracts = [c for c in contracts if c.room_id == room.id and c.status == '有效']
            if len(active_room_contracts) > 1:
                duplicate_rentals.append(room)
        
        if duplicate_rentals:
            print(f"   ⚠️  发现 {len(duplicate_rentals)} 个房间有多个有效合同:")
            for room in duplicate_rentals:
                print(f"      - {room.room_number}")
        else:
            print("   ✅ 没有房间重复出租")
        
        # 检查客户合同数量
        customer_contract_counts = {}
        for customer in customers:
            customer_contracts = [c for c in contracts if c.customer_id == customer.id]
            customer_contract_counts[customer.company_name] = len(customer_contracts)
        
        print("   - 客户合同数量分布:")
        for company, count in customer_contract_counts.items():
            print(f"      - {company}: {count} 个合同")
        
        # 7. 数据一致性检查
        print("\n7. 数据一致性检查:")
        
        # 检查租金计划与合同的一致性
        orphan_plans = []
        for plan in rent_plans:
            contract = Contract.query.get(plan.contract_id)
            if not contract:
                orphan_plans.append(plan)
        
        if orphan_plans:
            print(f"   ⚠️  发现 {len(orphan_plans)} 个孤立的租金计划（对应合同不存在）")
        else:
            print("   ✅ 所有租金计划都有对应合同")
        
        # 检查收款记录与租金计划的一致性
        orphan_payments = []
        for payment in payments:
            rent_plan = RentPlan.query.get(payment.rent_plan_id)
            if not rent_plan:
                orphan_payments.append(payment)
        
        if orphan_payments:
            print(f"   ⚠️  发现 {len(orphan_payments)} 个孤立的收款记录（对应租金计划不存在）")
        else:
            print("   ✅ 所有收款记录都有对应租金计划")
        
        # 8. 财务数据检查
        print("\n8. 财务数据检查:")
        
        # 计算总应收和总已收
        total_contract_value = 0
        total_deposit_received = 0
        
        for contract in contracts:
            # 计算合同总价值（简化计算）
            months_diff = (contract.end_date.year - contract.start_date.year) * 12 + (contract.end_date.month - contract.start_date.month)
            if contract.end_date.day > contract.start_date.day:
                months_diff += 1
            
            room = Room.query.get(contract.room_id)
            if room:
                # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
            monthly_rent = round(contract.unit_price * room.area * 365 / 12, 2)
            contract_value = monthly_rent * months_diff
                total_contract_value += contract_value
            
            total_deposit_received += contract.deposit_received
        
        print(f"   - 合同总价值（估算）: {total_contract_value:.2f} 元")
        print(f"   - 保证金实收总额: {total_deposit_received:.2f} 元")
        print(f"   - 租金实收总额: {total_payment_amount:.2f} 元")
        
        # 9. 系统健康度评估
        print("\n9. 系统健康度评估:")
        
        issues = []
        if rooms_without_contracts:
            issues.append("存在已出租但无合同的房间")
        if expired_contracts:
            issues.append("存在过期但状态仍为有效的合同")
        if duplicate_rentals:
            issues.append("存在重复出租的房间")
        if orphan_plans:
            issues.append("存在孤立的租金计划")
        if orphan_payments:
            issues.append("存在孤立的收款记录")
        if abs(total_payment_amount - total_invoice_amount) > 0.01:
            issues.append("收款金额与发票金额不匹配")
        
        if issues:
            print(f"   ⚠️  发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ 系统数据健康，未发现明显问题")
        
        # 10. 建议改进
        print("\n10. 建议改进:")
        suggestions = []
        
        if expired_contracts:
            suggestions.append("建议添加合同到期自动状态更新功能")
        if overdue_plans:
            suggestions.append("建议添加逾期租金自动提醒功能")
        if future_contracts:
            suggestions.append("建议添加合同即将生效的提醒功能")
        
        if suggestions:
            for suggestion in suggestions:
                print(f"   💡 {suggestion}")
        else:
            print("   ✅ 当前系统运行良好，无需紧急改进")

if __name__ == '__main__':
    analyze_business_logic()

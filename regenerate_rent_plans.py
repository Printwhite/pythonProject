#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, Contract, generate_rent_plans

def regenerate_all_rent_plans():
    """重新生成所有合同的租金计划"""
    
    with app.app_context():
        try:
            print("🔄 开始重新生成租金计划...")
            
            # 获取所有有效合同
            contracts = Contract.query.filter_by(status='有效').all()
            print(f"📋 找到 {len(contracts)} 个有效合同")
            
            for i, contract in enumerate(contracts, 1):
                print(f"📝 处理合同 {i}/{len(contracts)}: {contract.contract_number}")
                print(f"   - 客户: {contract.customer.company_name}")
                print(f"   - 房间: {contract.room.room_number}")
                print(f"   - 付款周期: {contract.payment_frequency}")
                print(f"   - 租期: {contract.start_date} 至 {contract.end_date}")
                
                # 重新生成租金计划
                generate_rent_plans(contract)
                
                # 验证生成的计划
                rent_plans = contract.rent_plans
                print(f"   - 生成了 {len(rent_plans)} 个租金计划")
                
                for plan in rent_plans:
                    print(f"     * {plan.period_start_date} 至 {plan.period_end_date}: ¥{plan.amount:.2f}")
                
                print()
            
            print("✅ 所有租金计划重新生成完成！")
            
        except Exception as e:
            print(f"❌ 重新生成失败: {str(e)}")
            raise

if __name__ == "__main__":
    regenerate_all_rent_plans()

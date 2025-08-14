#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 更新合同模型
添加新的字段：月租金、年租金、合同金额、收款金额、收款安排等
"""

import sqlite3
import os
from datetime import datetime

def update_contract_table():
    """更新合同表结构"""
    db_path = 'instance/rental_management.db'
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在，请先运行应用创建数据库")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 开始更新合同表结构...")
        
        # 检查新字段是否已存在
        cursor.execute("PRAGMA table_info(contract)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 需要添加的新字段
        new_columns = [
            ('monthly_rent', 'REAL NOT NULL DEFAULT 0.0'),
            ('yearly_rent', 'REAL NOT NULL DEFAULT 0.0'),
            ('contract_amount', 'REAL NOT NULL DEFAULT 0.0'),
            ('received_amount', 'REAL NOT NULL DEFAULT 0.0'),
            ('first_payment_start', 'DATE NOT NULL DEFAULT "2024-01-01"'),
            ('first_payment_end', 'DATE NOT NULL DEFAULT "2024-01-31"'),
            ('total_periods', 'INTEGER NOT NULL DEFAULT 1'),
            ('next_payment_date', 'DATE NOT NULL DEFAULT "2024-02-01"')
        ]
        
        # 添加新字段
        for column_name, column_def in new_columns:
            if column_name not in columns:
                print(f"➕ 添加字段: {column_name}")
                cursor.execute(f"ALTER TABLE contract ADD COLUMN {column_name} {column_def}")
            else:
                print(f"✅ 字段已存在: {column_name}")
        
        # 更新现有记录的租金相关字段
        print("🔄 更新现有合同的租金信息...")
        cursor.execute("""
            SELECT c.id, c.unit_price, r.area, c.start_date, c.end_date 
            FROM contract c 
            LEFT JOIN room r ON c.room_id = r.id
        """)
        
        contracts = cursor.fetchall()
        updated_count = 0
        
        for contract in contracts:
            contract_id, unit_price, area, start_date, end_date = contract
            
            if unit_price and area:
                # 计算月租金和年租金
                # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
                monthly_rent = round(unit_price * area * 365 / 12, 2)
                yearly_rent = round(monthly_rent * 12, 2)
                
                # 计算合同金额
                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    months_diff = (end.year - start.year) * 12 + (end.month - start.month)
                    contract_amount = monthly_rent * max(1, months_diff)
                else:
                    contract_amount = monthly_rent
                
                # 更新数据库
                cursor.execute("""
                    UPDATE contract 
                    SET monthly_rent = ?, yearly_rent = ?, contract_amount = ?,
                        first_payment_start = ?, first_payment_end = ?,
                        total_periods = 1, next_payment_date = ?
                    WHERE id = ?
                """, (
                    monthly_rent, yearly_rent, contract_amount,
                    start_date, end_date, end_date, contract_id
                ))
                updated_count += 1
        
        print(f"✅ 更新了 {updated_count} 个合同的租金信息")
        
        # 提交更改
        conn.commit()
        print("✅ 数据库更新完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {str(e)}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 合同模型更新脚本")
    print("=" * 50)
    
    success = update_contract_table()
    
    if success:
        print("\n🎉 更新成功！现在可以重新启动应用了。")
    else:
        print("\n💥 更新失败，请检查错误信息。")

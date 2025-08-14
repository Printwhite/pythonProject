#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime, timedelta
import calendar

def update_rent_plans_table():
    """更新租金计划表，添加期间开始和结束日期字段"""
    
    # 连接到数据库
    conn = sqlite3.connect('instance/rental_management.db')
    cursor = conn.cursor()
    
    try:
        # 检查是否已经存在新字段
        cursor.execute("PRAGMA table_info(rent_plan)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'period_start_date' not in columns:
            # 添加新字段
            cursor.execute("ALTER TABLE rent_plan ADD COLUMN period_start_date DATE")
            cursor.execute("ALTER TABLE rent_plan ADD COLUMN period_end_date DATE")
            print("✅ 已添加新字段 period_start_date 和 period_end_date")
        else:
            print("ℹ️ 字段已存在，跳过添加")
        
        # 更新现有记录的期间日期
        cursor.execute("SELECT id, year, month, start_day, end_day FROM rent_plan")
        rent_plans = cursor.fetchall()
        
        updated_count = 0
        for plan_id, year, month, start_day, end_day in rent_plans:
            # 计算期间开始日期
            if start_day <= end_day:
                # 同月内
                period_start = datetime(year, month, start_day).date()
                period_end = datetime(year, month, end_day).date()
            else:
                # 跨月
                period_start = datetime(year, month, start_day).date()
                if month == 12:
                    period_end = datetime(year + 1, 1, end_day).date()
                else:
                    period_end = datetime(year, month + 1, end_day).date()
            
            # 更新记录
            cursor.execute("""
                UPDATE rent_plan 
                SET period_start_date = ?, period_end_date = ? 
                WHERE id = ?
            """, (period_start, period_end, plan_id))
            
            updated_count += 1
        
        conn.commit()
        print(f"✅ 已更新 {updated_count} 条租金计划记录的期间日期")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("开始更新租金计划表...")
    update_rent_plans_table()
    print("更新完成！")

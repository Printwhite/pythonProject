from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import os
import json
from werkzeug.utils import secure_filename
import calendar
from io import BytesIO
import zipfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.url_map.strict_slashes = False

db = SQLAlchemy(app)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 数据库模型
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(100))
    advance_cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), unique=True, nullable=False)
    area = db.Column(db.Float, nullable=False)  # 面积
    floor = db.Column(db.String(20), nullable=False)  # 楼层
    unit_price = db.Column(db.Float, nullable=False)  # 单价
    status = db.Column(db.String(20), default='空置')  # 状态：空置/已出租
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(100), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # 租金单价（元/㎡/月）
    monthly_rent = db.Column(db.Float, nullable=False)  # 月租金
    yearly_rent = db.Column(db.Float, nullable=False)  # 年租金
    contract_amount = db.Column(db.Float, nullable=False)  # 合同金额
    payment_frequency = db.Column(db.String(20), nullable=False)  # 付款周期（月、季度、年付、半年付、其他）
    received_amount = db.Column(db.Float, default=0.0)  # 收款金额
    deposit_contract = db.Column(db.Float, nullable=False)  # 合同约定保证金
    deposit_received = db.Column(db.Float, nullable=False)  # 实收保证金
    payment_day = db.Column(db.Integer, nullable=False)  # 付款日
    payment_method = db.Column(db.String(50), nullable=False)  # 收租方式
    invoice_method = db.Column(db.String(20), nullable=False)  # 开票方式
    first_payment_start = db.Column(db.Date, nullable=False)  # 第一期收款开始日期
    first_payment_end = db.Column(db.Date, nullable=False)  # 第一期收款结束日期
    total_periods = db.Column(db.Integer, nullable=False)  # 总期数
    next_payment_date = db.Column(db.Date, nullable=False)  # 下次收款日期
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='有效')  # 合同状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='contracts')
    room = db.relationship('Room', backref='contracts')

class RentPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)  # 开始日
    end_day = db.Column(db.Integer, nullable=False)    # 结束日
    period_start_date = db.Column(db.Date, nullable=False)  # 期间开始日期
    period_end_date = db.Column(db.Date, nullable=False)    # 期间结束日期
    days = db.Column(db.Integer, nullable=False)       # 实际天数
    amount = db.Column(db.Float, nullable=False)       # 应收金额
    received_amount = db.Column(db.Float, default=0.0) # 已收金额
    status = db.Column(db.String(20), default='未收')  # 状态：未收/部分收款/已收
    due_date = db.Column(db.Date, nullable=False)      # 到期日
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    contract = db.relationship('Contract', backref='rent_plans')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    rent_plan_id = db.Column(db.Integer, db.ForeignKey('rent_plan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    contract = db.relationship('Contract', backref='payments')
    rent_plan = db.relationship('RentPlan', backref='payments')

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    invoice_number = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    contract = db.relationship('Contract', backref='invoices')
    payment = db.relationship('Payment', backref='invoices')

# 创建数据库表
with app.app_context():
    db.create_all()

# 工具函数
def calculate_rent_by_days(unit_price, area, start_day, end_day, year, month):
    """按天计算租金"""
    days_in_month = calendar.monthrange(year, month)[1]
    actual_days = end_day - start_day + 1
    # 月租金 = 面积 * 单价 * 365 / 12，按天数比例计算
    monthly_rent = unit_price * area * 365 / 12
    return round(monthly_rent * actual_days / days_in_month, 2)

def generate_rent_plans(contract):
    """为合同生成租金计划"""
    # 删除现有的租金计划
    RentPlan.query.filter_by(contract_id=contract.id).delete()
    
    current_date = contract.start_date
    end_date = contract.end_date
    
    # 根据付款周期确定每次收款的间隔
    if "按月" in contract.payment_frequency or "月付" in contract.payment_frequency:
        interval_months = 1
    elif "按季度" in contract.payment_frequency or "季付" in contract.payment_frequency:
        interval_months = 3
    elif "按半年" in contract.payment_frequency or "半年付" in contract.payment_frequency:
        interval_months = 6
    elif "按年" in contract.payment_frequency or "年付" in contract.payment_frequency:
        interval_months = 12
    else:
        interval_months = 1  # 默认按月
    
    period_start = current_date
    period_count = 0
    
    while period_start <= end_date:
        # 计算本期结束日期
        if interval_months == 1:
            # 按月支付
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1, day=1) - timedelta(days=1)
        else:
            # 按季度、半年或年支付
            # 计算结束月份和年份
            end_month = period_start.month + interval_months
            end_year = period_start.year
            
            while end_month > 12:
                end_month -= 12
                end_year += 1
            
            # 计算结束日期
            try:
                period_end = period_start.replace(year=end_year, month=end_month, day=1) - timedelta(days=1)
            except ValueError:
                # 如果月份不存在，使用最后一天
                last_day = calendar.monthrange(end_year, end_month)[1]
                period_end = period_start.replace(year=end_year, month=end_month, day=last_day)
        
        # 确保不超过合同结束日期
        if period_end > end_date:
            period_end = end_date
        
        # 计算本期实际天数
        days = (period_end - period_start).days + 1
        
        # 计算本期金额
        amount = calculate_rent_by_days(contract.unit_price, contract.room.area, 
                                      period_start.day, period_end.day, 
                                      period_start.year, period_start.month)
        
        # 计算到期日（本期开始日期加上付款日）
        try:
            due_date = period_start.replace(day=contract.payment_day)
        except ValueError:
            # 如果付款日超出月份天数，使用月份最后一天
            last_day = calendar.monthrange(period_start.year, period_start.month)[1]
            due_date = period_start.replace(day=min(contract.payment_day, last_day))
        
        if due_date < period_start:
            # 如果付款日早于开始日期，则到期日为下个月的付款日
            if period_start.month == 12:
                try:
                    due_date = period_start.replace(year=period_start.year + 1, month=1, day=contract.payment_day)
                except ValueError:
                    due_date = period_start.replace(year=period_start.year + 1, month=1, day=31)
            else:
                try:
                    due_date = period_start.replace(month=period_start.month + 1, day=contract.payment_day)
                except ValueError:
                    last_day = calendar.monthrange(period_start.year, period_start.month + 1)[1]
                    due_date = period_start.replace(month=period_start.month + 1, day=last_day)
        
        # 创建租金计划
        rent_plan = RentPlan(
            contract_id=contract.id,
            year=period_start.year,
            month=period_start.month,
            start_day=period_start.day,
            end_day=period_end.day,
            period_start_date=period_start,
            period_end_date=period_end,
            days=days,
            amount=amount,
            due_date=due_date
        )
        db.session.add(rent_plan)
        
        # 移动到下一期
        period_start = period_end + timedelta(days=1)
        period_count += 1
    
    db.session.commit()

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers')
def customers():
    customers = Customer.query.all()
    
    # 为每个客户计算租赁详情
    for customer in customers:
        # 获取该客户的所有合同
        contracts = Contract.query.filter_by(customer_id=customer.id).all()
        
        # 计算租赁详情
        customer.rental_details = []
        total_contract_amount = 0
        total_received_amount = 0
        
        for contract in contracts:
            # 计算合同总金额（月租金 * 租期月数）
            start_date = contract.start_date
            end_date = contract.end_date
            months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            if end_date.day > start_date.day:
                months_diff += 1
            
            # 安全获取房间信息
            room = Room.query.get(contract.room_id)
            if room:
                # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
                monthly_rent = round(contract.unit_price * room.area * 365 / 12, 2)
                contract_total_amount = monthly_rent * months_diff
                room_number = room.room_number
            else:
                # 默认面积100平方米
                monthly_rent = round(contract.unit_price * 100 * 365 / 12, 2)
                contract_total_amount = monthly_rent * months_diff
                room_number = "未知房间"
            
            # 计算已收金额
            received_amount = 0
            rent_plans = RentPlan.query.filter_by(contract_id=contract.id).all()
            for plan in rent_plans:
                received_amount += plan.received_amount
            
            # 添加到租赁详情
            customer.rental_details.append({
                'room_number': room_number,
                'start_date': contract.start_date.strftime('%Y-%m-%d'),
                'end_date': contract.end_date.strftime('%Y-%m-%d'),
                'contract_amount': contract_total_amount,
                'received_amount': received_amount,
                'deposit_contract': contract.deposit_contract,
                'deposit_received': contract.deposit_received
            })
            
            total_contract_amount += contract_total_amount
            total_received_amount += received_amount
        
        customer.total_contract_amount = total_contract_amount
        customer.total_received_amount = total_received_amount
    
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        data = request.get_json()
        customer = Customer(
            customer_id=data['customer_id'],
            company_name=data['company_name'],
            contact_person=data['contact_person'],
            contact_phone=data['contact_phone'],
            contact_email=data.get('contact_email', ''),
            advance_cost=float(data.get('advance_cost', 0))
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify({'success': True, 'message': '客户添加成功'})
    return render_template('add_customer.html')

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        data = request.get_json()
        customer.customer_id = data['customer_id']
        customer.company_name = data['company_name']
        customer.contact_person = data['contact_person']
        customer.contact_phone = data['contact_phone']
        customer.contact_email = data.get('contact_email', '')
        customer.advance_cost = float(data.get('advance_cost', 0))
        db.session.commit()
        return jsonify({'success': True, 'message': '客户信息更新成功'})
    return render_template('edit_customer.html', customer=customer)

@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # 检查是否有相关合同
        contracts = Contract.query.filter_by(customer_id=customer_id).all()
        if contracts:
            # 如果有合同，先删除相关数据
            for contract in contracts:
                # 删除相关的收款记录
                payments = Payment.query.filter_by(contract_id=contract.id).all()
                for payment in payments:
                    # 删除相关的发票
                    Invoice.query.filter_by(payment_id=payment.id).delete()
                    db.session.delete(payment)
                
                # 删除租金计划
                RentPlan.query.filter_by(contract_id=contract.id).delete()
                
                # 删除合同
                db.session.delete(contract)
            
            # 将相关房间状态改为空置
            for contract in contracts:
                room = Room.query.get(contract.room_id)
                if room:
                    room.status = '空置'
        
        # 删除客户
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'success': True, 'message': '客户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

@app.route('/rooms')
def rooms():
    rooms = Room.query.all()
    
    # 计算按面积的出租率
    total_area = sum(room.area for room in rooms)
    occupied_area = sum(room.area for room in rooms if room.status == '已出租')
    vacant_area = total_area - occupied_area
    
    # 计算按房间数的出租率（保留原有逻辑）
    total_rooms = len(rooms)
    occupied_rooms = len([room for room in rooms if room.status == '已出租'])
    vacant_rooms = total_rooms - occupied_rooms
    
    return render_template('rooms.html', rooms=rooms, 
                         total_area=total_area, occupied_area=occupied_area, vacant_area=vacant_area,
                         total_rooms=total_rooms, occupied_rooms=occupied_rooms, vacant_rooms=vacant_rooms)

@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        data = request.get_json()
        room = Room(
            room_number=data['room_number'],
            area=float(data['area']),
            floor=data['floor'],
            unit_price=float(data['unit_price'])
        )
        db.session.add(room)
        db.session.commit()
        return jsonify({'success': True, 'message': '房间添加成功'})
    return render_template('add_room.html')

@app.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    if request.method == 'POST':
        data = request.get_json()
        room.room_number = data['room_number']
        room.area = float(data['area'])
        room.floor = data['floor']
        room.unit_price = float(data['unit_price'])
        db.session.commit()
        return jsonify({'success': True, 'message': '房间信息更新成功'})
    return render_template('edit_room.html', room=room)

@app.route('/rooms/<int:room_id>/delete', methods=['POST'])
def delete_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        
        # 检查是否有相关合同
        contracts = Contract.query.filter_by(room_id=room_id).all()
        if contracts:
            # 如果有合同，先删除相关数据
            for contract in contracts:
                # 删除相关的收款记录
                payments = Payment.query.filter_by(contract_id=contract.id).all()
                for payment in payments:
                    # 删除相关的发票
                    Invoice.query.filter_by(payment_id=payment.id).delete()
                    db.session.delete(payment)
                
                # 删除租金计划
                RentPlan.query.filter_by(contract_id=contract.id).delete()
                
                # 删除合同
                db.session.delete(contract)
        
        # 删除房间
        db.session.delete(room)
        db.session.commit()
        return jsonify({'success': True, 'message': '房间删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

@app.route('/contracts')
def contracts():
    contracts = Contract.query.all()
    return render_template('contracts.html', contracts=contracts)

@app.route('/contracts/add', methods=['GET', 'POST'])
def add_contract():
    if request.method == 'POST':
        data = request.get_json()
        contract = Contract(
            contract_number=data['contract_number'],
            customer_id=int(data['customer_id']),
            room_id=int(data['room_id']),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            unit_price=float(data['unit_price']),
            monthly_rent=float(data['monthly_rent']),
            yearly_rent=float(data['yearly_rent']),
            contract_amount=float(data['contract_amount']),
            payment_frequency=data['payment_frequency'],
            received_amount=float(data.get('received_amount', 0)),
            deposit_contract=float(data['deposit_contract']),
            deposit_received=float(data['deposit_received']),
            payment_day=int(data['payment_day']),
            payment_method=data['payment_method'],
            invoice_method=data['invoice_method'],
            first_payment_start=datetime.strptime(data['first_payment_start'], '%Y-%m-%d').date(),
            first_payment_end=datetime.strptime(data['first_payment_end'], '%Y-%m-%d').date(),
            total_periods=int(data['total_periods']),
            next_payment_date=datetime.strptime(data['next_payment_date'], '%Y-%m-%d').date(),
            remarks=data.get('remarks', '')
        )
        db.session.add(contract)
        db.session.commit()
        
        room = Room.query.get(contract.room_id)
        room.status = '已出租'
        db.session.commit()
        
        generate_rent_plans(contract)
        
        return jsonify({'success': True, 'message': '合同添加成功'})
    
    customers = Customer.query.all()
    rooms = Room.query.filter_by(status='空置').all()
    return render_template('add_contract.html', customers=customers, rooms=rooms)

@app.route('/contracts/<int:contract_id>/edit', methods=['GET', 'POST'])
def edit_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if request.method == 'POST':
        data = request.get_json()
        contract.contract_number = data['contract_number']
        contract.customer_id = int(data['customer_id'])
        contract.room_id = int(data['room_id'])
        contract.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        contract.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        contract.unit_price = float(data['unit_price'])
        contract.payment_frequency = data['payment_frequency']
        contract.deposit_contract = float(data['deposit_contract'])
        contract.deposit_received = float(data['deposit_received'])
        contract.payment_day = int(data['payment_day'])
        contract.payment_method = data['payment_method']
        contract.invoice_method = data['invoice_method']
        contract.remarks = data.get('remarks', '')
        db.session.commit()
        
        generate_rent_plans(contract)
        
        return jsonify({'success': True, 'message': '合同信息更新成功'})
    
    customers = Customer.query.all()
    rooms = Room.query.all()
    return render_template('edit_contract.html', contract=contract, customers=customers, rooms=rooms)

@app.route('/contracts/<int:contract_id>/delete', methods=['POST'])
def delete_contract(contract_id):
    try:
        contract = Contract.query.get_or_404(contract_id)
        
        # 删除相关的收款记录
        payments = Payment.query.filter_by(contract_id=contract_id).all()
        for payment in payments:
            # 删除相关的发票
            Invoice.query.filter_by(payment_id=payment.id).delete()
            db.session.delete(payment)
        
        # 删除租金计划
        RentPlan.query.filter_by(contract_id=contract_id).delete()
        
        # 将房间状态改为空置
        room = Room.query.get(contract.room_id)
        if room:
            room.status = '空置'
        
        # 删除合同
        db.session.delete(contract)
        db.session.commit()
        return jsonify({'success': True, 'message': '合同删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

@app.route('/payments')
def payments():
    # 获取筛选参数
    company_filter = request.args.get('company', '')
    date_sort = request.args.get('sort', 'desc')  # desc 或 asc
    
    # 基础查询
    query = Payment.query.join(Contract).join(Customer).join(Room)
    
    # 按公司筛选
    if company_filter:
        query = query.filter(Customer.company_name.like(f'%{company_filter}%'))
    
    # 按日期排序
    if date_sort == 'asc':
        query = query.order_by(Payment.payment_date.asc())
    else:
        query = query.order_by(Payment.payment_date.desc())
    
    payments = query.all()
    
    # 获取所有公司名称用于筛选
    companies = db.session.query(Customer.company_name).distinct().all()
    companies = [company[0] for company in companies]
    
    return render_template('payments.html', payments=payments, companies=companies, 
                         company_filter=company_filter, date_sort=date_sort)

@app.route('/payments/add', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # 验证必需字段
            required_fields = ['contract_id', 'rent_plan_id', 'amount', 'payment_date', 'payment_method']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'message': f'缺少必需字段：{field}'})
            
            # 验证合同和租金计划是否存在
            contract = Contract.query.get(int(data['contract_id']))
            if not contract:
                return jsonify({'success': False, 'message': '合同不存在'})
            
            rent_plan = RentPlan.query.get(int(data['rent_plan_id']))
            if not rent_plan:
                return jsonify({'success': False, 'message': '租金计划不存在'})
            
            # 解析日期
            try:
                payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d %H:%M')
                except ValueError:
                    return jsonify({'success': False, 'message': '日期格式错误'})
            
            # 创建付款记录
            payment = Payment(
                contract_id=int(data['contract_id']),
                rent_plan_id=int(data['rent_plan_id']),
                amount=float(data['amount']),
                payment_date=payment_date,
                payment_method=data['payment_method'],
                remarks=data.get('remarks', '')
            )
            db.session.add(payment)
            
            # 更新租金计划的已收金额和状态
            rent_plan.received_amount += payment.amount
            
            # 根据已收金额更新状态
            if rent_plan.received_amount >= rent_plan.amount:
                rent_plan.status = '已收'
                rent_plan.received_amount = rent_plan.amount  # 确保不超过应收金额
            else:
                rent_plan.status = '部分收款'
            
            db.session.commit()
            return jsonify({'success': True, 'message': '收款登记成功'})
            
        except Exception as e:
            db.session.rollback()
            print(f"收款登记错误: {str(e)}")
            return jsonify({'success': False, 'message': f'收款登记失败：{str(e)}'})
    
    contracts = Contract.query.all()
    rent_plans = RentPlan.query.filter_by(status='未收').all()
    return render_template('add_payment.html', contracts=contracts, rent_plans=rent_plans)

@app.route('/rent_plans')
def rent_plans():
    rent_plans = RentPlan.query.all()
    return render_template('rent_plans.html', rent_plans=rent_plans)

@app.route('/statistics')
def statistics():
    total_customers = Customer.query.count()
    total_rooms = Room.query.count()
    occupied_rooms = Room.query.filter_by(status='已出租').count()
    total_contracts = Contract.query.count()
    active_contracts = Contract.query.filter_by(status='有效').count()
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_rent_plans = RentPlan.query.filter_by(year=current_year, month=current_month).all()
    
    total_due = sum(plan.amount for plan in monthly_rent_plans)
    total_received = sum(plan.received_amount for plan in monthly_rent_plans)
    total_unpaid = total_due - total_received
    
    return render_template('statistics.html', 
                         total_customers=total_customers,
                         total_rooms=total_rooms,
                         occupied_rooms=occupied_rooms,
                         total_contracts=total_contracts,
                         active_contracts=active_contracts,
                         total_due=total_due,
                         total_received=total_received,
                         total_unpaid=total_unpaid)

@app.route('/api/stats')
def api_stats():
    total_customers = Customer.query.count()
    total_rooms = Room.query.count()
    active_contracts = Contract.query.filter_by(status='有效').count()
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_rent_plans = RentPlan.query.filter_by(year=current_year, month=current_month).all()
    monthly_revenue = sum(plan.received_amount for plan in monthly_rent_plans)
    
    return jsonify({
        'total_customers': total_customers,
        'total_rooms': total_rooms,
        'active_contracts': active_contracts,
        'monthly_revenue': monthly_revenue
    })

@app.route('/api/clear_database', methods=['POST'])
def api_clear_database():
    """清空数据库API"""
    try:
        from sqlalchemy import text
        db.session.execute(text('DELETE FROM payment'))
        db.session.execute(text('DELETE FROM invoice'))
        db.session.execute(text('DELETE FROM rent_plan'))
        db.session.execute(text('DELETE FROM contract'))
        db.session.execute(text('DELETE FROM customer'))
        db.session.execute(text('DELETE FROM room'))
        db.session.commit()
        return jsonify({'success': True, 'message': '数据库清空成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'清空失败：{str(e)}'})

@app.route('/api/activities')
def api_activities():
    activities = []
    
    recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
    for customer in recent_customers:
        activities.append({
            'icon': 'fas fa-user-plus',
            'title': f'新增客户: {customer.company_name}',
            'time': customer.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    recent_contracts = Contract.query.order_by(Contract.created_at.desc()).limit(5).all()
    for contract in recent_contracts:
        activities.append({
            'icon': 'fas fa-file-contract',
            'title': f'签订合同: {contract.contract_number}',
            'time': contract.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    activities.sort(key=lambda x: x['time'], reverse=True)
    return jsonify({'activities': activities[:10]})

@app.route('/api/customers')
def api_customers():
    customers = Customer.query.all()
    
    # 为每个客户计算租赁详情
    customers_data = []
    for customer in customers:
        # 获取该客户的所有合同
        contracts = Contract.query.filter_by(customer_id=customer.id).all()
        
        # 计算租赁详情
        rental_details = []
        total_contract_amount = 0
        total_received_amount = 0
        
        for contract in contracts:
            # 计算合同总金额（月租金 * 租期月数）
            start_date = contract.start_date
            end_date = contract.end_date
            months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            if end_date.day > start_date.day:
                months_diff += 1
            
            # 安全获取房间信息
            room = Room.query.get(contract.room_id)
            if room:
                # 月租金 = 面积 * 单价 * 365 / 12，取2位小数
                monthly_rent = round(contract.unit_price * room.area * 365 / 12, 2)
                contract_total_amount = monthly_rent * months_diff
                room_number = room.room_number
            else:
                # 默认面积100平方米
                monthly_rent = round(contract.unit_price * 100 * 365 / 12, 2)
                contract_total_amount = monthly_rent * months_diff
                room_number = "未知房间"
            
            # 计算已收金额
            received_amount = 0
            rent_plans = RentPlan.query.filter_by(contract_id=contract.id).all()
            for plan in rent_plans:
                received_amount += plan.received_amount
            
            # 添加到租赁详情
            rental_details.append({
                'room_number': room_number,
                'start_date': contract.start_date.strftime('%Y-%m-%d'),
                'end_date': contract.end_date.strftime('%Y-%m-%d'),
                'contract_amount': contract_total_amount,
                'received_amount': received_amount,
                'deposit_contract': contract.deposit_contract,
                'deposit_received': contract.deposit_received
            })
            
            total_contract_amount += contract_total_amount
            total_received_amount += received_amount
        
        customers_data.append({
            'id': customer.id,
            'customer_id': customer.customer_id,
            'company_name': customer.company_name,
            'contact_person': customer.contact_person,
            'contact_phone': customer.contact_phone,
            'contact_email': customer.contact_email,
            'rental_details': rental_details,
            'total_contract_amount': total_contract_amount,
            'total_received_amount': total_received_amount
        })
    
    return jsonify(customers_data)

@app.route('/api/rooms')
def api_rooms():
    rooms = Room.query.all()
    return jsonify([{
        'id': r.id,
        'room_number': r.room_number,
        'area': r.area,
        'floor': r.floor,
        'unit_price': r.unit_price,
        'status': r.status
    } for r in rooms])

@app.route('/api/rooms/available')
def api_rooms_available():
    # 修改为显示所有房间，而不是只显示空置房间
    rooms = Room.query.all()
    return jsonify({
        'rooms': [{
            'id': r.id,
            'room_number': r.room_number,
            'area': r.area,
            'floor': r.floor,
            'unit_price': r.unit_price,
            'status': r.status
        } for r in rooms]
    })

@app.route('/api/statistics/monthly_plans')
def api_monthly_plans():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    rent_plans = db.session.query(RentPlan, Contract, Room, Customer).join(
        Contract, RentPlan.contract_id == Contract.id
    ).join(
        Room, Contract.room_id == Room.id
    ).join(
        Customer, Contract.customer_id == Customer.id
    ).filter(
        RentPlan.year == year,
        RentPlan.month == month
    ).all()
    
    plans_data = []
    for plan, contract, room, customer in rent_plans:
        plans_data.append({
            'plan_id': plan.id,
            'contract_number': contract.contract_number,
            'room_number': room.room_number,
            'customer_name': customer.company_name,
            'amount': plan.amount,
            'status': plan.status,
            'due_date': plan.due_date.strftime('%Y-%m-%d'),
            'days': plan.days
        })
    
    total_amount = sum(plan.amount for plan, _, _, _ in rent_plans)
    total_received = sum(plan.received_amount for plan, _, _, _ in rent_plans)
    total_unpaid = total_amount - total_received
    
    return jsonify({
        'plans': plans_data,
        'summary': {
            'total_amount': total_amount,
            'total_received': total_received,
            'total_unpaid': total_unpaid,
            'year': year,
            'month': month
        }
    })

@app.route('/api/statistics/room_plans')
def api_room_plans():
    room_id = request.args.get('room_id', type=int)
    
    if room_id:
        rent_plans = db.session.query(RentPlan, Contract, Room, Customer).join(
            Contract, RentPlan.contract_id == Contract.id
        ).join(
            Room, Contract.room_id == Room.id
        ).join(
            Customer, Contract.customer_id == Customer.id
        ).filter(
            Room.id == room_id
        ).order_by(RentPlan.year, RentPlan.month).all()
    else:
        rent_plans = db.session.query(RentPlan, Contract, Room, Customer).join(
            Contract, RentPlan.contract_id == Contract.id
        ).join(
            Room, Contract.room_id == Room.id
        ).join(
            Customer, Contract.customer_id == Customer.id
        ).order_by(Room.room_number, RentPlan.year, RentPlan.month).all()
    
    plans_data = []
    for plan, contract, room, customer in rent_plans:
        plans_data.append({
            'plan_id': plan.id,
            'contract_number': contract.contract_number,
            'room_number': room.room_number,
            'customer_name': customer.company_name,
            'amount': plan.amount,
            'status': plan.status,
            'due_date': plan.due_date.strftime('%Y-%m-%d'),
            'year': plan.year,
            'month': plan.month,
            'days': plan.days
        })
    
    total_amount = sum(plan.amount for plan, _, _, _ in rent_plans)
    total_received = sum(plan.received_amount for plan, _, _, _ in rent_plans)
    total_unpaid = total_amount - total_received
    
    return jsonify({
        'plans': plans_data,
        'summary': {
            'total_amount': total_amount,
            'total_received': total_received,
            'total_unpaid': total_unpaid,
            'room_id': room_id
        }
    })

@app.route('/api/contracts')
def api_contracts():
    contracts = Contract.query.all()
    return jsonify({
        'contracts': [{
            'id': c.id,
            'contract_number': c.contract_number,
            'customer': {
                'id': c.customer.id,
                'company_name': c.customer.company_name
            },
            'room': {
                'id': c.room.id,
                'room_number': c.room.room_number
            },
            'start_date': c.start_date.strftime('%Y-%m-%d'),
            'end_date': c.end_date.strftime('%Y-%m-%d'),
            'status': c.status
        } for c in contracts]
    })

@app.route('/api/rent_plans')
def api_rent_plans():
    contract_id = request.args.get('contract_id', type=int)
    
    if contract_id:
        rent_plans = RentPlan.query.filter_by(contract_id=contract_id).order_by(RentPlan.year, RentPlan.month).all()
    else:
        rent_plans = RentPlan.query.order_by(RentPlan.contract_id, RentPlan.year, RentPlan.month).all()
    
    return jsonify({
        'rent_plans': [{
            'id': plan.id,
            'contract_id': plan.contract_id,
            'year': plan.year,
            'month': plan.month,
            'amount': plan.amount,
            'status': plan.status,
            'due_date': plan.due_date.strftime('%Y-%m-%d'),
            'days': plan.days
        } for plan in rent_plans]
    })

@app.route('/download_template')
def download_template():
    """下载Excel导入模板"""
    # 创建示例数据
    sample_data = {
        '公司名称': ['示例公司A', '示例公司B'],
        '联系人': ['张三', '李四'],
        '联系方式': ['13800138001', '13800138002'],
        '邮箱': ['zhangsan@example.com', 'lisi@example.com'],
        '房间号': ['A101', 'A102'],
        '面积': [50.0, 75.5],
        '楼层': ['1层', '1层'],
        '单价（元/㎡/月）': [80.0, 85.0],
        '合同编号': ['HT2024001', 'HT2024002'],
        '租期开始时间': ['2024-01-01', '2024-01-15'],
        '租期结束时间': ['2024-12-31', '2024-12-31'],
        '月租金（元）': [4000.0, 6412.5],
        '年租金（元）': [48000.0, 76950.0],
        '合同金额（元）': [48000.0, 76950.0],
        '付款周期': ['月付', '季付'],
        '收款金额（元）': [0.0, 0.0],
        '租赁保证金（合同约定）': [4000.0, 6000.0],
        '租赁保证金（实收）': [4000.0, 6000.0],
        '付款日': [1, 15],
        '收款方式': ['银行转账', '现金'],
        '开票方式': ['增值税普通发票', '增值税专用发票'],
        '第一期收款开始日期': ['2024-01-01', '2024-01-15'],
        '第一期收款结束日期': ['2024-01-31', '2024-04-14'],
        '总期数': [12, 4],
        '下次收款日期': ['2024-02-01', '2024-04-15'],
        '备注': ['示例备注1', '示例备注2']
    }
    
    # 创建DataFrame
    df = pd.DataFrame(sample_data)
    
    # 创建Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='数据导入模板', index=False)
        
        # 获取工作表
        worksheet = writer.sheets['数据导入模板']
        
        # 设置列宽
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='租赁数据导入模板.xlsx'
    )

@app.route('/import', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if file and file.filename.endswith('.xlsx'):
            try:
                df = pd.read_excel(file)
                
                for _, row in df.iterrows():
                    # 创建或更新客户
                    customer = Customer.query.filter_by(company_name=row['公司名称']).first()
                    if not customer:
                        customer = Customer(
                            customer_id=f"CUST{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            company_name=row['公司名称'],
                            contact_person=row.get('联系人', ''),
                            contact_phone=row.get('联系方式', ''),
                            contact_email=row.get('邮箱', '')
                        )
                        db.session.add(customer)
                        db.session.flush()
                    
                    # 创建或更新房间
                    room = Room.query.filter_by(room_number=row['房间号']).first()
                    if not room:
                        room = Room(
                            room_number=row['房间号'],
                            area=float(row['面积']),
                            floor=row.get('楼层', ''),
                            unit_price=float(row['单价（元/㎡/月）'])
                        )
                        db.session.add(room)
                        db.session.flush()
                    
                    # 创建合同
                    contract = Contract(
                        contract_number=row['合同编号'],
                        customer_id=customer.id,
                        room_id=room.id,
                        start_date=pd.to_datetime(row['租期开始时间']).date(),
                        end_date=pd.to_datetime(row['租期结束时间']).date(),
                        unit_price=float(row['单价（元/㎡/月）']),
                        monthly_rent=float(row.get('月租金（元）', 0)),
                        yearly_rent=float(row.get('年租金（元）', 0)),
                        contract_amount=float(row.get('合同金额（元）', 0)),
                        payment_frequency=row.get('付款周期', row.get('支付方式', '月付')),
                        received_amount=float(row.get('收款金额（元）', 0)),
                        deposit_contract=float(row['租赁保证金（合同约定）']),
                        deposit_received=float(row['租赁保证金（实收）']),
                        payment_day=int(row['付款日']),
                        payment_method=row['收款方式'],
                        invoice_method=row['开票方式'],
                        first_payment_start=pd.to_datetime(row.get('第一期收款开始日期', row['租期开始时间'])).date(),
                        first_payment_end=pd.to_datetime(row.get('第一期收款结束日期', row['租期开始时间'])).date(),
                        total_periods=int(row.get('总期数', 1)),
                        next_payment_date=pd.to_datetime(row.get('下次收款日期', row['租期开始时间'])).date(),
                        remarks=row.get('备注', '')
                    )
                    db.session.add(contract)
                    db.session.flush()
                    
                    # 生成租金计划
                    generate_rent_plans(contract)
                
                db.session.commit()
                return jsonify({'success': True, 'message': '数据导入成功'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'导入失败: {str(e)}'})
        
        return jsonify({'success': False, 'message': '请上传Excel文件'})
    
    return render_template('import.html')

@app.route('/export/<data_type>')
def export_data(data_type):
    if data_type == 'customers':
        customers = Customer.query.all()
        data = []
        for customer in customers:
            data.append({
                '客户ID': customer.customer_id,
                '公司名称': customer.company_name,
                '联系人': customer.contact_person,
                '联系方式': customer.contact_phone,
                '邮箱': customer.contact_email
            })
        df = pd.DataFrame(data)
        
    elif data_type == 'rooms':
        rooms = Room.query.all()
        data = []
        for room in rooms:
            data.append({
                '房间号': room.room_number,
                '面积': room.area,
                '楼层': room.floor,
                '单价': room.unit_price,
                '状态': room.status
            })
        df = pd.DataFrame(data)
        
    elif data_type == 'contracts':
        contracts = Contract.query.all()
        data = []
        for contract in contracts:
            data.append({
                '合同编号': contract.contract_number,
                '公司名称': contract.customer.company_name,
                '房间号': contract.room.room_number,
                '租期开始': contract.start_date.strftime('%Y-%m-%d'),
                '租期结束': contract.end_date.strftime('%Y-%m-%d'),
                '单价': contract.unit_price,
                '支付方式': contract.payment_frequency,
                '状态': contract.status
            })
        df = pd.DataFrame(data)
        
    elif data_type == 'rent_plans':
        rent_plans = RentPlan.query.all()
        data = []
        for plan in rent_plans:
            data.append({
                '合同编号': plan.contract.contract_number,
                '公司名称': plan.contract.customer.company_name,
                '房间号': plan.contract.room.room_number,
                '年月': f"{plan.year}-{plan.month:02d}",
                '应收金额': plan.amount,
                '状态': plan.status,
                '到期日': plan.due_date.strftime('%Y-%m-%d')
            })
        df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='数据', index=False)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{data_type}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@app.route('/export/csv/<data_type>')
def export_csv(data_type):
    """导出CSV格式的数据"""
    if data_type == 'monthly_plans':
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not year or not month:
            return jsonify({'success': False, 'message': '请指定年月参数'})
        
        # 获取指定月份的租金计划
        rent_plans = RentPlan.query.filter_by(year=year, month=month).all()
        data = []
        for plan in rent_plans:
            # 计算已收金额
            received_amount = sum(payment.amount for payment in plan.payments)
            # 计算天数差
            days_diff = (plan.due_date - datetime.now().date()).days
            
            data.append({
                '合同编号': plan.contract.contract_number,
                '房间号': plan.contract.room.room_number,
                '客户名称': plan.contract.customer.company_name,
                '应收金额': plan.amount,
                '已收金额': received_amount,
                '未收金额': plan.amount - received_amount,
                '状态': plan.status,
                '到期日': plan.due_date.strftime('%Y-%m-%d'),
                '剩余天数': days_diff
            })
        
        df = pd.DataFrame(data)
        filename = f'月度收款计划_{year}年{month:02d}月_{datetime.now().strftime("%Y%m%d")}.csv'
        
    elif data_type == 'room_plans':
        room_id = request.args.get('room_id', type=int)
        
        if not room_id:
            return jsonify({'success': False, 'message': '请指定房间ID参数'})
        
        # 获取指定房间的租金计划
        rent_plans = RentPlan.query.join(Contract).filter(Contract.room_id == room_id).all()
        data = []
        for plan in rent_plans:
            # 计算已收金额
            received_amount = sum(payment.amount for payment in plan.payments)
            # 计算天数差
            days_diff = (plan.due_date - datetime.now().date()).days
            
            data.append({
                '合同编号': plan.contract.contract_number,
                '房间号': plan.contract.room.room_number,
                '客户名称': plan.contract.customer.company_name,
                '年月': f"{plan.year}年{plan.month}月",
                '应收金额': plan.amount,
                '已收金额': received_amount,
                '未收金额': plan.amount - received_amount,
                '状态': plan.status,
                '到期日': plan.due_date.strftime('%Y-%m-%d'),
                '剩余天数': days_diff
            })
        
        room = Room.query.get(room_id)
        room_name = room.room_number if room else f'房间{room_id}'
        df = pd.DataFrame(data)
        filename = f'{room_name}收款计划_{datetime.now().strftime("%Y%m%d")}.csv'
        
    elif data_type == 'statistics_summary':
        # 导出统计汇总数据
        total_customers = Customer.query.count()
        total_rooms = Room.query.count()
        occupied_rooms = Room.query.filter_by(status='已出租').count()
        total_contracts = Contract.query.count()
        active_contracts = Contract.query.filter_by(status='有效').count()
        
        # 计算本月应收和已收
        current_year = datetime.now().year
        current_month = datetime.now().month
        monthly_plans = RentPlan.query.filter_by(year=current_year, month=current_month).all()
        
        total_due = sum(plan.amount for plan in monthly_plans)
        total_received = sum(
            sum(payment.amount for payment in plan.payments) 
            for plan in monthly_plans
        )
        total_unpaid = total_due - total_received
        
        data = [{
            '统计项目': '总客户数',
            '数值': total_customers,
            '单位': '个'
        }, {
            '统计项目': '总房间数',
            '数值': total_rooms,
            '单位': '个'
        }, {
            '统计项目': '已租房间数',
            '数值': occupied_rooms,
            '单位': '个'
        }, {
            '统计项目': '房间使用率',
            '数值': f"{occupied_rooms / total_rooms * 100:.1f}%" if total_rooms > 0 else "0%",
            '单位': ''
        }, {
            '统计项目': '总合同数',
            '数值': total_contracts,
            '单位': '个'
        }, {
            '统计项目': '有效合同数',
            '数值': active_contracts,
            '单位': '个'
        }, {
            '统计项目': '合同有效率',
            '数值': f"{active_contracts / total_contracts * 100:.1f}%" if total_contracts > 0 else "0%",
            '单位': ''
        }, {
            '统计项目': '本月应收',
            '数值': total_due,
            '单位': '元'
        }, {
            '统计项目': '本月已收',
            '数值': total_received,
            '单位': '元'
        }, {
            '统计项目': '本月未收',
            '数值': total_unpaid,
            '单位': '元'
        }, {
            '统计项目': '收款率',
            '数值': f"{total_received / total_due * 100:.1f}%" if total_due > 0 else "0%",
            '单位': ''
        }]
        
        df = pd.DataFrame(data)
        filename = f'统计分析汇总_{datetime.now().strftime("%Y%m%d")}.csv'
        
    else:
        return jsonify({'success': False, 'message': '不支持的数据类型'})
    
    # 创建CSV文件
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

# 异常处理路由
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_title='页面未找到',
                         error_message='抱歉，您访问的页面不存在。',
                         error_code='404',
                         error_description='请求的页面或资源未找到',
                         show_contact=False), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_title='服务器内部错误',
                         error_message='抱歉，服务器遇到了一个内部错误。',
                         error_code='500',
                         error_description='服务器内部处理错误',
                         show_contact=True), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html',
                         error_title='访问被拒绝',
                         error_message='抱歉，您没有权限访问此页面。',
                         error_code='403',
                         error_description='权限不足或访问被拒绝',
                         show_contact=False), 403

@app.errorhandler(405)
def method_not_allowed_error(error):
    return render_template('error.html',
                         error_title='请求方法不允许',
                         error_message='抱歉，此页面不支持您使用的请求方法。',
                         error_code='405',
                         error_description='HTTP请求方法不被允许',
                         show_contact=False), 405

# 通用异常处理
@app.errorhandler(Exception)
def handle_exception(e):
    # 记录错误日志
    app.logger.error(f'未处理的异常: {str(e)}')
    
    return render_template('error.html',
                         error_title='系统错误',
                         error_message='抱歉，系统遇到了一个意外错误。',
                         error_code='UNKNOWN',
                         error_description=str(e),
                         show_contact=True), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
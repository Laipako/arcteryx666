import streamlit as st
import re


def convert_krw_to_cny(krw_amount):
    """
    将韩元金额转换为人民币金额
    复用主页面显示的汇率数据
    """
    try:
        # 从主页面获取汇率信息
        if 'exchange_rate_info' in st.session_state:
            rate_str = st.session_state.exchange_rate_info
            # 从字符串中提取汇率值（如从"10000韩元=50.34人民币"提取50.34）
            match = re.search(r'10000韩元=(\d+\.?\d*)人民币', rate_str)
            if match:
                rate_per_10000 = float(match.group(1))
                cny_amount = (krw_amount / 10000) * rate_per_10000
                return int(cny_amount)  # 取整显示
    except:
        pass

    # 汇率获取失败时返回0（前端会只显示韩元）
    return 0


# 退税范围表（韩国标准 - 范围制）
REFUND_RATE_TABLE = [
    # (min_amount, max_amount, refund_amount)
    (15000, 29999, 1000),
    (30000, 49999, 2000),
    (50000, 74999, 3000),
    (75000, 99999, 5000),
    (100000, 124999, 7000),
    (125000, 149999, 8000),
    (150000, 174999, 9000),
    (175000, 199999, 10000),
    (200000, 224999, 12000),
    (225000, 249999, 13000),
    (250000, 274999, 15000),
    (275000, 299999, 17000),
    (300000, 324999, 19000),
    (325000, 349999, 21000),
    (350000, 374999, 23000),
    (375000, 399999, 25000),
    (400000, 424999, 27000),
    (425000, 449999, 28000),
    (450000, 474999, 30000),
    (475000, 499999, 32000),
    (500000, 549999, 35000),
    (550000, 599999, 37000),
    (600000, 649999, 41000),
    (650000, 699999, 45000),
    (700000, 749999, 50000),
    (750000, 799999, 53000),
    (800000, 849999, 57000),
    (850000, 899999, 60000),
    (900000, 949999, 65000),
    (950000, 999999, 68000),
    (1000000, 1099999, 75000),
    (1100000, 1199999, 80000),
    (1200000, 1299999, 90000),
    (1300000, 1399999, 95000),
    (1400000, 1499999, 105000),
    (1500000, 1599999, 110000),
    (1600000, 1699999, 115000),
    (1700000, 1799999, 127000),
    (1800000, 1899999, 135000),
    (1900000, 1999999, 140000),
    (2000000, 2099999, 150000),
    (2100000, 2199999, 155000),
    (2200000, 2299999, 160000),
    (2300000, 2399999, 170000),
    (2400000, 2499999, 177000),
    (2500000, 2599999, 185000),
    (2600000, 2699999, 190000),
    (2700000, 2799999, 200000),
    (2800000, 2899999, 210000),
    (2900000, 2999999, 215000),
    (3000000, 3099999, 225000),
    (3100000, 3199999, 230000),
    (3200000, 3299999, 235000),
    (3300000, 3399999, 240000),
    (3400000, 3499999, 250000),
    (3500000, 3599999, 260000),
    (3600000, 3699999, 270000),
    (3700000, 3799999, 280000),
    (3800000, 3899999, 285000),
    (3900000, 3999999, 290000),
    (4000000, 4099999, 300000),
    (4100000, 4199999, 310000),
    (4200000, 4299999, 315000),
    (4300000, 4399999, 320000),
    (4400000, 4499999, 333000),
    (4500000, 4599999, 340000),
    (4600000, 4699999, 350000),
    (4700000, 4799999, 360000),
    (4800000, 4899999, 370000),
    (4900000, 4999999, 380000),
    (5000000, 5099999, 390000),
    (5100000, 5199999, 400000),
    (5200000, 5299999, 410000),
    (5300000, 5399999, 420000),
    (5400000, 5499999, 430000),
    (5500000, 5599999, 440000),
    (5600000, 5699999, 450000),
    (5700000, 5799999, 460000),
    (5800000, 5899999, 470000),
    (5900000, 5999999, 480000),
]


def calculate_tax_refund(krw_amount):
    """
    计算退税额 - 基于韩国退税范围表（范围制）
    根据消费金额查表获取对应的固定退税额
    """
    if krw_amount < 15000:
        return 0
    
    # 查表获取退税额 - 查找金额所在的范围
    for min_amount, max_amount, refund_amount in REFUND_RATE_TABLE:
        if min_amount <= krw_amount <= max_amount:
            return refund_amount
    
    return 0


def calculate_detailed_price(total_krw, selected_discounts):
    """详细价格计算"""
    # 第1步：计算税前优惠
    pre_tax_discount = 0
    for discount in selected_discounts:
        if discount['type'] == 'pre_tax_percent':
            pre_tax_discount += total_krw * discount['rate']
        elif discount['type'] == 'pre_tax_fixed':
            if total_krw >= discount['threshold']:
                pre_tax_discount += discount['amount']
        elif discount['type'] == 'pre_tax_capped':
            if total_krw >= discount['threshold']:
                discount_amount = total_krw * discount['rate']
                pre_tax_discount += min(discount_amount, discount['cap'])
        elif discount['type'] == 'pre_tax_tiered':
            for tier in reversed(discount['tiers']):  # 从高到低检查
                if total_krw >= tier['threshold']:
                    pre_tax_discount += tier['amount']
                    break

    # 第2步：计算税前优惠后价格
    after_pre_tax = total_krw - pre_tax_discount

    # 第3步：根据税前优惠后的价格查看税后优惠（阶梯赠券和积分）
    gift_coupon = 0
    points_reward = 0
    for discount in selected_discounts:
        if discount['type'] == 'post_tax_tiered':
            for tier in reversed(discount['tiers']):  # 从高到低检查
                if after_pre_tax >= tier['threshold']:
                    gift_coupon = tier['amount']
                    break
        elif discount['type'] == 'post_tax_tiered_points':
            for tier in reversed(discount['tiers']):  # 从高到低检查
                if after_pre_tax >= tier['threshold']:
                    points_reward = tier['amount']
                    break

    # 第4步：计算退税额
    tax_refund = calculate_tax_refund(after_pre_tax)

    # 第5步：计算税后价格
    after_tax = after_pre_tax - tax_refund

    # 第6步：计算最终实付（商品券和积分都计入）
    total_post_tax_benefit = gift_coupon + points_reward
    final_payment = after_tax - total_post_tax_benefit

    return {
        'total_krw': total_krw,
        'pre_tax_discount': pre_tax_discount,
        'after_pre_tax': after_pre_tax,
        'tax_refund': tax_refund,
        'after_tax': after_tax,
        'gift_coupon': gift_coupon,
        'points_reward': points_reward,
        'final_payment': final_payment,
        'selected_discounts': [d['name'] for d in selected_discounts]
    }

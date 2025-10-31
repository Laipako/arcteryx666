import streamlit as st
from purchase_plan_manager import (
    get_plans_grouped_by_store,
    calculate_store_total_price,
    remove_product_from_plan,
    remove_store_from_plan,
    calculate_store_domestic_total
)
from calculation_utils import calculate_detailed_price, convert_krw_to_cny
import time


def show_purchase_plan_tab():
    """显示购买计划标签页"""
    st.header("🛒 购买计划")
    
    # 初始化session_state
    if "plan_refreshed" not in st.session_state:
        st.session_state.plan_refreshed = False
    
    # 初始化试算相关状态
    if "show_plan_calculation_config" not in st.session_state:
        st.session_state.show_plan_calculation_config = {}
    if "plan_calculation_result" not in st.session_state:
        st.session_state.plan_calculation_result = {}
    
    # 获取购买计划数据
    plans_by_store = get_plans_grouped_by_store()
    
    if not plans_by_store:
        st.info("暂无购买计划")
        return
    
    # 库存查询按钮区域
    st.subheader("📦 库存查询")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("查购买计划库存", key="check_plan_inventory"):
            try:
                from inventory_check import safe_batch_query
                from favorites_manager import load_favorites
                
                # 收集购买计划中的所有产品
                all_plan_products = []
                for products in plans_by_store.values():
                    all_plan_products.extend(products)
                
                if all_plan_products:
                    st.info(f"开始查询购买计划中的 {len(all_plan_products)} 个产品的库存...")
                    
                    # 从收藏中加载SKU信息
                    favorites = load_favorites()
                    
                    # 为购买计划产品补充SKU信息
                    plan_products_with_sku = []
                    for plan_product in all_plan_products:
                        # 从收藏中查找匹配的产品
                        for fav in favorites:
                            if (fav.get("product_model") == plan_product.get("product_model") and
                                fav.get("color") == plan_product.get("color") and
                                fav.get("size") == plan_product.get("size")):
                                # 找到匹配的收藏产品，使用其SKU
                                plan_product_copy = plan_product.copy()
                                plan_product_copy["sku"] = fav.get("sku")
                                plan_products_with_sku.append(plan_product_copy)
                                break
                    
                    if plan_products_with_sku:
                        # 调用库存查询函数
                        inventory_matrix = safe_batch_query(plan_products_with_sku)
                        
                        if inventory_matrix:
                            st.session_state.purchase_plan_inventory_matrix = inventory_matrix
                            st.success(f"✓ 查询完成！共获取 {len(inventory_matrix)} 个店铺的库存数据")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("库存查询失败，请检查网络连接或稍后重试")
                    else:
                        st.error(f"⚠️ 购买计划中有 {len(all_plan_products)} 个产品，但在收藏中找不到对应的SKU。请确保这些产品已添加到收藏中")
                else:
                    st.warning("购买计划中无产品")
            except Exception as e:
                st.error(f"库存查询异常: {e}")
    
    with col2:
        if st.button("导入收藏库存数据", key="import_favorites_inventory"):
            # 从session_state中获取收藏库存数据
            if st.session_state.get('inventory_matrix'):
                st.session_state.purchase_plan_inventory_matrix = st.session_state.inventory_matrix
                st.success("✓ 已导入收藏产品的库存数据")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("⚠️ 收藏产品库存数据不可用，请先在【⭐ 收藏产品】标签页查询库存")
    
    st.divider()
    
    # 遍历每个店铺
    for store_name in plans_by_store.keys():
        products = plans_by_store[store_name]
        total_price = calculate_store_total_price(products)
        
        # 店铺标题区域
        st.subheader(f"🏪 {store_name}")
        
        # 创建容器用于产品列表
        with st.container(border=True):
            # 显示每个产品
            for idx, product in enumerate(products):
                col1, col2, col3, col4 = st.columns([3, 1, 0.8, 0.8])
                
                with col1:
                    # 产品信息
                    product_display = f"{product['exact_model'] or product['product_model']} {product['color']} {product['size']}"
                    
                    # 新增：显示库存信息
                    # 库存矩阵使用 product_model 作为键（不是 exact_model）
                    product_key_for_inventory = f"{product['product_model']} {product['color']} {product['size']}"
                    
                    # 获取当前店铺的库存矩阵
                    inventory_matrix = st.session_state.get('purchase_plan_inventory_matrix', None)
                    
                    if inventory_matrix and store_name in inventory_matrix:
                        # 查询该店铺下该产品的库存
                        store_inventory = inventory_matrix[store_name]
                        if product_key_for_inventory in store_inventory:
                            stock_count = store_inventory[product_key_for_inventory]
                            if stock_count and int(stock_count) > 0:
                                product_display += f"({stock_count}件)"
                            else:
                                product_display += "(无库存)"
                        else:
                            # 库存未找到 - 显示无库存
                            product_display += "(无库存)"
                            # 添加调试信息（可选，仅在展开器中显示）
                            with st.expander("ℹ️ 库存匹配调试信息", expanded=False):
                                st.write(f"🔍 搜索的产品键：`{product_key_for_inventory}`")
                                st.write(f"📍 店铺：{store_name}")
                                st.write(f"📝 product_model: `{product.get('product_model')}`")
                                st.write(f"📝 exact_model: `{product.get('exact_model')}`")
                                if store_inventory:
                                    st.write(f"📦 该店铺的可用产品键（前10个）：")
                                    for i, key in enumerate(list(store_inventory.keys())[:10]):
                                        st.write(f"  {i+1}. `{key}`")
                                    if len(store_inventory) > 10:
                                        st.write(f"  ... 还有 {len(store_inventory) - 10} 个产品")
                                else:
                                    st.write("❌ 该店铺无库存数据")
                    else:
                        # 未查询库存
                        product_display += "(未查库存)"
                    
                    st.write(product_display)
                
                with col2:
                    # 价格
                    price_display = f"{product['price_krw']:,}韩元"
                    st.write(price_display)
                
                with col3:
                    # 删除按钮
                    if st.button("🗑️", key=f"delete_product_{product['id']}", help="删除该产品"):
                        if remove_product_from_plan(product['id']):
                            st.success("已删除")
                            st.rerun()
                
                with col4:
                    st.empty()  # 占位符保持对齐
            
            # 分割线
            st.divider()
            
            # 税前总价
            col1, col2, col3 = st.columns([3, 1, 0.8])
            with col1:
                st.write("**税前总价**")
            with col2:
                st.write(f"**{total_price:,}韩元**")
            with col3:
                st.empty()
        
        # 删除店铺和试算按钮区域
        col1, col2, col3, col4 = st.columns([3, 1, 1, 0.8])
        
        with col2:
            # 试算按钮
            if st.button("💰 试算", key=f"calc_plan_{store_name}"):
                st.session_state.show_plan_calculation_config[store_name] = True
                st.session_state.plan_calculation_result[store_name] = None
                st.rerun()
        
        with col3:
            # 删除店铺按钮
            if st.button("删除店铺", key=f"delete_store_{store_name}"):
                # 显示确认对话框
                if st.session_state.get(f"confirm_delete_{store_name}", False):
                    if remove_store_from_plan(store_name):
                        st.success(f"已删除 {store_name} 及其所有产品")
                        st.session_state[f"confirm_delete_{store_name}"] = False
                        st.rerun()
                else:
                    st.session_state[f"confirm_delete_{store_name}"] = True
                    st.rerun()
        
        # 显示删除确认
        if st.session_state.get(f"confirm_delete_{store_name}", False):
            with col1:
                st.warning(f"确认删除 {store_name} 下的所有产品吗？")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("确认删除", key=f"confirm_delete_btn_{store_name}"):
                    if remove_store_from_plan(store_name):
                        st.success(f"已删除 {store_name} 及其所有产品")
                        st.session_state[f"confirm_delete_{store_name}"] = False
                        st.rerun()
            with col_cancel:
                if st.button("取消", key=f"cancel_delete_btn_{store_name}"):
                    st.session_state[f"confirm_delete_{store_name}"] = False
                    st.rerun()
        
        # 显示试算配置窗口
        if st.session_state.show_plan_calculation_config.get(store_name, False):
            show_store_calculation_config(store_name, products)
            continue
        
        # 显示试算结果
        if st.session_state.plan_calculation_result.get(store_name):
            with st.expander(f"💰 {store_name} 试算结果", expanded=True):
                col_close, _ = st.columns([1, 3])
                with col_close:
                    if st.button(f"✕ 关闭试算", key=f"close_calc_{store_name}"):
                        st.session_state.plan_calculation_result[store_name] = None
                        st.rerun()
                
                display_store_calculation_results(store_name, products, st.session_state.plan_calculation_result[store_name])
        
        st.write("")  # 间距


def show_store_calculation_config(store_name: str, products: list):
    """显示店铺购买计划的试算配置窗口"""
    from discount_config import DISCOUNT_CONFIG
    
    st.subheader(f"💰 {store_name} 试算配置")
    
    # 初始化产品选择状态（默认全选）
    selection_key = f"product_selection_{store_name}"
    if selection_key not in st.session_state:
        st.session_state[selection_key] = {product['id']: True for product in products}
    
    # 显示产品清单和选择复选框
    st.write("**选择要试算的产品:**")
    for i, product in enumerate(products, 1):
        col1, col2 = st.columns([0.5, 3.5])
        with col1:
            selected = st.checkbox(
                "选择",
                value=st.session_state[selection_key].get(product['id'], True),
                key=f"product_select_{store_name}_{product['id']}",
                label_visibility="collapsed"
            )
            st.session_state[selection_key][product['id']] = selected
        with col2:
            st.write(f"{i}. {product['exact_model'] or product['product_model']} - {product['color']} - {product['size']} - {product['price_krw']:,}韩元")
    
    # 获取选中的产品
    selected_products = [p for p in products if st.session_state[selection_key].get(p['id'], True)]
    
    # 计算选中产品的总价
    total_krw = sum(product['price_krw'] for product in selected_products)
    
    st.divider()
    st.write(f"**已选产品数:** {len(selected_products)}/{len(products)}")
    st.write(f"**选中产品税前总价:** {total_krw:,}韩元")
    st.divider()
    
    # 商家选择（单选）
    st.write("**选择商家优惠:**")
    store_options = ["明洞乐天", "新世界", "旗舰店", "乐天/新世界奥莱", "现代百货"]
    selected_store = st.radio("商家选择", store_options, key=f"store_selection_{store_name}", label_visibility="collapsed")
    
    # 显示对应商家的优惠选项
    store_config = DISCOUNT_CONFIG[selected_store]
    st.write(f"*{store_config['description']}*")
    
    selected_discounts = []
    for option in store_config['options']:
        col1, col2 = st.columns([1, 4])
        with col1:
            selected = st.checkbox(option['name'], key=f"discount_plan_{store_name}_{option['name']}")
        with col2:
            with st.expander("ℹ️ 规则说明"):
                st.write(option['rule'])
        
        if selected:
            selected_discounts.append(option)
    
    # 一键试算按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 开始试算", key=f"calculate_plan_{store_name}"):
            # 检查是否有选中的产品
            if len(selected_products) == 0:
                st.error("❌ 请至少选择一个产品进行试算")
            else:
                # 修改逻辑：即使没有选择优惠也允许试算，此时只计算退税
                result = calculate_detailed_price(total_krw, selected_discounts)
                st.session_state.plan_calculation_result[store_name] = result
                st.session_state.show_plan_calculation_config[store_name] = False
                st.rerun()
    
    with col2:
        if st.button("← 返回购买计划", key=f"back_to_plan_{store_name}"):
            st.session_state.show_plan_calculation_config[store_name] = False
            st.rerun()


def display_store_calculation_results(store_name: str, products: list, result):
    """显示店铺购买计划的试算结果"""
    if not result:
        st.error("试算失败，请重试")
        return
    
    st.subheader("📊 试算结果")
    
    # 获取选中的产品
    selection_key = f"product_selection_{store_name}"
    selected_products = [p for p in products if st.session_state.get(selection_key, {}).get(p['id'], True)]
    
    # 显示产品清单
    st.write("**试算产品清单:**")
    for i, product in enumerate(selected_products, 1):
        st.write(f"{i}. {product['exact_model'] or product['product_model']} - {product['color']} - {product['size']}")
    
    st.divider()
    
    # 计算人民币价格
    cny_price = convert_krw_to_cny(result['final_payment'])
    
    # 计算国内总价和折扣率
    total_domestic_price, has_all_domestic_prices = calculate_store_domestic_total(selected_products)
    discount_rate = None
    if has_all_domestic_prices and total_domestic_price > 0:
        discount_rate = int((cny_price / total_domestic_price) * 100)
    
    # 显示计算步骤
    st.write("**详细计算过程:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("原始总价", f"{result['total_krw']:,.0f}韩元")
        st.metric("税前优惠", f"-{result['pre_tax_discount']:,.0f}韩元")
        st.metric("优惠后总价", f"{result['after_pre_tax']:,.0f}韩元")
        st.metric("退税额", f"-{result['tax_refund']:,.0f}韩元")
    
    with col2:
        st.metric("税后总价", f"{result['after_tax']:,.0f}韩元")
        
        # 显示商品券和积分的组合情况
        if result['gift_coupon'] > 0 and result['points_reward'] > 0:
            # 同时有商品券和积分
            st.metric("商品券优惠", f"-{result['gift_coupon']:,.0f}韩元")
            st.metric("积分赠送", f"-{result['points_reward']:,.0f}积分")
            st.metric("最终实付",
                      f"{result['final_payment']:,.0f}韩元/{cny_price:,.0f}人民币",
                      f"含{result['gift_coupon']:,.0f}韩元商品券和{result['points_reward']:,.0f}积分")
        elif result['gift_coupon'] > 0:
            # 只有商品券
            st.metric("商品券优惠", f"-{result['gift_coupon']:,.0f}韩元")
            st.metric("最终实付",
                      f"{result['final_payment']:,.0f}韩元/{cny_price:,.0f}人民币",
                      f"含{result['gift_coupon']:,.0f}韩元商品券")
        elif result['points_reward'] > 0:
            # 只有积分
            st.metric("积分赠送", f"-{result['points_reward']:,.0f}积分")
            st.metric("最终实付",
                      f"{result['final_payment']:,.0f}韩元/{cny_price:,.0f}人民币",
                      f"含{result['points_reward']:,.0f}积分")
        else:
            # 没有商品券也没有积分
            st.metric("商品券优惠", "0韩元")
            st.metric("积分赠送", "0积分")
            st.metric("最终实付", f"{result['final_payment']:,.0f}韩元/{cny_price:,.0f}人民币")
    
    # 显示国内价格对比和折扣率
    st.divider()
    st.write("**国内价格对比:**")
    if has_all_domestic_prices:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("国内总价", f"{total_domestic_price:,.0f}元")
        with col2:
            st.metric("最终实付", f"{cny_price:,.0f}元")
        with col3:
            if discount_rate is not None:
                st.metric("折扣率", f"{discount_rate}%", delta=f"{100-discount_rate}% 优惠")
    else:
        st.warning("⚠️ 部分产品缺少国内价格数据，无法计算折扣率")
    
    # 显示使用的优惠
    st.divider()
    st.write("**使用的优惠:**")
    for discount in result['selected_discounts']:
        st.write(f"✅ {discount}")

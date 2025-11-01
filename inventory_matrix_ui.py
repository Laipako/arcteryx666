import streamlit as st
import pandas as pd
import time
from inventory_check import (
    safe_batch_query,
    calculate_enhanced_inventory_stats,
    calculate_product_depth_stats,
    calculate_key_store_analysis,
    STORE_REGION_MAPPING
)
from filter_utils import apply_filters_and_sort, convert_to_excel
from favorites_manager import load_favorites
from purchase_plan_manager import add_to_plan, check_product_in_plan
from followed_stores_manager import get_followed_store_names
from calculation_utils import convert_krw_to_cny


def show_inventory_matrix_tab():
    """显示库存矩阵标签页"""
    st.header("📊 库存矩阵")

    # 初始化session_state
    if "inventory_matrix_queried" not in st.session_state:
        st.session_state.inventory_matrix_queried = False
    if "inventory_matrix_data" not in st.session_state:
        st.session_state.inventory_matrix_data = None
    if "stock_filter_matrix" not in st.session_state:
        st.session_state.stock_filter_matrix = "全部"
    if "region_filter_matrix" not in st.session_state:
        st.session_state.region_filter_matrix = "全部"
    if "sort_option_matrix" not in st.session_state:
        st.session_state.sort_option_matrix = "默认"
    if "query_stats" not in st.session_state:
        st.session_state.query_stats = None

    # 加载收藏产品列表
    favorites = load_favorites()

    if not favorites:
        st.info("📌 提示：暂无收藏产品。请先在【收藏产品】标签页添加收藏产品。")
        return

    st.subheader("📊 库存矩阵查询")
    
    # 查询按钮
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 查全部库存", key="matrix_check_all", use_container_width=True):
            if not favorites:
                st.warning("收藏列表为空")
            else:
                # 显示查询进度
                progress_text = st.empty()
                progress_text.info(f"开始查询所有 {len(favorites)} 个产品的库存...")

                # 实际执行查询（查询所有收藏产品）
                inventory_matrix, query_stats = safe_batch_query(favorites)

                if inventory_matrix:
                    st.session_state.inventory_matrix_queried = True
                    st.session_state.inventory_matrix_data = inventory_matrix
                    st.session_state.query_stats = query_stats
                    
                    # 显示成功/失败统计
                    success_count = query_stats.get("success", 0)
                    failed_count = query_stats.get("failed", 0)
                    success_rate = query_stats.get("success_rate", 0)
                    duration = query_stats.get("duration", 0)
                    
                    progress_text.success(
                        f"查询完成！成功: {success_count}个 ✅ | 失败: {failed_count}个 ❌ | "
                        f"成功率: {success_rate}% | 耗时: {duration}秒 | 共 {len(inventory_matrix)} 个店铺"
                    )
                    st.rerun()
                else:
                    st.error("库存查询失败，请检查网络连接或稍后重试")

    with col2:
        if st.session_state.inventory_matrix_queried and st.button("🔄 重新查询", key="matrix_requery", use_container_width=True):
            st.session_state.inventory_matrix_queried = False
            st.session_state.inventory_matrix_data = None
            st.session_state.query_stats = None
            st.session_state.stock_filter_matrix = "全部"
            st.session_state.region_filter_matrix = "全部"
            st.session_state.sort_option_matrix = "默认"
            st.rerun()

    st.write("")

    # 显示查询统计信息（如果查询已完成）
    if st.session_state.inventory_matrix_queried and st.session_state.query_stats:
        query_stats = st.session_state.query_stats
        success_count = query_stats.get("success", 0)
        failed_count = query_stats.get("failed", 0)
        success_rate = query_stats.get("success_rate", 0)
        duration = query_stats.get("duration", 0)
        failed_details = query_stats.get("failed_details", [])
        
        # 显示统计信息卡片
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        with stats_col1:
            st.metric("✅ 成功", f"{success_count}个")
        with stats_col2:
            st.metric("❌ 失败", f"{failed_count}个")
        with stats_col3:
            st.metric("📊 成功率", f"{success_rate}%")
        with stats_col4:
            st.metric("⏱️ 耗时", f"{duration}秒")
        
        # 如果有失败的产品，显示失败详情
        if failed_details:
            with st.expander("📋 查看失败产品详情"):
                for product_id, reason in failed_details:
                    st.write(f"• 产品 {product_id}: {reason}")

    # 显示库存矩阵（基于session_state判断）
    if st.session_state.inventory_matrix_queried and st.session_state.inventory_matrix_data:
        st.info("📊 当前显示所有收藏产品的库存矩阵")

        # 获取缓存的库存矩阵
        inventory_matrix = st.session_state.inventory_matrix_data

        if inventory_matrix:
            # 使用新的统计函数
            stats = calculate_enhanced_inventory_stats(inventory_matrix)

            # 显示实时库存状态分布
            st.subheader("📊 库存状态分布")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ 高库存店铺",
                          f"{stats['stock_status']['高库存店铺']['count']}家",
                          f"{stats['stock_status']['高库存店铺']['percentage']}%")
            with col2:
                st.metric("⚠️ 低库存店铺",
                          f"{stats['stock_status']['低库存店铺']['count']}家",
                          f"{stats['stock_status']['低库存店铺']['percentage']}%")
            with col3:
                st.metric("❌ 无库存店铺",
                          f"{stats['stock_status']['无库存店铺']['count']}家",
                          f"{stats['stock_status']['无库存店铺']['percentage']}%")

            # 显示区域库存热力图
            st.subheader("🗺️ 区域库存分布")
            for region, data in stats['region_heatmap'].items():
                st.write(f"**{region}**: {data['count']}家店铺 ({data['percentage']}%) - {data['inventory']}件库存")

            # 先显示重点关注店铺分析
            st.subheader("🏪🏪 关注店铺库存分析")

            # 获取用户关注的店铺列表
            followed_stores = get_followed_store_names()
            
            # 如果用户没有关注任何店铺，提示用户
            if not followed_stores:
                st.info("💡 提示：在\"关注店铺\"标签页中添加关注店铺，以在此显示库存分析")
                # 使用默认的重点关注店铺进行分析
                key_store_analysis = calculate_key_store_analysis(favorites, inventory_matrix)
            else:
                # 使用用户关注的店铺进行分析
                key_store_analysis = calculate_key_store_analysis(favorites, inventory_matrix, key_stores=followed_stores)

            # 显示每个重点关注店铺的库存情况
            for store_name, products in key_store_analysis.items():
                if products:
                    # 创建两列布局：店铺名称在左，库存详情在右（可折叠）
                    col1, col2 = st.columns([1, 3])

                    with col1:
                        # 店铺名称始终显示（不折叠）
                        st.write(f"**{store_name}**")

                    with col2:
                        # 库存详情可折叠
                        with st.expander(f"查看库存详情", expanded=False):
                            # 显示所有产品的库存状态
                            for product in products:
                                st.write(f"• {product['display_text']}")
                                
                                # 只有有库存的产品才能加入购买计划
                                if product['stock_count'] > 0:
                                    # 从product_key中解析product_model、color、size
                                    product_key_parts = product['product_key'].rsplit(' ', 2)
                                    if len(product_key_parts) == 3:
                                        product_model, color, size = product_key_parts
                                        
                                        # 从favorites中查找对应的favorite对象
                                        favorite = None
                                        for fav in favorites:
                                            if (fav['product_model'] == product_model and 
                                                fav['color'] == color and 
                                                fav['size'] == size):
                                                favorite = fav
                                                break
                                        
                                        if favorite:
                                            if st.button("加入购买计划", key=f"add_plan_matrix_{store_name}_{product_model}_{color}_{size}"):
                                                # 准备产品信息
                                                product_info = {
                                                    "product_model": favorite['product_model'],
                                                    "exact_model": favorite.get('exact_model', ''),
                                                    "color": favorite['color'],
                                                    "size": favorite['size'],
                                                    "price_krw": int(favorite['price']),
                                                    "year_info": favorite.get('year_info', ''),
                                                    "domestic_price_cny": favorite.get('china_price_cny', None)
                                                }
                                                
                                                if add_to_plan(store_name, product_info):
                                                    st.success(f"✅ 已添加到 {store_name} 的购买计划")
                                                    st.rerun()
                                                else:
                                                    st.error(f"❌ 添加到 {store_name} 的购买计划失败")

                else:
                    # 如果店铺没有相关产品数据
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.write(f"**{store_name}**")
                    with col2:
                        st.write("该店铺无相关产品库存数据")

                st.divider()

            st.subheader("📦📦 产品库存深度分析")

            product_depth_stats = calculate_product_depth_stats(favorites, inventory_matrix)

            for product_key, stats in product_depth_stats.items():
                with st.expander(f"{product_key} 库存分析"):
                    # 基础统计
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📦 总库存", f"{stats['total_inventory']}件")
                    with col2:
                        st.metric("🏪 有库存店铺", f"{stats['stores_with_stock']}家")

                    # 详细区域分布
                    st.write("📍 区域分布:")
                    for region, region_data in stats['region_distribution'].items():
                        if region_data['total'] > 0:
                            # 显示区域汇总
                            st.write(f"**{region}**: {region_data['total']}件")

                            # 显示具体店铺分布（缩进显示）
                            for store_info in region_data['stores']:
                                st.write(f"  - {store_info['store_name']}: {store_info['stock']}件")

            # 筛选区域
            st.subheader("筛选选项")
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 1])

            with filter_col1:
                stock_filter = st.selectbox(
                    "库存状态",
                    ["全部", "有库存", "无库存"],
                    index=["全部", "有库存", "无库存"].index(st.session_state.stock_filter_matrix),
                    key="stock_filter_matrix_select"
                )

            with filter_col2:
                region_filter = st.selectbox(
                    "店铺区域",
                    ["全部", "首尔城区", "京畿道地区", "釜山", "大邱"],
                    index=["全部", "首尔城区", "京畿道地区", "釜山", "大邱"].index(st.session_state.region_filter_matrix),
                    key="region_filter_matrix_select"
                )

            with filter_col3:
                sort_option = st.selectbox(
                    "排序方式",
                    ["默认", "库存总量降序", "库存总量升序"],
                    index=["默认", "库存总量降序", "库存总量升序"].index(st.session_state.sort_option_matrix),
                    key="sort_option_matrix_select"
                )

            with filter_col4:
                st.write("")  # 空行用于对齐
                if st.button("一键清除筛选", key="clear_filters_matrix"):
                    st.session_state.stock_filter_matrix = "全部"
                    st.session_state.region_filter_matrix = "全部"
                    st.session_state.sort_option_matrix = "默认"
                    st.rerun()

            # 更新session状态
            st.session_state.stock_filter_matrix = stock_filter
            st.session_state.region_filter_matrix = region_filter
            st.session_state.sort_option_matrix = sort_option

            # 应用筛选和排序
            filtered_matrix = apply_filters_and_sort(
                inventory_matrix, stock_filter, region_filter, sort_option
            )

            if filtered_matrix:
                # 转换为DataFrame显示
                df = pd.DataFrame.from_dict(filtered_matrix, orient='index')

                # 添加表格样式
                st.markdown("""
                <style>
                .dataframe {
                    font-size: 11px;
                }
                .dataframe th {
                    font-size: 11px;
                    white-space: nowrap;
                }
                .dataframe td {
                    font-size: 11px;
                    white-space: nowrap;
                }
                </style>
                """, unsafe_allow_html=True)

                st.dataframe(df, use_container_width=True, height=500)

                # Excel下载按钮 - 转换DataFrame为JSON字符串以支持缓存
                import json
                df_dict = df.to_dict(orient='index')
                df_json_str = json.dumps(df_dict, default=str)
                excel_data = convert_to_excel(df_json_str)
                st.download_button(
                    label="下载库存数据(Excel)",
                    data=excel_data,
                    file_name="inventory_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("没有找到符合筛选条件的店铺")
        else:
            st.error("无法生成库存矩阵")

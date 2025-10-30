# followed_stores_ui.py
import streamlit as st
from followed_stores_manager import (
    load_followed_stores,
    add_followed_store,
    remove_followed_store,
    get_followed_store_names,
    clear_all_followed_stores
)
from inventory_check import STORE_REGION_MAPPING


@st.cache_data(ttl=300)
def get_all_stores():
    """获取所有可用的店铺列表（缓存5分钟）"""
    return sorted(STORE_REGION_MAPPING.keys())


def get_followed_stores_cached():
    """获取已关注的店铺（使用session_state缓存）"""
    if "followed_stores_cache" not in st.session_state:
        st.session_state.followed_stores_cache = load_followed_stores()
    return st.session_state.followed_stores_cache


def refresh_followed_stores_cache():
    """刷新关注店铺的缓存"""
    st.session_state.followed_stores_cache = load_followed_stores()


def show_followed_stores_tab():
    """显示关注店铺标签页"""
    st.header("⭐ 关注店铺")
    
    # 初始化session_state
    if "show_store_input" not in st.session_state:
        st.session_state.show_store_input = False
    
    # 获取所有可用的店铺列表（缓存）
    all_stores = get_all_stores()
    
    # 加载已关注的店铺（使用缓存）
    followed_stores = get_followed_stores_cached()
    
    # 标题和刷新按钮
    col_title, col_refresh = st.columns([0.9, 0.1])
    with col_title:
        st.subheader(f"已关注店铺 ({len(followed_stores)}家)")
    with col_refresh:
        if st.button("🔄", key="refresh_followed_btn", help="刷新已关注店铺列表"):
            refresh_followed_stores_cache()
            st.rerun()
    
    if followed_stores:
        # 显示已关注的店铺列表
        for idx, store in enumerate(followed_stores):
            col1, col2, col3 = st.columns([3, 1, 0.5])
            
            with col1:
                st.write(f"🏪 {store['store_name']}")
            
            with col2:
                st.empty()  # 占位符
            
            with col3:
                # 删除按钮
                if st.button("🗑️", key=f"delete_store_{store['id']}", help="取消关注"):
                    if remove_followed_store(store['id']):
                        refresh_followed_stores_cache()
                        st.toast("已取消关注", icon="✅")
                    else:
                        st.error("删除失败")
    else:
        st.info("暂无关注的店铺，请添加一些店铺")
    
    st.divider()
    
    # 添加新店铺区域
    st.subheader("添加关注店铺")
    
    # 显示/隐藏输入框的按钮
    if not st.session_state.show_store_input:
        if st.button("➕ 添加店铺", use_container_width=True):
            st.session_state.show_store_input = True
            st.rerun()
    else:
        # 店铺选择下拉框
        selected_store = st.selectbox(
            "选择店铺",
            all_stores,
            key="store_select_dropdown"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✓ 确认添加", use_container_width=True):
                if selected_store:
                    success, message = add_followed_store(selected_store)
                    if success:
                        refresh_followed_stores_cache()
                        st.session_state.show_store_input = False
                        st.toast(message, icon="✅")
                    else:
                        st.warning(message)
        
        with col2:
            if st.button("✕ 取消", use_container_width=True):
                st.session_state.show_store_input = False
                st.rerun()
    
    st.divider()
    
    # 批量操作
    st.subheader("批量操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 刷新列表", use_container_width=True):
            refresh_followed_stores_cache()
            st.toast("已刷新关注店铺列表", icon="✅")
    
    with col2:
        if st.button("🗑️ 清空所有", use_container_width=True):
            if st.session_state.get(f"confirm_clear_all", False):
                if clear_all_followed_stores():
                    refresh_followed_stores_cache()
                    st.session_state[f"confirm_clear_all"] = False
                    st.toast("已清空所有关注店铺", icon="✅")
            else:
                st.session_state[f"confirm_clear_all"] = True
                st.rerun()
    
    # 显示清空确认
    if st.session_state.get(f"confirm_clear_all", False):
        st.warning("⚠️ 确认要清空所有关注店铺吗？此操作不可撤销！")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("🔴 确认清空", use_container_width=True, key="confirm_clear_btn"):
                if clear_all_followed_stores():
                    refresh_followed_stores_cache()
                    st.session_state[f"confirm_clear_all"] = False
                    st.toast("已清空所有关注店铺", icon="✅")
        with col_cancel:
            if st.button("❌ 取消", use_container_width=True, key="cancel_clear_btn"):
                st.session_state[f"confirm_clear_all"] = False
                st.rerun()

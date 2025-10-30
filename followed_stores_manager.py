# followed_stores_manager.py
import streamlit as st
from supabase_client import supabase_manager


def load_followed_stores():
    """从 Supabase 加载所有关注的店铺"""
    try:
        client = supabase_manager.get_client()
        response = client.table('followed_stores').select('*').order('created_at', desc=False).execute()
        
        stores = response.data if response.data else []
        return stores
    
    except Exception as e:
        print(f"❌ 从Supabase加载关注店铺失败: {e}")
        return []


def add_followed_store(store_name: str) -> tuple:
    """添加关注的店铺到 Supabase"""
    try:
        # 检查是否重复
        existing_stores = load_followed_stores()
        for store in existing_stores:
            if store['store_name'] == store_name:
                return False, "该店铺已在关注列表中"
        
        # 准备插入数据
        store_data = {
            "store_name": store_name
        }
        
        # 插入数据
        client = supabase_manager.get_client()
        response = client.table('followed_stores').insert(store_data).execute()
        
        if response.data:
            return True, f"成功关注 {store_name}"
        else:
            return False, "添加到数据库失败"
    
    except Exception as e:
        print(f"❌ 添加关注店铺失败: {e}")
        return False, f"添加关注店铺失败: {str(e)}"


def remove_followed_store(store_id: int) -> bool:
    """从关注列表中删除店铺"""
    try:
        client = supabase_manager.get_client()
        client.table('followed_stores').delete().eq('id', store_id).execute()
        return True
    
    except Exception as e:
        print(f"❌ 删除关注店铺失败: {e}")
        return False


def get_followed_store_names() -> list:
    """获取所有关注的店铺名称列表"""
    stores = load_followed_stores()
    return [store['store_name'] for store in stores]


def clear_all_followed_stores() -> bool:
    """清空所有关注的店铺"""
    try:
        client = supabase_manager.get_client()
        client.table('followed_stores').delete().neq('id', 0).execute()
        return True
    
    except Exception as e:
        print(f"❌ 清空关注店铺失败: {e}")
        return False

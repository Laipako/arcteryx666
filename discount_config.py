# 新增文件：discount_config.py
DISCOUNT_CONFIG = {
    "明洞乐天": {
        "description": "明洞乐天免税店专属优惠",
        "options": [
            {
                "name": "5%折扣券",
                "type": "pre_tax_percent",
                "rate": 0.05,
                "rule": "总价5%折扣（税前优惠）"
            },
            {
                "name": "新会员5%折扣",
                "type": "pre_tax_percent",
                "rate": 0.05,
                "rule": "需韩国电话注册新会员，总价5%折扣（税前优惠）"
            },
            {
                "name": "银联满10万减7500",
                "type": "pre_tax_fixed",
                "threshold": 100000,
                "amount": 7500,
                "once_only": True,
                "rule": "单笔支付满10万韩元减7500（仅限一次）"
            }
        ]
    },
    "新世界": {
        "description": "明洞/江南/釜山新世界优惠",
        "options": [
            {
                "name": "会员卡5%折扣",
                "type": "pre_tax_percent",
                "rate": 0.05,
                "rule": "需出示会员卡，总价5%折扣（税前优惠）"
            },
            {
                "name": "新会员5%折扣",
                "type": "pre_tax_percent",
                "rate": 0.05,
                "rule": "需韩国电话注册新会员，总价5%折扣（税前优惠）"
            },
            {
                "name": "银联阶梯立减",
                "type": "pre_tax_tiered",
                "tiers": [
                    {"threshold": 550000, "amount": 35000},
                    {"threshold": 1000000, "amount": 100000},
                    {"threshold": 10000000, "amount": 1000000}
                ],
                "once_only": True,
                "rule": "单笔支付消费满5.5/10/100万韩元分别立减0.35/1/10万韩元（仅限一次）"
            },
            {
                "name": "银联阶梯赠券",
                "type": "post_tax_tiered",
                "tiers": [
                    {"threshold": 200000, "amount": 10000},
                    {"threshold": 400000, "amount": 20000},
                    {"threshold": 600000, "amount": 30000}
                ],
                "rule": "税前优惠后总价满20/40/60万赠1/2/3万商品券"
            }
        ]
    },
    "旗舰店": {
        "description": "旗舰店优惠",
        "options": [
            {
                "name": "新会员5%折扣",
                "type": "pre_tax_percent",
                "rate": 0.05,
                "rule": "需韩国电话注册新会员，总价5%折扣（税前优惠）"
            }
        ]
    },
    "乐天/新世界奥莱": {
        "description": "奥特莱斯专属优惠",
        "options": [
            {
                "name": "新会员5%折扣",
                "type": "pre_tax_percent",
                "rate": 0.05,
                "rule": "需韩国电话注册新会员，总价5%折扣（税前优惠）"
            },
            {
                "name": "银联满5万10%折扣",
                "type": "pre_tax_capped",
                "threshold": 50000,
                "rate": 0.10,
                "cap": 10000,
                "rule": "银联消费满5万韩元享10%折扣，最高减1万韩元"
            }
        ]
    },
    "现代百货": {
        "description": "现代百货专属优惠",
        "options": [
            {
                "name": "新会员5%折扣",
                "type": "pre_tax_percent",
                "rate": 0.05,
                "rule": "需韩国电话注册新会员，总价5%折扣（税前优惠）"
            },
            {
                "name": "7%积分赠送",
                "type": "post_tax_tiered_points",
                "tiers": [
                    {"threshold": 500000, "amount": 35000},
                    {"threshold": 700000, "amount": 49000},
                    {"threshold": 1000000, "amount": 70000},
                    {"threshold": 3000000, "amount": 210000},
                    {"threshold": 5000000, "amount": 350000}
                ],
                "rule": "税前优惠后总价满50/70/100/300/500万赠3.5/4.9/7/21/35万积分"
            },
            {
                "name": "商品券赠送",
                "type": "post_tax_tiered",
                "tiers": [
                    {"threshold": 500000, "amount": 30000},
                    {"threshold": 1000000, "amount": 70000},
                    {"threshold": 2000000, "amount": 150000},
                    {"threshold": 3000000, "amount": 230000},
                    {"threshold": 5000000, "amount": 400000}
                ],
                "rule": "税前优惠后总价满50/100/200/300/500万赠3/7/15/23/40万商品券"
            },
            {
                "name": "汝矣岛店商品券赠送",
                "type": "post_tax_tiered",
                "tiers": [
                    {"threshold": 500000, "amount": 50000},
                    {"threshold": 700000, "amount": 70000},
                    {"threshold": 1000000, "amount": 100000},
                    {"threshold": 3000000, "amount": 300000},
                    {"threshold": 5000000, "amount": 500000},
                    {"threshold": 10000000, "amount": 1000000}
                ],
                "rule": "税前优惠后总价满50/70/100/300/500/1000万赠5/7/10/30/50/100万商品券"
            },
            {
                "name": "本店/贸易中心店/新村板桥店商品券赠送",
                "type": "post_tax_tiered",
                "tiers": [
                    {"threshold": 500000, "amount": 25000},
                    {"threshold": 700000, "amount": 35000},
                    {"threshold": 1000000, "amount": 50000},
                    {"threshold": 3000000, "amount": 150000},
                    {"threshold": 5000000, "amount": 250000},
                    {"threshold": 10000000, "amount": 500000}
                ],
                "rule": "税前优惠后总价满50/70/100/300/500/1000万赠2.5/3.5/5/15/25/50万商品券"
            }
        ]
    },
    "汝矣岛店": {
        "description": "汝矣岛店专属优惠",
        "options": [
            {
                "name": "商品券赠送",
                "type": "post_tax_tiered",
                "tiers": [
                    {"threshold": 500000, "amount": 50000},
                    {"threshold": 700000, "amount": 70000},
                    {"threshold": 1000000, "amount": 100000},
                    {"threshold": 3000000, "amount": 300000},
                    {"threshold": 5000000, "amount": 500000},
                    {"threshold": 10000000, "amount": 1000000}
                ],
                "rule": "税前优惠后总价满50/70/100/300/500/1000万赠5/7/10/30/50/100万商品券"
            }
        ]
    },
    "本店/贸易中心店/新村板桥店": {
        "description": "本店/贸易中心店/新村板桥店专属优惠",
        "options": [
            {
                "name": "商品券赠送",
                "type": "post_tax_tiered",
                "tiers": [
                    {"threshold": 500000, "amount": 25000},
                    {"threshold": 700000, "amount": 35000},
                    {"threshold": 1000000, "amount": 50000},
                    {"threshold": 3000000, "amount": 150000},
                    {"threshold": 5000000, "amount": 250000},
                    {"threshold": 10000000, "amount": 500000}
                ],
                "rule": "税前优惠后总价满50/70/100/300/500/1000万赠2.5/3.5/5/15/25/50万商品券"
            }
        ]
    }
}
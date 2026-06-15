package com.lzz.common.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class QueryContent {
    private String queryColumnName = "gyy_mall_title";

    // 查询关键词
    private String queryString = "*";

    // 查询所属类别 id
    private Integer queryCategoryID;

    // 查询所诉地区 id
    private Integer queryAreaID;

    // 查询会员内容
    private Integer vip;

    // 设置价格升序降序
    private String priceSort = "0";

    // 当前所在页
    private Integer page = 1;

    // 查询数据表名称
    private String queryTable = "mall";

    // 价格区间
    private Double[] priceSection = {0.0, 0.0, 0.0};
}

package com.lzz.gyyMall.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.solr.client.solrj.beans.Field;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GyyMall {
    // ID
    @Field("id")
    private String itemid;

    // 商品类别 ID
    @Field("gyy_catid")
    private Integer catid;

    // 所属地区 ID
    @Field("gyy_parentid")
    private Integer parentid;

    // 商品名称
    @Field("gyy_title")
    private String title;

    // 商品价格
    @Field("gyy_price")
    private Float price;

    // 生产公司
    @Field("gyy_company")
    private String company;

    // 生产公司 id
    @Field("gyy_company_id")
    private Integer companyID;

    // 所属地区
    @Field("gyy_areaname")
    private String areaname;

    // 是否为 vip
    @Field("gyy_vip")
    private Integer vip;

    // 商品图片
    @Field("gyy_pic")
    private String picture;
}

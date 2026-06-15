package com.lzz.gyyCompany.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.solr.client.solrj.beans.Field;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GyyCompany {
    // 主键id
    @Field("id")
    private String id;

    // company
    @Field("gyy_company")
    private String company;

    // business
    @Field("gyy_company_business")
    private String business;
}

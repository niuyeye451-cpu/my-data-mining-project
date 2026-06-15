package com.lzz.gyyArea.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.solr.client.solrj.beans.Field;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GyyArea {
    // ID
    @Field("id")
    private String areaid;

    // 所属地区
    @Field("gyy_areaname")
    private String areaname;
}

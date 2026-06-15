package com.lzz.gyyArea.service;

import com.lzz.common.pojo.GyyResult;
import com.lzz.gyyArea.pojo.GyyArea;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class GetArea {
    private final String baseSolrUrl = "http://localhost:8983/solr/core_area";
    HttpSolrClient client = new HttpSolrClient.Builder(baseSolrUrl).build();

    public GyyResult getArea() throws Exception{
        long startTime = System.currentTimeMillis();
        GyyResult gyyResult = new GyyResult();

        String query = "*:*";
        SolrQuery solrQuery = new SolrQuery(query);

        QueryResponse queryResponse = client.query(solrQuery);

        int QTime = queryResponse.getQTime();
        long totalCount = queryResponse.getResults().getNumFound();
        System.out.println("总数据数目" + totalCount +"\t" + "用时：" + QTime);

        List<GyyArea> areaList = queryResponse.getBeans(GyyArea.class);

        // 封装查询到的结果集
        gyyResult.setData(areaList);

        // 查询结果条数
        gyyResult.setRecordCount(totalCount);

        // 查询结果条数
        gyyResult.setRecordCount(totalCount);

        // 总页数
        gyyResult.setPageCount((long) 1);

        // 消息
        gyyResult.setMsg("成功获取到数据");
        long endTime = System.currentTimeMillis();
        System.out.println("========= 消耗时间为 =========" + (endTime - startTime) + "ms\n");
        return gyyResult;
    }
}

package com.lzz.gyyCompany.service;

import com.lzz.common.pojo.GyyResult;
import com.lzz.common.pojo.QueryContent;
import com.lzz.gyyMall.pojo.GyyMall;
import com.lzz.common.service.LzzSearch;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class CompanySearch implements LzzSearch {
    // 每页显示 20 条查询数据
    public final static Integer PAGE_SIZE = 10;

    private final String baseSolrUrl = "http://localhost:8983/solr/core_company";
    HttpSolrClient client = new HttpSolrClient.Builder(baseSolrUrl).build();

    @Override
    public GyyResult query(QueryContent queryContent) throws Exception{
        long startTime = System.currentTimeMillis();
        System.out.println(
                "检索域：" + queryContent.getQueryColumnName() + "\n" +
                "关键词：" + queryContent.getQueryString() + "\n" +
                "页数：" + queryContent.getPage() + "\n"

        );
        GyyResult gyyResult = new GyyResult();

        String query = queryContent.getQueryColumnName() + ":" + queryContent.getQueryString();
        SolrQuery solrQuery = new SolrQuery(query);

        QueryResponse queryResponse = client.query(solrQuery);

        int QTime = queryResponse.getQTime();
        long totalCount = queryResponse.getResults().getNumFound();
        System.out.println("总数据数目" + totalCount +"\t" + "用时：" + QTime);

        List<GyyMall> mallList = queryResponse.getBeans(GyyMall.class);

        // 封装查询到的结果集
        gyyResult.setData(mallList);

        // 查询结果条数
        gyyResult.setRecordCount(totalCount);

        // 消息
        gyyResult.setMsg("成功获取到数据");
        long endTime = System.currentTimeMillis();
        System.out.println("========= 消耗时间为 =========" + (endTime - startTime) + "ms\n");
        return gyyResult;
    }
}

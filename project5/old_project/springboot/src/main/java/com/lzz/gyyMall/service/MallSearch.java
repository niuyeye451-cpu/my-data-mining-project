package com.lzz.gyyMall.service;

import com.lzz.common.pojo.GyyResult;
import com.lzz.common.pojo.QueryContent;
import com.lzz.gyyMall.pojo.GyyMall;
import com.lzz.common.service.LzzSearch;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.*;

@Service
public class MallSearch implements LzzSearch {
    // 每页显示 10 条查询数据
    public final static Integer PAGE_SIZE = 10;

    @Autowired
    SolrClient solrClient;

//    private String baseSolrUrl = "http://localhost:8081/solr/core_demo";
//    HttpSolrClient client = new HttpSolrClient.Builder(baseSolrUrl).build();

    @Override
    public GyyResult query(QueryContent queryContent) throws Exception{
        if(Objects.equals(queryContent.getQueryString(), "")){
            queryContent.setQueryString("*");
        }
        System.out.println(
                "检索域：" + queryContent.getQueryColumnName() + "\n" +
                "关键词：" + queryContent.getQueryString() + "\n" +
                "类别id：" + queryContent.getQueryCategoryID() + "\n" +
                "地区id：" + queryContent.getQueryAreaID() + "\n" +
                "是否查询vip：" + (queryContent.getVip() == 0 ? "否":"是") + "\n" +
                "排序方法：" + (queryContent.getPriceSort().equals("0") ? "默认排序":"价格排序") + "\n" +
                "排序规则：" + queryContent.getPriceSort() + "\n" +
                "价格区间：" + (queryContent.getPriceSection()[0] == 0 ?
                        "无": ("[" + queryContent.getPriceSection()[1] + "," +
                        queryContent.getPriceSection()[2] + "]")) + "\n" +
                "页数：" + queryContent.getPage() + "\n"

        );
        long startTime = System.currentTimeMillis();

        GyyResult gyyResult = new GyyResult();

        // 设置默认检索域后则不需要 "*:*" 的形式
//        String query = queryContent.getQueryColumnName() + ":" + queryContent.getQueryString();
        String query = queryContent.getQueryString();
        SolrQuery solrQuery = new SolrQuery(query);

        // 设置默认域为 gyy_mall_title
        solrQuery.set("df", "gyy_title");

        // 设置价格的查询区间
        if (queryContent.getPriceSection()[0] != 0) {
            solrQuery.addFilterQuery("gyy_price:[" + queryContent.getPriceSection()[1] + " TO " + queryContent.getPriceSection()[2] + "]");
        }

        // 设置多条件查询
        // 查询具体的 areaid 对应的结果
        if(queryContent.getQueryAreaID() != 0){
            String filter = "gyy_parentid:" + queryContent.getQueryAreaID();
            solrQuery.addFilterQuery(filter);
        }

        // 查询具体的 catid 对应的结果
        if(queryContent.getQueryCategoryID() != 0){
            String filter = "gyy_catid:" + queryContent.getQueryCategoryID();
            solrQuery.addFilterQuery(filter);
        }

        // 查询会员结果
        if(queryContent.getVip() != 0){
            String filter = "gyy_vip:1 or gyy_vip:2 or gyy_vip:3";
            solrQuery.addFilterQuery(filter);
        }

        QueryResponse queryResponse = solrClient.query(solrQuery);

        int QTime = queryResponse.getQTime();
        long totalCount = queryResponse.getResults().getNumFound();
        System.out.println("总数据数目" + totalCount +"\t" + "用时：" + QTime);


        try{
            List<GyyMall> mallList =new ArrayList<>();
            // 价格升序、降序
            if(!Objects.equals(queryContent.getPriceSort(), "0")){
                if(Objects.equals(queryContent.getPriceSort(), "desc")) {
                    solrQuery.addSort("gyy_price", SolrQuery.ORDER.desc);
                }
                else{
                    solrQuery.addSort("gyy_price", SolrQuery.ORDER.asc);
                }
                solrQuery.setStart((queryContent.getPage() - 1) * PAGE_SIZE);
                solrQuery.setRows((long) queryContent.getPage() * PAGE_SIZE > totalCount ?
                        (int) (totalCount - (queryContent.getPage() - 1) * PAGE_SIZE) : PAGE_SIZE);

                queryResponse = solrClient.query(solrQuery);
                mallList = queryResponse.getBeans(GyyMall.class);

                gyyResult.setData(mallList);

                // 查询结果条数
                gyyResult.setRecordCount(totalCount);

                // 总页数
                gyyResult.setPageCount(totalCount/PAGE_SIZE);
            }
            else{
                try{
                    mallList = reSort(PAGE_SIZE, queryContent.getPage(),"100", solrClient, solrQuery);

                    long total = mallList.size() + queryResponse.getResults().getNumFound();
                    if(queryContent.getPage() * PAGE_SIZE > mallList.size()){
                        int count = queryContent.getPage() * PAGE_SIZE - mallList.size();
                        if(count > PAGE_SIZE){
                            solrQuery.setStart(count);
                            solrQuery.setRows(PAGE_SIZE);
                            queryResponse = solrClient.query(solrQuery);
                            mallList = queryResponse.getBeans(GyyMall.class);
                        }
                        else{
                            solrQuery.setStart(0);
                            solrQuery.setRows(count);
                            queryResponse = solrClient.query(solrQuery);
                            mallList.addAll(queryResponse.getBeans(GyyMall.class));// 封装查询到的结果集
                        }
                    }

                    gyyResult.setData(mallList);

                    // 查询结果条数
                    gyyResult.setRecordCount(total);

                    // 总页数
                    gyyResult.setPageCount(total/PAGE_SIZE);


                }
                catch (Exception e){
                    System.out.println(e);
                }
            }

            // 当前所在页
            gyyResult.setCurPage(queryContent.getPage());

            // 消息
            gyyResult.setMsg("成功获取到数据");

        }
        catch (Exception e){
            gyyResult.setMsg("未找到相关内容");
        }
        long endTime = System.currentTimeMillis();
        System.out.println("========= 消耗时间为 =========" + (endTime - startTime) + "ms\n");
        return gyyResult;
    }

    public static List<GyyMall> reSort(Integer PAGE_SIZE, Integer currentPage, String companyID, SolrClient solrClient, SolrQuery solrQuery) throws SolrServerException, IOException {
        // 根据用户所属公司 id 获取与该公司业务类似的其他公司的 id 列表
        HttpSolrClient client = new HttpSolrClient.Builder("http://localhost:8983/solr/core_company_relative").build();
        String query = "id:" + companyID;
        SolrQuery solrQueryRelative = new SolrQuery(query);

        QueryResponse queryResponse1 = client.query(solrQueryRelative);
        String relative = queryResponse1.getResults().get(0).get("gyy_company_relative").toString();
        String[] relativeId = relative.replace("[", "").replace("]", "").split(",");

        List<String> relativeIdList = new ArrayList<>(Arrays.asList(relativeId));
//        System.out.println(relativeIdList);
        String filter = "";

        for(int i = 0; i < relativeIdList.size(); i++){
            if(i < relativeIdList.size() - 1){
                filter = filter + "gyy_company_id:" + relativeIdList.get(i) + " or ";
            }
            else{
                filter = filter + "gyy_company_id:" + relativeIdList.get(i);
            }
        }

        solrQuery.addFilterQuery(filter);

        QueryResponse queryResponseRelative = solrClient.query(solrQuery);
        int QTime = queryResponseRelative.getQTime();
        long totalCountRelative = queryResponseRelative.getResults().getNumFound();
        System.out.println("总数据数目" + totalCountRelative +"\t" + "用时：" + QTime);

        if(totalCountRelative < PAGE_SIZE){
            solrQuery.setStart(0);
            solrQuery.setRows((int)totalCountRelative);
        }
        else if(totalCountRelative > (long) currentPage * PAGE_SIZE){
            solrQuery.setStart((currentPage - 1) * PAGE_SIZE);
            solrQuery.setRows(PAGE_SIZE);
        }

        List<GyyMall> relativeMall = queryResponseRelative.getBeans(GyyMall.class);
        System.out.println("relativeMall.size:" + relativeMall.size());
        solrQuery.removeFilterQuery(filter);

        return relativeMall;
    }
}

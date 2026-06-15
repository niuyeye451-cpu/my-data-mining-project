package com.lzz.solr;

import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrInputDocument;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.*;

public class ProductCompanyConnect {
    @Test
    public void doProductCompanyConnect() throws SolrServerException, IOException {
        String companySolrUrl = "http://localhost:8081/solr/core_company";
        HttpSolrClient clientCompany = new HttpSolrClient.Builder(companySolrUrl).build();

        String productSolrUrl = "http://localhost:8081/solr/core_demo";
        HttpSolrClient clientProduct = new HttpSolrClient.Builder(productSolrUrl).build();

        String productSolrUrlReset = "http://localhost:8081/solr/core_product";
        HttpSolrClient clientProductReset = new HttpSolrClient.Builder(productSolrUrlReset).build();

        SolrQuery solrQueryProduct = new SolrQuery("*:*");
        QueryResponse queryResponseProduct = clientProduct.query(solrQueryProduct);

        long totalCountProduct = queryResponseProduct.getResults().getNumFound();

        int currentProduct = 0;
        int missCount = 0;
        solrQueryProduct.setStart(currentProduct);

        Map<String, String> mapCompanyId = new HashMap<>();

        while (currentProduct < totalCountProduct) {
            ListIterator<SolrDocument> resultProduct = queryResponseProduct.getResults().listIterator();
            List<SolrInputDocument> solrDocsProduct = new ArrayList<>();

            int countEachWhile = 0;
            while (resultProduct.hasNext()) {
                currentProduct += 1;
                System.out.println("===========================当前：" + currentProduct + "，失效：" + missCount + "===========================");
                SolrDocument docProduct = resultProduct.next();

                System.out.println(docProduct.get("gyy_company").toString());
                if(!Objects.equals(docProduct.get("gyy_company").toString(), "")){
                    if(mapCompanyId.containsKey(docProduct.get("gyy_company").toString())){
                        SolrInputDocument docProductReset = new SolrInputDocument();
                        docProductReset.addField("id", docProduct.get("id").toString());
                        docProductReset.addField("gyy_catid", docProduct.get("gyy_catid").toString());
                        docProductReset.addField("gyy_areaname", docProduct.get("gyy_areaname").toString());
                        docProductReset.addField("gyy_pic", docProduct.get("gyy_pic").toString());
                        docProductReset.addField("gyy_price", docProduct.get("gyy_price").toString());
                        docProductReset.addField("gyy_company", docProduct.get("gyy_company").toString());
                        docProductReset.addField("gyy_company_id", mapCompanyId.get(docProduct.get("gyy_company").toString()));
                        docProductReset.addField("gyy_title", docProduct.get("gyy_title").toString());
                        docProductReset.addField("gyy_vip", docProduct.get("gyy_vip").toString());
                        docProductReset.addField("gyy_parentid", docProduct.get("gyy_parentid").toString());
                        solrDocsProduct.add(docProductReset);
                    }
                    else {
                        String regEx="[^a-zA-Z_\\u4e00-\\u9fa5]";
                        String queryCompany = "gyy_company:" + docProduct.get("gyy_company").toString().replaceAll(regEx, "");

                        try{
                            SolrQuery solrQueryCompany = new SolrQuery(queryCompany);
                            QueryResponse queryResponseCompany = clientCompany.query(solrQueryCompany);
                            SolrDocument docCompany = queryResponseCompany.getResults().get(0);
                            if(Objects.equals(docCompany.get("id").toString(), "")){
                                docCompany = queryResponseCompany.getResults().get(1);
                            }
                            SolrInputDocument docProductReset = new SolrInputDocument();
                            docProductReset.addField("id", docProduct.get("id").toString());
                            docProductReset.addField("gyy_catid", docProduct.get("gyy_catid").toString());
                            docProductReset.addField("gyy_areaname", docProduct.get("gyy_areaname").toString());
                            docProductReset.addField("gyy_pic", docProduct.get("gyy_pic").toString());
                            docProductReset.addField("gyy_price", docProduct.get("gyy_price").toString());
                            docProductReset.addField("gyy_company", docProduct.get("gyy_company").toString());
                            docProductReset.addField("gyy_title", docProduct.get("gyy_title").toString());
                            docProductReset.addField("gyy_vip", docProduct.get("gyy_vip").toString());
                            docProductReset.addField("gyy_parentid", docProduct.get("gyy_parentid").toString());
                            if (Objects.equals(docCompany.get("gyy_company").toString(), docProduct.get("gyy_company").toString())) {
                                docProductReset.addField("gyy_company_id", docCompany.get("id").toString());
                                mapCompanyId.put(docCompany.get("gyy_company").toString(), docCompany.get("id").toString());
                                System.out.println("===========================插入公司：" + docProduct.get("gyy_company").toString() + "===========================");
                            }
                            else{
                                docProductReset.addField("gyy_company_id", "0");
                                System.out.println(docProduct.get("gyy_company").toString() + "不在 company 表中");
                                missCount += 1;
                            }
                            countEachWhile += 1;
                            solrDocsProduct.add(docProductReset);
                        }
                        catch (Exception e){
                            System.out.println(docProduct.get("gyy_company").toString() + "不在 company 表中");
                        }
                    }
                }
            }

            if(solrDocsProduct.size() > 0){
                clientProductReset.add(solrDocsProduct);
                clientProductReset.commit();
                System.out.println("本轮插入有效数据：" + countEachWhile + "条");
            }

            solrQueryProduct.setStart(currentProduct);
            queryResponseProduct = clientProduct.query(solrQueryProduct);
            totalCountProduct = queryResponseProduct.getResults().getNumFound();
        }
        System.out.println("current:" + currentProduct);
    }

    @Test
    public void doProductCompanyConnect2() throws SolrServerException, IOException {
        String companySolrUrl = "http://localhost:8081/solr/core_company";
        HttpSolrClient clientCompany = new HttpSolrClient.Builder(companySolrUrl).build();

        String productSolrUrl = "http://localhost:8081/solr/core_demo";
        HttpSolrClient clientProduct = new HttpSolrClient.Builder(productSolrUrl).build();

        String productSolrUrlReset = "http://localhost:8081/solr/core_product";
        HttpSolrClient clientProductReset = new HttpSolrClient.Builder(productSolrUrlReset).build();

        SolrQuery solrQueryProduct = new SolrQuery("*:*");
        QueryResponse queryResponseProduct = clientProduct.query(solrQueryProduct);

        long totalCountProduct = queryResponseProduct.getResults().getNumFound();

        int currentProduct = 756505;
        int missCount = 0;
        solrQueryProduct.setStart(currentProduct);

        Map<String, String> mapCompanyId = new HashMap<>();

        while (currentProduct < totalCountProduct) {
            ListIterator<SolrDocument> resultProduct = queryResponseProduct.getResults().listIterator();
            List<SolrInputDocument> solrDocsProduct = new ArrayList<>();

            int countEachWhile = 0;
            while (resultProduct.hasNext()) {
                currentProduct += 1;
                System.out.println("===========================当前：" + currentProduct + "，失效：" + missCount + "===========================");
                SolrDocument docProduct = resultProduct.next();

                System.out.println(docProduct.get("gyy_company").toString());
                if(!Objects.equals(docProduct.get("gyy_company").toString(), "")){
                    if(mapCompanyId.containsKey(docProduct.get("gyy_company").toString())){
                        SolrInputDocument docProductReset = new SolrInputDocument();
                        docProductReset.addField("id", docProduct.get("id").toString());
                        docProductReset.addField("gyy_catid", docProduct.get("gyy_catid").toString());
                        docProductReset.addField("gyy_areaname", docProduct.get("gyy_areaname").toString());
                        docProductReset.addField("gyy_pic", docProduct.get("gyy_pic").toString());
                        docProductReset.addField("gyy_price", docProduct.get("gyy_price").toString());
                        docProductReset.addField("gyy_company", docProduct.get("gyy_company").toString());
                        docProductReset.addField("gyy_company_id", mapCompanyId.get(docProduct.get("gyy_company").toString()));
                        docProductReset.addField("gyy_title", docProduct.get("gyy_title").toString());
                        docProductReset.addField("gyy_vip", docProduct.get("gyy_vip").toString());
                        docProductReset.addField("gyy_parentid", docProduct.get("gyy_parentid").toString());
                        solrDocsProduct.add(docProductReset);
                    }
                    else {
                        String regEx="[^a-zA-Z_\\u4e00-\\u9fa5]";
                        String queryCompany = "gyy_company:" + docProduct.get("gyy_company").toString().replaceAll(regEx, "");

                        try{
                            SolrQuery solrQueryCompany = new SolrQuery(queryCompany);
                            QueryResponse queryResponseCompany = clientCompany.query(solrQueryCompany);
                            SolrDocument docCompany = queryResponseCompany.getResults().get(0);
                            if(Objects.equals(docCompany.get("id").toString(), "")){
                                docCompany = queryResponseCompany.getResults().get(1);
                            }
                            SolrInputDocument docProductReset = new SolrInputDocument();
                            docProductReset.addField("id", docProduct.get("id").toString());
                            docProductReset.addField("gyy_catid", docProduct.get("gyy_catid").toString());
                            docProductReset.addField("gyy_areaname", docProduct.get("gyy_areaname").toString());
                            docProductReset.addField("gyy_pic", docProduct.get("gyy_pic").toString());
                            docProductReset.addField("gyy_price", docProduct.get("gyy_price").toString());
                            docProductReset.addField("gyy_company", docProduct.get("gyy_company").toString());
                            docProductReset.addField("gyy_title", docProduct.get("gyy_title").toString());
                            docProductReset.addField("gyy_vip", docProduct.get("gyy_vip").toString());
                            docProductReset.addField("gyy_parentid", docProduct.get("gyy_parentid").toString());
                            if (Objects.equals(docCompany.get("gyy_company").toString(), docProduct.get("gyy_company").toString())) {
                                docProductReset.addField("gyy_company_id", docCompany.get("id").toString());
                                mapCompanyId.put(docCompany.get("gyy_company").toString(), docCompany.get("id").toString());
                                System.out.println("===========================插入公司：" + docProduct.get("gyy_company").toString() + "===========================");
                            }
                            else{
                                docProductReset.addField("gyy_company_id", "0");
                                System.out.println(docProduct.get("gyy_company").toString() + "不在 company 表中");
                                missCount += 1;
                            }
                            countEachWhile += 1;
                            solrDocsProduct.add(docProductReset);
                        }
                        catch (Exception e){
                            System.out.println(docProduct.get("gyy_company").toString() + "不在 company 表中");
                        }
                    }
                }
            }

            if(solrDocsProduct.size() > 0){
                clientProductReset.add(solrDocsProduct);
                clientProductReset.commit();
                System.out.println("本轮插入有效数据：" + countEachWhile + "条");
            }

            solrQueryProduct.setStart(currentProduct);
            queryResponseProduct = clientProduct.query(solrQueryProduct);
            totalCountProduct = queryResponseProduct.getResults().getNumFound();
        }
        System.out.println("current:" + currentProduct);
    }

    @Test
    public void doProductCompanyConnect3() throws SolrServerException, IOException {
        String companySolrUrl = "http://localhost:8081/solr/core_company";
        HttpSolrClient clientCompany = new HttpSolrClient.Builder(companySolrUrl).build();

        String productSolrUrl = "http://localhost:8081/solr/core_demo";
        HttpSolrClient clientProduct = new HttpSolrClient.Builder(productSolrUrl).build();

        String productSolrUrlReset = "http://localhost:8081/solr/core_product";
        HttpSolrClient clientProductReset = new HttpSolrClient.Builder(productSolrUrlReset).build();

        SolrQuery solrQueryProduct = new SolrQuery("*:*");
        QueryResponse queryResponseProduct = clientProduct.query(solrQueryProduct);

        long totalCountProduct = queryResponseProduct.getResults().getNumFound();

        int currentProduct = 756505;
        int missCount = 0;
        solrQueryProduct.setStart(currentProduct);

        Map<String, String> mapCompanyId = new HashMap<>();

        while (currentProduct < totalCountProduct) {
            ListIterator<SolrDocument> resultProduct = queryResponseProduct.getResults().listIterator();
            List<SolrInputDocument> solrDocsProduct = new ArrayList<>();

            int countEachWhile = 0;
            while (resultProduct.hasNext()) {
                currentProduct += 1;
                System.out.println("===========================当前：" + currentProduct + "，失效：" + missCount + "===========================");
                SolrDocument docProduct = resultProduct.next();

                System.out.println(docProduct.get("gyy_company").toString());
                if(!Objects.equals(docProduct.get("gyy_company").toString(), "")){
                    if(mapCompanyId.containsKey(docProduct.get("gyy_company").toString())){
                        SolrInputDocument docProductReset = new SolrInputDocument();
                        docProductReset.addField("id", docProduct.get("id").toString());
                        docProductReset.addField("gyy_catid", docProduct.get("gyy_catid").toString());
                        docProductReset.addField("gyy_areaname", docProduct.get("gyy_areaname").toString());
                        docProductReset.addField("gyy_pic", docProduct.get("gyy_pic").toString());
                        docProductReset.addField("gyy_price", docProduct.get("gyy_price").toString());
                        docProductReset.addField("gyy_company", docProduct.get("gyy_company").toString());
                        docProductReset.addField("gyy_company_id", mapCompanyId.get(docProduct.get("gyy_company").toString()));
                        docProductReset.addField("gyy_title", docProduct.get("gyy_title").toString());
                        docProductReset.addField("gyy_vip", docProduct.get("gyy_vip").toString());
                        docProductReset.addField("gyy_parentid", docProduct.get("gyy_parentid").toString());
                        solrDocsProduct.add(docProductReset);
                    }
                    else {
                        String regEx="[^a-zA-Z_\\u4e00-\\u9fa5]";
                        String queryCompany = "gyy_company:" + docProduct.get("gyy_company").toString().replaceAll(regEx, "");

                        try{
                            SolrQuery solrQueryCompany = new SolrQuery(queryCompany);
                            QueryResponse queryResponseCompany = clientCompany.query(solrQueryCompany);
                            SolrDocument docCompany = queryResponseCompany.getResults().get(0);
                            if(Objects.equals(docCompany.get("id").toString(), "")){
                                docCompany = queryResponseCompany.getResults().get(1);
                            }
                            SolrInputDocument docProductReset = new SolrInputDocument();
                            docProductReset.addField("id", docProduct.get("id").toString());
                            docProductReset.addField("gyy_catid", docProduct.get("gyy_catid").toString());
                            docProductReset.addField("gyy_areaname", docProduct.get("gyy_areaname").toString());
                            docProductReset.addField("gyy_pic", docProduct.get("gyy_pic").toString());
                            docProductReset.addField("gyy_price", docProduct.get("gyy_price").toString());
                            docProductReset.addField("gyy_company", docProduct.get("gyy_company").toString());
                            docProductReset.addField("gyy_title", docProduct.get("gyy_title").toString());
                            docProductReset.addField("gyy_vip", docProduct.get("gyy_vip").toString());
                            docProductReset.addField("gyy_parentid", docProduct.get("gyy_parentid").toString());
                            if (Objects.equals(docCompany.get("gyy_company").toString(), docProduct.get("gyy_company").toString())) {
                                docProductReset.addField("gyy_company_id", docCompany.get("id").toString());
                                mapCompanyId.put(docCompany.get("gyy_company").toString(), docCompany.get("id").toString());
                                System.out.println("===========================插入公司：" + docProduct.get("gyy_company").toString() + "===========================");
                            }
                            else{
                                docProductReset.addField("gyy_company_id", "0");
                                System.out.println(docProduct.get("gyy_company").toString() + "不在 company 表中");
                                missCount += 1;
                            }
                            countEachWhile += 1;
                            solrDocsProduct.add(docProductReset);
                        }
                        catch (Exception e){
                            System.out.println(docProduct.get("gyy_company").toString() + "不在 company 表中");
                        }
                    }
                }
            }

            if(solrDocsProduct.size() > 0){
                clientProductReset.add(solrDocsProduct);
                clientProductReset.commit();
                System.out.println("本轮插入有效数据：" + countEachWhile + "条");
            }

            solrQueryProduct.setStart(currentProduct);
            queryResponseProduct = clientProduct.query(solrQueryProduct);
            totalCountProduct = queryResponseProduct.getResults().getNumFound();
        }
        System.out.println("current:" + currentProduct);
    }
}
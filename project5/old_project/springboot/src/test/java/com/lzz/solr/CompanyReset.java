package com.lzz.solr;

import com.lzz.gyyArea.pojo.GyyArea;
import com.lzz.gyyCompany.pojo.GyyCompany;
import org.apache.ibatis.jdbc.SQL;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.sql.*;
import java.util.List;
import java.util.ListIterator;

public class CompanyReset {

    @Test
    public void InsertIntoCompany() throws SQLException, ClassNotFoundException, SolrServerException, IOException {
        String baseSolrUrl = "http://localhost:8081/solr/core_company";
        HttpSolrClient client = new HttpSolrClient.Builder(baseSolrUrl).build();
        HttpSolrClient client1 = new HttpSolrClient.Builder(baseSolrUrl).build();

        // 数据库链接
        Connection connection = null;

        // 预编译 statement
        Statement stmt = null;

        // 加载数据库驱动
        Class.forName("com.mysql.jdbc.Driver");

        // 连接数据库
        connection = DriverManager.getConnection("jdbc:mysql://10.236.11.236:3306/gyy", "root", "lzzdbpwd");

        SolrQuery solrQuery = new SolrQuery("*:*");
        Integer start = 0;
        solrQuery.setStart(start);
        QueryResponse queryResponse = client.query(solrQuery);

        int QTime = queryResponse.getQTime();
        long totalCount = queryResponse.getResults().getNumFound();
//        System.out.println(queryResponse.getResults().get(0).get("gyy_company_business").toString());
        System.out.println("总数据数目" + totalCount +"\t" + "用时：" + QTime);

        // 大概每存入 6W 条数据时会出现错误，需要从出现错误的地方重新进行
        // 报错原因是连接频率问题
        int current = 428225;
        while (current < totalCount) {
            ListIterator<SolrDocument> result = queryResponse.getResults().listIterator();
            while (result.hasNext()) {
                current += 1;
                System.out.println("===========================" + current + "===========================");
                SolrDocument doc = result.next();

                String relative = "[";

                // 去掉除 字母、下划线、汉字 以外的全部字符
                String regEx="[^a-zA-Z_\\u4e00-\\u9fa5]";
                String business = doc.get("gyy_company_business").toString().replaceAll(regEx, " ").replace("OR", "或").
                        replace("or", "或").replace("AND", "和").replace("and", "和");
                if(business.equals("") || business.contains("href") || business.trim().length()== 0){
                    continue;
                }
                String query = "gyy_company_business:" + business;
                System.out.println(query);
                SolrQuery solrQuery1 = new SolrQuery(query);
                QueryResponse queryResponse1 = client1.query(solrQuery1);

                int j = 0;
                long totalCount1 = queryResponse1.getResults().getNumFound();
                while (j < totalCount1) {
                    ListIterator<SolrDocument> result1 = queryResponse1.getResults().listIterator();

                    while (result1.hasNext()) {
                        SolrDocument doc1 = result1.next();
                        if(doc1.get("id") == doc.get("id")){
                            continue;
                        }
                        relative = relative + doc1.get("id");
                        relative = relative + ",";
                        j++;
                    }
                    solrQuery1.setStart(j);
                    queryResponse1 = client.query(solrQuery1);
                    totalCount1 = queryResponse1.getResults().getNumFound();
                    if(j >= 100){
                        break;
                    }

                }
                System.out.println(relative.substring(0, relative.length() - 1));
                relative = relative.substring(0, relative.length() - 1);
                relative = relative + "]";

                try {
                    String insert_sql = "insert into gyy_company_reset values('" + doc.get("id").toString() + "', '"
                            + doc.get("gyy_company").toString() + "', '" + business + "','"
                            + relative + "')";
                    stmt = connection.createStatement();
                    stmt.execute(insert_sql);
                }
                catch (Exception e){
                    continue;
                }
            }
            solrQuery.setStart(current);
            queryResponse = client.query(solrQuery);
            totalCount = queryResponse.getResults().getNumFound();
        }
        connection.close();
        System.out.println("current:" + current);
    }
}

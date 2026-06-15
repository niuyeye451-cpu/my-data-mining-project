package com.lzz.neo4j;

import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.junit.jupiter.api.Test;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;

public class getInfoFromSolr {
    private static final String parentPath = "D:\\Neo4j\\neo4j-community-3.5.31\\import\\";

    @Test
    public static void main(String[] args) throws SolrServerException, IOException {
        String baseSolrUrl = "http://localhost:8081/solr/core_area";
        createCity("省-直辖市.csv", getCity(baseSolrUrl));
    }

    public static List<String> getCity(String solrUrl) throws SolrServerException, IOException {
        HttpSolrClient client = new HttpSolrClient.Builder(solrUrl).build();
        SolrQuery solrQuery = new SolrQuery("*:*");
        solrQuery.setStart(0);
        QueryResponse queryResponse = client.query(solrQuery);
        long totalCount = queryResponse.getResults().getNumFound();

        int current = 0;
        List<String> cityList = new ArrayList<>();
        while (current < totalCount) {
            for (SolrDocument entries : queryResponse.getResults()) {
                current += 1;
                cityList.add(entries.get("gyy_areaname").toString());
            }
            solrQuery.setStart(current);
            queryResponse = client.query(solrQuery);
            totalCount = queryResponse.getResults().getNumFound();
        }
        return cityList;
    }

    public static void createCity(String filename, List<String> cityList) throws IOException {
        String cityPath = parentPath + filename;
        BufferedWriter cityWriter = new BufferedWriter (new FileWriter(cityPath));
        for(String city: cityList){
            cityWriter.write(city);
            cityWriter.newLine();
        }
        cityWriter.close();
    }
}

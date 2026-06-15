package com.lzz.neo4j;

import org.junit.jupiter.api.Test;
import org.springframework.data.redis.connection.ReactiveSetCommands;

import java.io.*;
import java.util.*;

public class createObjectRelations {
    private static final String parentPath = "D:\\Neo4j\\neo4j-community-3.5.31\\import\\";

    @Test
    public static void main(String[] args) throws IOException {
        createCrossRelationFromExist("商品-公司.csv", "售卖");
    }

    // 创建反向关系
    public static void createCrossRelationFromExist(String relationFileName, String Relation) throws IOException {
        String relationFilePath = parentPath + relationFileName;
        BufferedReader relationFileReader = new BufferedReader(new FileReader(relationFilePath));
        String relationFileReaderLine = relationFileReader.readLine();

        String subParRelationPath = parentPath +
                relationFileName.replace(".csv", "").split("-")[1] +
                "-" +
                relationFileName.replace(".csv", "").split("-")[0] +
                ".csv";
        BufferedWriter subParRelationWriter = new BufferedWriter (new FileWriter(subParRelationPath));

        while (relationFileReaderLine != null){
            String subParRelation = relationFileReaderLine.split(",")[2] +
                    "," +
                    Relation +
                    "," +
                    relationFileReaderLine.split(",")[0];
            subParRelationWriter.write(subParRelation);
            subParRelationWriter.newLine();
            relationFileReaderLine = relationFileReader.readLine();
        }
        subParRelationWriter.close();
        relationFileReader.close();
    }

    // 批量创建关系
    public static void autoCreateObjectRelations() throws IOException {
        randomRelated("商品.csv", "子类别.csv", "属于");
        randomRelated("商品.csv", "公司.csv", "卖家");
        randomRelated("子类别.csv", "类别.csv", "属于");
        randomRelated("公司.csv", "省市.csv", "省市");
    }

    // 批量创建对象
    public static void autoCreateObject() throws IOException {
        Map<String, Integer> objectMap = new HashMap<>();
        objectMap.put("商品.csv", 10000);
        objectMap.put("子类别.csv", 500);
        objectMap.put("公司.csv", 1000);
        String[] keyList = objectMap.keySet().toString().replace("[", "")
                .replace("]","").split(", ");
        for(String key : keyList){
            objectCreate(objectMap.get(key), key);
        }
    }

    // 创建对象
    public static void objectCreate(int createNum, String filename) throws IOException {
        String subPath = parentPath + filename;
        FileWriter subWriter = new FileWriter(subPath);

        int i = 0;
        while(i < createNum){
            String objectName;
            if(i < (createNum - 1)){
                objectName = filename.replace(".csv", "") + (i + 1) + "\n";
            }
            else{
                objectName = filename.replace(".csv", "") + (i + 1);
            }
            subWriter.write(objectName);
            i++;
        }
        subWriter.close();
    }

    // 创建对象之间的关系
    public static void randomRelated(String subFileName, String parFileName, String Relation) throws IOException {
        String parPath = parentPath + parFileName;
        BufferedReader parReader = new BufferedReader(new FileReader(parPath));
        String parReaderLine = parReader.readLine();

        String subPath = parentPath + subFileName;
        BufferedReader subReader = new BufferedReader(new FileReader(subPath));
        String subReaderLine = subReader.readLine();

        String subParRelationPath = parentPath + subFileName.replace(".csv", "")
                + "-" + parFileName;
        BufferedWriter subParRelationWriter = new BufferedWriter (new FileWriter(subParRelationPath));

        List<String> parObjectList = new ArrayList<>();
        while (parReaderLine != null){
            parObjectList.add(parReaderLine);
            parReaderLine = parReader.readLine();
        }
        parReader.close();

        Random random = new Random();
        while (subReaderLine != null){
            int index = random.nextInt(parObjectList.size());
            String subParRelation = subReaderLine + "," + Relation + "," + parObjectList.get(index);
            subParRelationWriter.write(subParRelation);
            subParRelationWriter.newLine();
            subReaderLine = subReader.readLine();
        }
        subParRelationWriter.close();
        subReader.close();
    }
}

package com.lzz.solr;

import com.lzz.gyyMall.pojo.GyyMall;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.junit.jupiter.api.Test;
//import org.wltea.analyzer.lucene.IKAnalyzer;

import java.nio.file.Paths;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class AreaReset {

    @Test
    public void remakeDB() {
        // 数据库链接
        Connection connection = null;
        Connection connection1 = null;

        // 预编译 statement
        PreparedStatement preparedStatement = null;
        Statement stmt = null;

        // 结果集
        ResultSet resultSet = null;

        try {
            // 加载数据库驱动
            Class.forName("com.mysql.jdbc.Driver");

            // 连接数据库
            connection = DriverManager.getConnection("jdbc:mysql://10.236.11.236:3306/gyy", "root", "lzzdbpwd");

            connection1 = DriverManager.getConnection("jdbc:mysql://10.236.11.236:3306/gyy", "root", "lzzdbpwd");

            // SQL 语句  查询数据库表中的所有数据
            String sql = "SELECT * FROM gyy_area_reset";

            // 创建 preparedStatement
            preparedStatement = connection.prepareStatement(sql);

            // 获取结果集
            resultSet = preparedStatement.executeQuery();

            int count = 0;
            while(resultSet.next()){
                count += 1;
                String areaid = resultSet.getString("areaid");
                String areaname = resultSet.getString("areaname");
                String[] arrparentid = resultSet.getString("arrparentid").split(",");
                if(arrparentid.length > 1){
                    String areaNameReset = "";
                    for(int i = 1; i < arrparentid.length; i++){
                        String parent_sql = "SELECT areaname FROM gyy_area_reset where areaid = " + arrparentid[i];
                        PreparedStatement preparedStatement1 = connection1.prepareStatement(parent_sql);
                        ResultSet resultSet1 = preparedStatement1.executeQuery();
                        while (resultSet1.next()){
                            if(i == 1){
                                areaNameReset = resultSet1.getString("areaname");
                            }
                            else{
                                areaNameReset = areaNameReset + "/" + resultSet1.getString("areaname");
                            }
                        }
                    }
                    areaNameReset = areaNameReset + "/" + areaname;
                    String update_sql = "Update gyy_area_reset set areaname = '" + areaNameReset + "' where areaid = " + areaid;
                    stmt = connection1.createStatement();
                    stmt.execute(update_sql);
                    System.out.println(areaNameReset);
                }
            }
            System.out.println("总共" + count + "条数据");
            connection.close();
            connection1.close();
        } catch (SQLException throwables) {
            throwables.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }

    @Test
    public void remakeDB_AreaReset() throws ClassNotFoundException, SQLException {
        // 数据库链接
        Connection connection = null;
        Connection connection1 = null;

        // 预编译 statement
        PreparedStatement preparedStatement = null;
        Statement stmt = null;

        // 结果集
        ResultSet resultSet = null;

        try {
            // 加载数据库驱动
            Class.forName("com.mysql.jdbc.Driver");

            // 连接数据库
            connection = DriverManager.getConnection("jdbc:mysql://10.236.11.236:3306/gyy", "root", "lzzdbpwd");

            connection1 = DriverManager.getConnection("jdbc:mysql://10.236.11.236:3306/gyy", "root", "lzzdbpwd");

            // SQL 语句  查询数据库表中的所有数据
            String sql = "SELECT * FROM gyy_area_reset";

            // 创建 preparedStatement
            preparedStatement = connection.prepareStatement(sql);

            // 获取结果集
            resultSet = preparedStatement.executeQuery();

            int count = 0;
            while(resultSet.next()){
                count += 1;
                String areaid = resultSet.getString("areaid");
                String[] areaname = resultSet.getString("areaname").split("/");
                String[] arrparentid = resultSet.getString("arrparentid").split(",");
                if(areaname.length != arrparentid.length){
                    String areaNameReset = "";
                    for(int i = areaname.length - arrparentid.length; i < areaname.length; i++){
                        if(i == areaname.length - arrparentid.length){
                            areaNameReset = areaname[i];
                        }
                        else{
                            areaNameReset = areaNameReset + "/" + areaname[i];
                        }
                    }
                    String update_sql = "Update gyy_area_reset set areaname = '" + areaNameReset + "' where areaid = " + areaid;
                    stmt = connection1.createStatement();
                    stmt.execute(update_sql);
                    if(areaNameReset != "")
                        System.out.println(areaNameReset);
                }
                else{
                    continue;
                }
            }
            System.out.println("总共" + count + "条数据");
            connection.close();
            connection1.close();
        } catch (SQLException throwables) {
            throwables.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }

    @Test
    public void remakeDB_ParentReset() throws ClassNotFoundException, SQLException {
        // 数据库链接
        Connection connection = null;
        Connection connection1 = null;

        // 预编译 statement
        PreparedStatement preparedStatement = null;
        Statement stmt = null;

        // 结果集
        ResultSet resultSet = null;

        try {
            // 加载数据库驱动
            Class.forName("com.mysql.jdbc.Driver");

            // 连接数据库
            connection = DriverManager.getConnection("jdbc:mysql://10.236.11.236:3306/gyy", "root", "lzzdbpwd");

            connection1 = DriverManager.getConnection("jdbc:mysql://10.236.11.236:3306/gyy", "root", "lzzdbpwd");

            // SQL 语句  查询数据库表中的所有数据
            String sql = "SELECT * FROM gyy_area_reset";

            // 创建 preparedStatement
            preparedStatement = connection.prepareStatement(sql);

            // 获取结果集
            resultSet = preparedStatement.executeQuery();

            int count = 0;
            while(resultSet.next()){
                count += 1;
                String areaid = resultSet.getString("areaid");
                String parentid = resultSet.getString("parentid");
                String[] arrparentid = resultSet.getString("arrparentid").split(",");
                if(arrparentid.length > 1){
                    parentid = arrparentid[1];
                }
                else{
                    parentid = areaid;;
                }
                String update_sql = "Update gyy_area_reset set parentid = '" + parentid + "' where areaid = " + areaid;
                stmt = connection1.createStatement();
                stmt.execute(update_sql);
                System.out.println(count);
            }
            System.out.println("总共" + count + "条数据");
            connection.close();
            connection1.close();
        } catch (SQLException throwables) {
            throwables.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
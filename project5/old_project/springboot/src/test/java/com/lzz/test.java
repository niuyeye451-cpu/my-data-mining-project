package com.lzz;

import org.junit.jupiter.api.Test;
//import org.neo4j.driver.*;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

public class test {
    @Test
    public static void main(String[] args) {
//        Driver driver = GraphDatabase.driver("bolt://localhost:7687", AuthTokens.basic("neo4j", "123456"));
//        Session session = driver.session();
//        // 查询
//        Result result = session.run("MATCH (p:商品) WHERE p.name = \"商品1\" RETURN p.name as name, p.price as price");
//        while (result.hasNext()) {
//            Record record = result.next();
//            String name = record.get("name").asString();
//            Integer price = record.get("price").asInt();
//            System.out.println(name + "\t" + price);
//        }
//        session.close();
//        driver.close();
    }
}

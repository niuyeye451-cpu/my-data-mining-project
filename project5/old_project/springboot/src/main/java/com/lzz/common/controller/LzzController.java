package com.lzz.common.controller;

import com.lzz.common.pojo.GyyResult;
import com.lzz.common.pojo.QueryContent;
import com.lzz.gyyArea.service.GetArea;
import com.lzz.gyyCompany.service.CompanySearch;
import com.lzz.gyyMall.service.MallSearch;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
public class LzzController {
    @Autowired
    private CompanySearch companySearch;

    @Autowired
    private MallSearch mallSearch;

    @Autowired
    private GetArea getArea;


    @PostMapping("/getArea")
    public GyyResult getArea() throws Exception {
        return getArea.getArea();
    }

    @PostMapping("/query")
    public GyyResult query(@RequestBody QueryContent queryContent){
        // 处理当前页
        if (StringUtils.isEmpty(queryContent.getPage())) {
            queryContent.setPage(1);
        }
        if (queryContent.getPage() <= 0) {
            queryContent.setPage(1);
        }

        GyyResult result = new GyyResult();

        // 调用 service 查询
        try{
            if(queryContent.getQueryTable().equals("mall")){
                result = mallSearch.query(queryContent);
            }
            else{
                result = companySearch.query(queryContent);
            }
        }
        catch (Exception e){
            result.setMsg("未查询到相关信息");
        }
        return result;
    }
}

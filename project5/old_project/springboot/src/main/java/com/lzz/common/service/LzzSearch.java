package com.lzz.common.service;

import com.lzz.common.pojo.GyyResult;
import com.lzz.common.pojo.QueryContent;
import org.springframework.stereotype.Service;

@Service
public interface LzzSearch {
    /*
    * queryColumnName 代表要检索的内容所在列的列名
    * queryString 表示检索关键字
    * page 代表当前页
    * */
    GyyResult query(QueryContent queryContent) throws Exception;
}

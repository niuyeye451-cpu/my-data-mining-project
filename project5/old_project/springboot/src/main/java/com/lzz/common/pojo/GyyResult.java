package com.lzz.common.pojo;

import com.lzz.gyyCompany.pojo.GyyCompany;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Collection;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GyyResult<T> {
    // 返回数据
    private List<T> data;

    // 数据总数
    private Long recordCount;

    // 总页数
    private Long pageCount;

    // 当前页
    private long curPage;

    // 设置消息
    private String msg;
}

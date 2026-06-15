package com.lzz.user.pojo;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

@Data
public class User implements Serializable {
    private Integer userID;

    private String username;

    private String password;

    private String email;

    private String gender;

    private String userimg = " ";

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date signinDate;

    private String keywordList;

    private Integer companyID;
}

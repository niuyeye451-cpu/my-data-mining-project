package com.lzz.user.mapper;


import com.lzz.user.pojo.User;
import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Component;

@Component
@Mapper
public interface UserMapper {

    @Options(useGeneratedKeys = true,keyProperty = "userID",keyColumn = "userID")
    @Insert("INSERT INTO `gyy_user`(`username`,`password`,`email`,`gender`,`userimg`,`signinDate`,`keywordList`,`companyID`) " +
            "VALUES (#{user.username},#{user.password},#{user.email},#{user.gender},#{user.userimg},#{user.signinDate},#{user.keywordList},#{user.companyID})")
    void insert(@Param("user") User user );

    @Select("SELECT COALESCE(userID,0) FROM `gyy_user` WHERE `username` = #{username}")
    Integer getUserIDByName(@Param("username") String username);

    @Select("SELECT * FROM `gyy_user` WHERE `username` = #{username}")
    User getUserByName(@Param("username") String username);


}

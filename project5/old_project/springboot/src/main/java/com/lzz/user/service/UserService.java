package com.lzz.user.service;

import com.lzz.user.mapper.UserMapper;
import com.lzz.user.pojo.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;


@Service
public class UserService {
    @Autowired
    UserMapper userMapper;

    /*
        按名字查询某个用户的id
    */
    public Integer getUserIDByName(String username) {
        if(userMapper.getUserIDByName(username) == null)
            return 0;
        else
            return userMapper.getUserIDByName(username);
    }
    /*
        按名字查询某个用户
    */
    public User getUserByName(String username) {
        return userMapper.getUserByName(username);
    }


    /*
        根据用户名判断用户是否存在
    */
    public boolean exist(User user) {
        return getUserIDByName(user.getUsername()) != 0;
    }

    /*
        新注册用户
    */
    public void register(User user) {
        //System.out.println("hh");
        if (exist(user)) {
            throw new RuntimeException("用户名已被注册！");
        }
        else {
            System.out.println("hh");
            userMapper.insert(user);
        }
        //userMapper.insert(user);
    }
}

package com.lzz.user.controller;

import com.lzz.common.pojo.MessageResult;
import com.lzz.user.pojo.User;
import com.lzz.user.service.UserService;
import org.apache.shiro.SecurityUtils;
import org.apache.shiro.authc.AuthenticationException;
import org.apache.shiro.authc.UsernamePasswordToken;
import org.apache.shiro.subject.Subject;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.HtmlUtils;

import java.util.Date;


@RestController
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/register")
    public MessageResult register(@RequestBody User user) {
        //获取用户名密码
        String username = HtmlUtils.htmlEscape(user.getUsername());
        user.setUsername(username);
        user.setPassword(user.getPassword());
        //获取注册日期
        Date date = new Date();
        date.getTime();
        user.setSigninDate(date);

        try {
            userService.register(user);
            return new MessageResult(200,"注册成功");
        }catch (Exception e) {
            e.printStackTrace();
            return new MessageResult(400,e.getMessage());
        }
    }

    @PostMapping("/login")
    public MessageResult login(@RequestBody User requestUser) {
        String requestUserName = HtmlUtils.htmlEscape(requestUser.getUsername());
        Subject subject = SecurityUtils.getSubject();
        UsernamePasswordToken usernamePasswordToken = new UsernamePasswordToken(requestUserName,requestUser.getPassword());
        try{
            subject.login(usernamePasswordToken);
            return new MessageResult(200,"登录成功");

        } catch (AuthenticationException e) {
            e.printStackTrace();
            return new MessageResult(400,"账号或密码错误");
        }
    }

}

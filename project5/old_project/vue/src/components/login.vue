<template>
  <div>
    <div class="mainbox">
      <div class="inputbox">
        <el-tag>用户名:</el-tag>
        <el-input v-model="inputname"></el-input>
      </div>
      <div class="inputbox">
        <el-tag>密&emsp;码:</el-tag>
        <el-input v-model="inputpsw" type="password"></el-input>
      </div>
      <div class="btnbox">
        <el-button type="success" round @click="toLogin">登&emsp;录</el-button>
        <el-button type="warning" round @click="toRegist">注&emsp;册</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  data() {
    return {
      inputname:'',
      inputpsw:'',
      username:''
    }
  },
  methods: {
    toRegist(){
      this.$router.push({ path: "/register" })
    },
    toLogin(){
      if(this.inputname===''){
        ElMessage('请输入用户名！')
      } else if(this.inputpsw===''){
        ElMessage('请输入密码！')
      } else {
        this.username = this.inputname
        this.$http({
          method: 'post',
          url: '/login',
          data: {
            username: this.inputname,
            password: this.inputpsw,
          }
        })
          .then(({ data }) => {
            console.log(data)
            if(data.code===200){
              this.$store.state.if_login = true
              this.$store.state.userName = this.username
              this.$router.push({ path: "/search" })
            } else {
              if (data.message !== null){
                ElMessage(data.message)
              } else {
                ElMessage('登陆失败！')
              }
            }
          })
          .catch((error) => {
            console.log('ERR')
            console.log(error)
          })
      }
    }
  },
  computed: {
      
  }
}
</script>

<style scoped>
.mainbox{
  width: 400px;
  height: 200px;
  margin: 100px auto;
  border-style: dashed;
  border-radius: 15px;
  border-color: pink;
  padding: 15px 0px 0px 0px;
}

.el-input{
  width: 200px;
  margin: 10px;
}

.el-tag{
  width: 80px;
  height: 32px;
  font-size: 16px;
  margin: 10px 10px;
}

.el-button{
  margin: 10px 15px;
}

.inputbox{
  margin: 5px 0px;
}

.btnbox{
  margin: 10px 0px 0px 0px;
}
</style>
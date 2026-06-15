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
      <div class="inputbox">
        <el-tag>邮&emsp;箱:</el-tag>
        <el-input v-model="inputmail"></el-input>
      </div>
      <div class="inputbox">
        <el-tag>性&emsp;别:</el-tag>
        <div class="space">
          <el-switch v-model="sexual" active-color="#13ce66" inactive-color="#ff4949" active-text="女" inactive-text="男" />
        </div>
      </div>
      <div class="inputbox">
        <el-tag>行&emsp;业:</el-tag>
        <el-input v-model="keyword"></el-input>
      </div>
      <div class="btnbox">
        <el-button type="success" round @click="regist">注&emsp;册</el-button>
        <el-button type="warning" round @click="reset">重&emsp;置</el-button>
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
      inputmail:'',
      keyword:'',
      sexual: false
    }
  },
  methods: {
    regist(){
      if(this.check()) {
        // console.log(this)
        this.$http({
          method: 'post',
          url: '/register',
          data: {
            userID: 0,
            username: this.inputname,
            password: this.inputpsw,
            email: this.inputmail,
            gender: this.getSex,
            userimg: 'default',
            signinDate: '',
            keywordList: this.keyword,
            companyID: 1
          }
        })
          .then(({ data }) => {
            console.log(data)
            if (data.code=== 200) {
              ElMessage('注册成功！')
              new Promise((resove) => {
                setTimeout(resove, 1500)
              })
                .then(() => {
                  this.$router.push({path: '/login'})
                })
            } else {
              if (data.message !== null){
                ElMessage(data.message)
              } else {
                ElMessage('注册失败！')
              }
            }
          })
          .catch((error) => {
            console.log('ERR')
            console.log(error)
          })
      }
    },
    reset(){
      this.sexual=false
      this.inputname = ''
      this.inputpsw = ''
      this.inputmail = ''
      this.keyword = ''
    },
    check(){
      if(this.inputname==='') {
        ElMessage('请输入用户名！')
        return false
      } else if(this.inputpsw==='') {
        ElMessage('请输入密码！')
        return false
      } else if(this.inputmail==='') {
        ElMessage('请输入邮箱！')
        return false
      } else {
        return true
      }
    }
  },
  computed: {
    getSex(){
      if(this.sexual) {
        return '女'
      } else {
        return '男'
      }
    }
  }
}
</script>

<style scoped>
.mainbox{
  width: 400px;
  height: 375px;
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

.space{
  display: inline-block;
  height: 32px;
  width: 200px;
  margin: 10px;
  text-align: left;
}

</style>
<template>
  <div>
    <el-menu class="h" mode="horizontal" router>
      <el-menu-item id="mall" index="/search">
        <img class="logoImg" src="../assets/lzz.png" />
        &emsp;工业商城
      </el-menu-item>
      <el-menu-item id="loginmenu" v-if="!ifLogin" index="/login">
        <!--<img src="../assets/avatar.png" class="headerImg" />-->
        <el-avatar> 用户 </el-avatar>
        &emsp;未登录
      </el-menu-item>
      <el-sub-menu id="submenu" v-else>
        <template #title>
          <img src="../assets/pic.jpg" class="headerImg" />&emsp;{{ userName }}
        </template>
        <el-menu-item @click="logout" index="/search">登出</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons'

export default {
  components:{
    UserFilled
  },
  data() {
    return {
      
    }
  },
  methods: {
    logout(){
      this.$store.state.if_login = false
      this.$store.state.userName = null
      ElMessage('成功登出！')
    }

  },
  computed: {
    ifLogin() {
      return this.$store.state.if_login
    },
    userName() {
      return this.$store.state.userName
    },
    /*handleClose() {

    },
    handleOpen() {

    },
    handleSelect( index ) {
      //if(index){
        this.$router.push({ path: index })
      //}
    }*/
  }
}
</script>

<style scoped>
.h {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
}
.headerImg {
  width: 55px;
  height: 55px;
  /* border-radius: 50%; */
}
#submenu,
#loginmenu{
  position: absolute;
  right: 0;
}
.logoImg{
  height: 50px;
}
/*#mall{
  position: absolute;
  left: 0;
}*/
</style>
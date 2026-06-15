<template>
  <div>
    <div id="searchbox">
      <div id="selectclass">
        <div class="label">
          <span style="margin: auto;">所属类别</span>
        </div>
        <div>
          <div id="tags">
            <el-tag :type="classTagType(0)" @click.native="classTagOnclick(0, '全部')">全部</el-tag>
            <el-tag :type="classTagType(1)" @click.native="classTagOnclick(1, '摩托车配件')">摩托车配件</el-tag>
            <el-tag :type="classTagType(2)" @click.native="classTagOnclick(2, '装备制造')">装备制造</el-tag>
            <el-tag :type="classTagType(3)" @click.native="classTagOnclick(3, '电子制造')">电子制造</el-tag>
            <el-tag :type="classTagType(4)" @click.native="classTagOnclick(4, '材料/新材料')">材料/新材料</el-tag>
            <el-tag :type="classTagType(5)" @click.native="classTagOnclick(5, '生物医药')">生物医药</el-tag>
            <el-tag :type="classTagType(6)" @click.native="classTagOnclick(6, '食品/农副产品')">食品/农副产品</el-tag>
            <el-tag :type="classTagType(7)" @click.native="classTagOnclick(7, '化工/塑料')">化工/塑料</el-tag>
            <el-tag :type="classTagType(8)" @click.native="classTagOnclick(8, '服装鞋靴')">服装鞋靴</el-tag>
          </div>
          <div v-show="showClass">
            <div class="hide">
              <el-tag :type="classTagType(9)" @click.native="classTagOnclick(9, '软件/信息服务')">软件/信息服务</el-tag>
              <el-tag :type="classTagType(10)" @click.native="classTagOnclick(10, '高新技术')">高新技术</el-tag>
              <el-tag :type="classTagType(11)" @click.native="classTagOnclick(11, '特色轻工/仪表')">特色轻工/仪表</el-tag>
              <el-tag :type="classTagType(12)" @click.native="classTagOnclick(12, '五金制品')">五金制品</el-tag>
              <el-tag :type="classTagType(13)" @click.native="classTagOnclick(13, '钢铁冶金')">钢铁冶金</el-tag>
              <el-tag :type="classTagType(14)" @click.native="classTagOnclick(14, '环保科技')">环保科技</el-tag>
              <el-tag :type="classTagType(15)" @click.native="classTagOnclick(15, '新能源')">新能源</el-tag>
              <el-tag :type="classTagType(16)" @click.native="classTagOnclick(16, '电子信息')">电子信息</el-tag>
              <el-tag :type="classTagType(17)" @click.native="classTagOnclick(17, '铝加工')">铝加工</el-tag>
            </div>
            <div class="hide">
              <el-tag :type="classTagType(18)" @click.native="classTagOnclick(18, '家居建材/照明')">家居建材/照明</el-tag>
              <el-tag :type="classTagType(19)" @click.native="classTagOnclick(19, '精密加工')">精密加工</el-tag>
              <el-tag :type="classTagType(20)" @click.native="classTagOnclick(20, '煤炭采洗')">煤炭采洗</el-tag>
              <el-tag :type="classTagType(21)" @click.native="classTagOnclick(21, '再生资源')">再生资源</el-tag>
              <el-tag :type="classTagType(22)" @click.native="classTagOnclick(22, '黑色金属')">黑色金属</el-tag>
              <el-tag :type="classTagType(23)" @click.native="classTagOnclick(23, '木材加工')">木材加工</el-tag>
              <el-tag :type="classTagType(24)" @click.native="classTagOnclick(24, '管道管件')">管道管件</el-tag>
              <el-tag :type="classTagType(25)" @click.native="classTagOnclick(25, '机械制造')">机械制造</el-tag>
              <el-tag :type="classTagType(26)" @click.native="classTagOnclick(26, '信息技术')">信息技术</el-tag>
            </div>
            <div class="hide">
              <el-tag :type="classTagType(27)" @click.native="classTagOnclick(27, '汽车制造及配件')">汽车制造及配件</el-tag>
              <el-tag :type="classTagType(28)" @click.native="classTagOnclick(28, '现代服务业')">现代服务业</el-tag>
              <el-tag :type="classTagType(29)" @click.native="classTagOnclick(29, '消费品工业')">消费品工业</el-tag>
              <el-tag :type="classTagType(30)" @click.native="classTagOnclick(30, '显示器产业集群')">显示器产业集群</el-tag>
              <el-tag :type="classTagType(31)" @click.native="classTagOnclick(31, '大数据产业')">大数据产业</el-tag>
              <el-tag :type="classTagType(32)" @click.native="classTagOnclick(32, '5****业集群')">5****业集群</el-tag>
              <el-tag :type="classTagType(33)" @click.native="classTagOnclick(33, '工业楼和总部经济')">工业楼和总部经济</el-tag>
            </div>
          </div>
        </div>
        <div>
          <el-button round v-if="showClass" @click="changeShowClass">
            <el-icon>
              <arrow-up-bold/>
            </el-icon>
            收起
          </el-button>
          <el-button round v-else @click="changeShowClass">
            <el-icon>
              <arrow-down-bold/>
            </el-icon>
            展开
          </el-button>
        </div>
      </div>
      <div id="selectlocation">
        <div class="label">
          <span style="margin: auto;">所在地</span>
        </div>
        <div>
          <div id="tags">
            <el-tag :type="tagsType(0)" @click.native="tagsOnclick(0, '全部', 0)">全部</el-tag>
            <el-tag :type="tagsType(1)" @click.native="tagsOnclick(1, '北京市', 1)">北京市</el-tag>
            <el-tag :type="tagsType(2)" @click.native="tagsOnclick(2, '天津市', 2)">天津市</el-tag>
            <el-tag :type="tagsType(3)" @click.native="tagsOnclick(3, '上海市', 9)">上海市</el-tag>
            <el-tag :type="tagsType(4)" @click.native="tagsOnclick(4, '广东省', 19)">广东省</el-tag>
            <el-tag :type="tagsType(5)" @click.native="tagsOnclick(5, '海南省', 21)">海南省</el-tag>
            <el-tag :type="tagsType(6)" @click.native="tagsOnclick(6, '四川省', 23)">四川省</el-tag>
            <el-tag :type="tagsType(7)" @click.native="tagsOnclick(7, '湖南省', 18)">湖南省</el-tag>
            <el-tag :type="tagsType(8)" @click.native="tagsOnclick(8, '湖北省', 17)">湖北省</el-tag>
            <el-tag :type="tagsType(9)" @click.native="tagsOnclick(9, '福建省', 13)">福建省</el-tag>
            <el-tag :type="tagsType(10)" @click.native="tagsOnclick(10, '重庆市', 22)">重庆市</el-tag>
          </div>
          <div v-show="showLocation" id="hiden">
            <div class="hide">
              <el-tag :type="tagsType(11)" @click.native="tagsOnclick(11, '浙江省', 11)">浙江省</el-tag>
              <el-tag :type="tagsType(12)" @click.native="tagsOnclick(12, '江西省', 14)">江西省</el-tag>
              <el-tag :type="tagsType(13)" @click.native="tagsOnclick(13, '山西省', 4)">山西省</el-tag>
              <el-tag :type="tagsType(14)" @click.native="tagsOnclick(14, '陕西省', 27)">陕西省</el-tag>
              <el-tag :type="tagsType(15)" @click.native="tagsOnclick(15, '河北省', 3)">河北省</el-tag>
              <el-tag :type="tagsType(16)" @click.native="tagsOnclick(16, '辽宁省', 6)">辽宁省</el-tag>
              <el-tag :type="tagsType(17)" @click.native="tagsOnclick(17, '吉林省', 7)">吉林省</el-tag>
              <el-tag :type="tagsType(18)" @click.native="tagsOnclick(18, '江苏省', 10)">江苏省</el-tag>
              <el-tag :type="tagsType(19)" @click.native="tagsOnclick(19, '安徽省', 12)">安徽省</el-tag>
              <el-tag :type="tagsType(20)" @click.native="tagsOnclick(20, '山东省', 15)">山东省</el-tag>
            </div>
            <div class="hide">
              <el-tag :type="tagsType(21)" @click.native="tagsOnclick(21, '河南省', 16)">河南省</el-tag>
              <el-tag :type="tagsType(22)" @click.native="tagsOnclick(22, '云南省', 25)">云南省</el-tag>
              <el-tag :type="tagsType(23)" @click.native="tagsOnclick(23, '甘肃省', 28)">甘肃省</el-tag>
              <el-tag :type="tagsType(24)" @click.native="tagsOnclick(24, '贵州省', 24)">贵州省</el-tag>
              <el-tag :type="tagsType(25)" @click.native="tagsOnclick(25, '青海省', 29)">青海省</el-tag>
              <el-tag :type="tagsType(26)" @click.native="tagsOnclick(26, '黑龙江省', 8)">黑龙江省</el-tag>
              <el-tag :type="tagsType(27)" @click.native="tagsOnclick(27, '内蒙古自治区', 5)">内蒙古自治区</el-tag>
              <el-tag :type="tagsType(28)" @click.native="tagsOnclick(28, '广西壮族自治区', 20)">广西壮族自治区</el-tag>
              <el-tag :type="tagsType(29)" @click.native="tagsOnclick(29, '西藏自治区', 26)">西藏自治区</el-tag>
            </div>
            <div class="hide">
              <el-tag :type="tagsType(30)" @click.native="tagsOnclick(30, '宁夏回族自治区', 30)">宁夏回族自治区</el-tag>
              <el-tag :type="tagsType(31)" @click.native="tagsOnclick(31, '新疆维吾尔族自治区', 31)">新疆维吾尔族自治区</el-tag>
              <el-tag :type="tagsType(32)" @click.native="tagsOnclick(32, '台湾省', 32)">台湾省</el-tag>
              <el-tag :type="tagsType(33)" @click.native="tagsOnclick(33, '香港', 33)">香港</el-tag>
              <el-tag :type="tagsType(34)" @click.native="tagsOnclick(34, '澳门', 34)">澳门</el-tag>
              <el-tag :type="tagsType(35)" @click.native="tagsOnclick(35, '海外', 35)">海外</el-tag>
              <el-tag :type="tagsType(36)" @click.native="tagsOnclick(36, '其他', 36)">其他</el-tag>
            </div>
          </div>
        </div>
        <div>
          <el-button round v-if="showLocation" @click="changeShowLocation">
            <el-icon>
              <arrow-up-bold/>
            </el-icon>
            收起
          </el-button>
          <el-button round v-else @click="changeShowLocation">
            <el-icon>
              <arrow-down-bold/>
            </el-icon>
            展开
          </el-button>
        </div>
      </div>
      <div id="inputbox">
        <div style="width: 250px">
          <el-input placeholder="请输入内容" v-model="input" clearable>
            <!--<template #prefix>
              <el-icon :size="20" style="top: 5px; left: 0px"><search /></el-icon>
            </template>--></el-input>
        </div>
        <el-button type="primary" style="margin: 0px 10px" @click="searchBtnOnclick">
          <el-icon style="vertical-align: middle;">
            <search/>
          </el-icon>
          <span style="vertical-align: middle;"> 搜索 </span>
        </el-button>
        <el-tag v-show="locationIndex!==0" closable @close="handleTagClose(true)">{{ location }}</el-tag>
        <el-tag v-show="classIndex!==0" closable @close="handleTagClose(false)">{{ Class }}</el-tag>
        <el-tag v-show="showPrice" closable @close="handlePriceTagClose">
          {{'价格区间：'+ priceArr[1]+' - '+priceArr[2]}}
        </el-tag>
      </div>
      <div id="selectbox">
        <el-switch v-model="sortPrice" @change="handleSwitchChange" 
          active-color="#13ce66" inactive-color="#ff4949" active-text="价格排序" inactive-text="默认排序"/>
        <span v-show="!sortPrice">&emsp;</span>
        <span v-show="sortPrice">
          <el-tag v-show="sortAsc" effect="dark" type="warning" @click.native="sortTagOnclick">
            价格升序<el-icon><sort-up /></el-icon>
          </el-tag>
          <el-tag v-show="!sortAsc" effect="dark" type="warning" @click.native="sortTagOnclick">
            价格降序<el-icon><sort-down /></el-icon>
          </el-tag>
        </span>
        只看会员
        <el-switch v-model="vip_only"  @change="handleSwitchChange" inline-prompt active-text="是" inactive-text="否"/>
        &emsp;价格区间&nbsp;
        <el-input v-model="priceInputArr[0]" class="smallinput" size="small"/>
        &nbsp;-&nbsp;
        <el-input v-model="priceInputArr[1]" class="smallinput" size="small"/>
        <el-tag effect="dark" type="warning" @click.native="priceTagOnclick"><el-icon><check /></el-icon></el-tag>
      </div>
    </div>
    <div id="itembox">
      <div class="item" v-for="result in this.resultList">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <div class="item-content">
                <span class="titlespan" :title="result.title">{{ result.title }}</span>
              </div>
              <el-button id="msgbtn" type="danger" round>在线咨询
                <el-icon><message/></el-icon>
              </el-button>
            </div>
          </template>
          <div>
            <div class="imgdiv">
              <img class="itemimg" v-if="result.picture[0] === 'h'" :src="result.picture">
              <img class="defaultimg" v-else
                src="https://img1.baidu.com/it/u=983140283,2519191872&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=375">
            </div>
            <div class="infodiv">
              <div class="text">公司名：{{ result.company }}</div>
              <div class="text">所在地：{{ result.areaname }}</div>
              <div class="text">价&emsp;格：{{ result.price }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    <div v-if="this.pageCount!==0" id="pagebox">
      <el-pagination layout="prev, pager, next" :total="getPage" @current-change="handlePageChange"/>
    </div>
  </div>
</template>

<script>
import {Search, ArrowDownBold, ArrowUpBold, SortUp, SortDown, Message, Check} from '@element-plus/icons'
import {ElMessage} from 'element-plus'

export default {
  components: {
    Search,
    ArrowDownBold,
    ArrowUpBold,
    SortUp,
    SortDown,
    Message,
    Check
  },
  data() {
    return {
      locationIndex: 0,
      classIndex: 0,
      LocationTagsTypeArr: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      ClassTagsTypeArr: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      priceArr: [0, 0, 0],
      priceInputArr: ['', ''],
      locationID: 0,
      classID: 0,
      location: '全部',
      Class: '全部',
      input: '',
      refreshData: false,
      showLocation: false,
      showClass: false,
      showPrice: false,
      // testtext: '',
      sortAsc: true,
      vip_only: false,
      sortPrice: false,
      pageCount: 0,
      curPage: 0,
      count: 0,
      resultList: null,
      // itemcount: 0,
      // noResult: false,
    };
  },
  methods: {
    HTTPQuery(page) {
      this.refreshData = false
      this.$http({
        method: 'post',
        url: '/query',
        data: {
          queryColumnName: "String",
          queryString: this.input,
          queryCategoryID: 0,
          queryAreaID: this.locationID,
          vip: this.getVIP,
          priceSort: this.getSort,
          page: page,
          queryTable: "mall",
          priceSection: this.priceArr
        }
      })
          .then(({data}) => {
            console.log(data)
            if (data.data) {
              this.resultList = data.data
              this.count = data.recordCount
              this.pageCount = data.pageCount
              this.curPage = data.curPage
              // this.itemcount = this.count - 10 * this.curPage + 10
              this.refreshData = true
            } else {
              // this.noResult = true
              ElMessage('未查询到相关商品')
            }
          })
          .catch((error) => {
            console.log('ERR')
            console.log(error)
          })
    },
    resetData() {
      // this.itemcount = 0
      this.count = 0
      this.curPage = 0
      this.pageCount = 0
      this.resultList = null
    },
    print() {
      console.log(this)
    },
    changeShowLocation() {
      this.showLocation = !this.showLocation
    },
    changeShowClass() {
      this.showClass = !this.showClass
    },
    tagsOnclick(index, text, ID) {
      if (index !== this.locationIndex) {
        this.LocationTagsTypeArr[this.locationIndex] = 0
        this.LocationTagsTypeArr[index] = 1
        this.location = text
        this.locationIndex = index
        this.locationID = ID
      }
    },
    tagsType(index) {
      if (this.LocationTagsTypeArr[index] === 0) {
        return "info"
      } else {
        return ""
      }
    },
    classTagOnclick(index, text, ID) {
      if (index !== this.classIndex) {
        this.ClassTagsTypeArr[this.classIndex] = 0
        this.ClassTagsTypeArr[index] = 1
        this.Class = text
        this.classIndex = index
        this.classID = ID
      }
    },
    classTagType(index) {
      if (this.ClassTagsTypeArr[index] === 0) {
        return "info"
      } else {
        return ""
      }
    },
    handleTagClose(bool) {
      if (bool) {
        this.LocationTagsTypeArr[this.locationIndex] = 0
        this.location = '全部'
        this.locationIndex = 0
        this.LocationTagsTypeArr[this.locationIndex] = 1
        this.locationID = 0
      } else {
        this.ClassTagsTypeArr[this.classIndex] = 0
        this.Class = '全部'
        this.classIndex = 0
        this.ClassTagsTypeArr[this.classIndex] = 1
        this.classID = 0
      }
    },
    searchBtnOnclick() {
      this.resetData()
      this.HTTPQuery(1)
    },
    handlePageChange(page) {
      console.log(page)
      // this.resetData()
      this.HTTPQuery(page)
    },
    setSortDefault() {
      this.sortDefault = true;
    },
    sortTagOnclick() {
      this.sortAsc = !this.sortAsc
      if(this.refreshData){
        this.HTTPQuery(1)
      }
    },
    priceTagOnclick(){
      this.priceArr = [0 ,0 ,0]
      this.showPrice = false
      let x = Number(this.priceInputArr[0])
      let y = Number(this.priceInputArr[1])
      if(isNaN(x) || isNaN(y)){
        ElMessage('价格区间请输入数字！')
      } else {
        if( x < 0 || y < 0){
          ElMessage('价格区间应大于0！') 
        } else {
          x = Number(x.toFixed(1))
          y = Number(y.toFixed(1))
          // console.log('x:'+x)
          // console.log('y:'+y)
          if ( x === y ){
            ElMessage('请输入合理的价格区间！(价格区间不能太小)')
            // ElMessage('')
          } else {
            this.priceArr[0] = 1
            if( y > x ){
              this.priceArr[2] = y
              this.priceArr[1] = x
              // console.log(typeof x)
            } else {
              this.priceArr[1] = y
              this.priceArr[2] = x
            }
            this.showPrice = true
            if(this.refreshData){
              this.HTTPQuery(1)
            }
          }
        }
      }
    },
    handlePriceTagClose(){
      this.showPrice = false
      this.priceArr = [0, 0, 0]
      this.priceInputArr= ['', '']
    },
    handleSwitchChange(/* b */){
      // console.log(b)
      if (this.refreshData) {
        this.HTTPQuery(1)
      }
    }
  },
  computed: {
    getSort() {
      if (this.sortPrice === false) {
        return '0';
      } else {
        if (this.sortAsc) {
          return 'asc'
        } else {
          return 'desc'
        }
      }
    },
    getPage() {
      if (this.count !== 0) {
        if (this.count % 10 === 0) {
          return this.pageCount * 10
        } else {
          return (this.pageCount + 1) * 10
        }
      } else {
        return 10
      }
    },
    getVIP() {
      if (this.vip_only){
        return 1
      } else {
        return 0
      }
    }
  }
}
</script>

<style scoped>
#msgbtn{
  float: right;
  width: 20%;
}

#itembox {
  margin: 20px auto 20px;
  width: 80%;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
}

#inputbox {
  margin: auto;
  display: flex;
  flex-direction: row;
  height: 30px;
  width: 900px;
}

#selectlocation {
  width: 1100px;
  margin: 20px auto;
  display: flex;
  flex-direction: row;
}

#selectclass {
  width: 1100px;
  margin: 20px auto;
  display: flex;
  flex-direction: row;
}

.el-tag {
  cursor: pointer;
  font-size: 14px;
  margin: auto 10px;
}

#tags {
  height: 30px;
  display: flex;
  flex-direction: row;
}

.label {
  height: 30px;
  width: 80px;
}

#hiden {
  width: 900px;
}

.hide {
  display: flex;
  width: 900px;
  height: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text {
  display: flex;
  justify-content: flex-start;
  font-size: 14px;
}

.box-card {
  width: 100%;
  height: 200px;
}

.itemrow {
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.item {
  margin: 5px;
  flex: 1;
}

.item-content{
  float: left;
  width: 80%;
}

.titlespan{
  min-width: 360px;
  max-width: 360px;
  text-align: left;
  white-space: nowrap;
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
}

.imgdiv{
  float: left;
  width: 180px;
}

.infodiv{
  float: left;
  margin-top: 10px;
}

.itemimg{
  width: 100px;
  height: 100px;
  float: left;
  margin-left: 40px;
}

.defaultimg{
  width: 150px;
  height: 100px;
  float: left;
  margin-left:15px;
}

#pagebox {
  margin: 0px auto;
  width: 600px;
  display: flex;
  justify-content: center;
}

#selectbox{
  margin-top: 5px;
}

.smallinput{
  width: 50px;
}
</style>

//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
<template>
<div id="receptionpages">
  <div class="receptionpage" v-show="page_1">
    <div class="receptiontop">
      <button class="returnbtn" v-on:click="backhome"><i class="fa fa-times-rectangle"></i></button>
    </div>
    <button class="receptioncontain" v-on:click="invoice">
      <div class="receptioncontainer">
        <i class="fa fa-file">
          <p>生成账单</p>
        </i>
      </div>
    </button>
    <button class="receptioncontain" v-on:click="detail">
      <div class="receptioncontainer">
        <i class="fa fa-file-text">
          <p>生成详单</p>
        </i>
      </div>
    </button>
  </div>

  <div class="receptionpage" v-show="page_2">
    <div class="receptiontop">
      房间号:
      <input class="receptioninput" v-model="room_id">
      <button class="receptionnewbutton" v-on:click="get_invoice">搜索</button>
      <button class="receptionnewbutton" v-on:click="print_invoice">打印</button>
      <button class="returnbtn" v-on:click="changerole"><i class="fa fa-times-rectangle"></i></button>
    </div>
    <div v-if="invoicetable">
      <table>
        <tr>
          <th>房间号</th>
          <th>登入时间</th>
          <th>登出时间</th>
          <th>费用</th>
        </tr>
        <tr>
          <td>{{ invoices.room_id }}</td>
          <td>{{ invoices.check_in_time }}</td>
          <td>{{ invoices.check_out_time }}</td>
          <td>{{ invoices.fee }}</td>
        </tr>
      </table>
    </div>
  </div>

  <div class="receptionpage" v-show="page_3">
    <div class="receptiontop">
      房间号:
      <input class="receptioninput" v-model="room_id">
      <button class="receptionnewbutton" v-on:click="get_rdr">搜索</button>
      <button class="receptionnewbutton" v-on:click="print_rdr">打印</button>
      <button class="returnbtn" v-on:click="changerole"><i class="fa fa-times-rectangle"></i></button>
    </div>
    <div v-if="rdrtable">
      <table>
        <tr>
          <th>房间号</th>
          <th>起始时间</th>
          <th>结束时间</th>
          <th>风速</th>
          <th>费率</th>
          <th>费用</th>
        </tr>
        <tr v-for="rdr in rdrs" :key="rdr.start_time">
          <td v-text="rdr.room_id"></td>
          <td v-text="rdr.start_time"></td>
          <td v-text="rdr.end_time"></td>
          <td v-text="rdr.speed"></td>
          <td v-text="rdr.fee_rate"></td>
          <td v-text="rdr.fee"></td>
        </tr>
      </table>
    </div>
  </div>
</div>
</template>

<style>
html,
body,
#receptionpages,
.receptionpage {
  width: 100%;
  height: 100%;
  margin: 0;
  background-color: #173446;
  color: #598DAC;
}

button {
  margin: 0;
  padding: 0;
  border: 0;
  outline: none;
  background-color: #173446;
  color: #598DAC;
}

.returnbtn {
  background-color: #09212F;
  position: absolute;
  top: 0;
  right: 0;
  height: 79px;
  width: 79px;
  font-size: 28px;
}

.returnbtn:hover {
  transition: all 0.7s;
  background-color: #010101;
}

.receptionnewbutton {
  background-color: #09212F;
  color: #173446;
  font-size: 24px;
}

.receptiontop {
  text-align: center;
  width: 100%;
  height: 79px;
  background-color: #09212F;
  color: #7296AC;
  border-bottom: 1px solid #1A2B36;
  line-height: 79px;
  font-size: 24px;
}

.receptioninput {
  line-height: 28px;
  color: #7296AC;
  background: none;
  border: none;
  margin: 0;
  border-bottom: 2px solid #7296AC;
}

.receptioncontain {
  display: flex;
  float: left;
  height: calc(100% - 80px);
  width: 50%;
}

.receptioncontain:hover {
  transition: all 0.7s;
  background-color: #1A2B36;
}

.receptioncontainer {
  margin: auto;
  text-align: center;
}

.receptioncontainer i {
  text-align: center;
  font-size: 10em;
}

.receptioncontainer p {
  margin: 0 auto;
  line-height: 2em;
  font-size: 0.2em;
}

table {
  padding-top: 30px;
  width: 100%;
  text-align: center;
  line-height: 30px;
}
</style>

<script>
// @ is an alias to /src
export default {
  data() {
    return {
      page_1: true,
      page_2: false,
      page_3: false,
      invoicetable: false,
      rdrtable: false,
      room_id: '',
      invoices: {
        room_id: '',
        check_in_time: '',
        check_out_time: '',
        fee: '',
      },
      rdrs: [],
    }
  },
  methods: {
    backhome: function() {
      this.$router.push("/");
    },
    changerole: function() {
      this.page_1 = true;
      this.page_2 = false;
      this.page_3 = false;
    },
    invoice: function() {
      this.page_1 = false;
      this.page_2 = true;
      this.page_3 = false;
    },
    detail: function() {
      this.page_1 = false;
      this.page_2 = false;
      this.page_3 = true;
    },
    get_invoice: function() {
      //3.3 查询账单
      var this_axios = this;
      this_axios.$axios({
        method: 'get',
        url: this.$store.state.website+'/logger/query_invoice?room_id=' + this_axios.room_id,
      }).then(function(response) {
        if (response.data.message == 'OK') {
          this_axios.invoices = response.data.result;
          this_axios.invoicetable = true;
        } else alert(response.data.message);
      }).catch(function(error) {
        alert(error);
      })
    },
    print_invoice: function() {
      //3.4 打印账单
      var this_axios = this;
      this_axios.$axios({
        url: this.$store.state.website+'/logger/print_invoice?room_id=' + this_axios.room_id, // 接口名字
        method: 'get',
        responseType: "blob"
      }).then(function(response) {
        const blob = new Blob([response.data])
        const aEle = document.createElement('a'); // 创建a标签
        const href = window.URL.createObjectURL(blob); // 创建下载的链接
        aEle.href = href;
        aEle.download = this_axios.room_id+'账单'+'.csv'; // 下载后文件名
        document.body.appendChild(aEle);
        aEle.click(); // 点击下载
        document.body.removeChild(aEle); // 下载完成移除元素
        window.URL.revokeObjectURL(href) // 释放掉blob对象
      })
    },
    get_rdr: function() {
      //3.5 查询详单
      var this_axios = this;
      this_axios.$axios({
        method: 'get',
        url: this.$store.state.website+'/logger/query_rdr?room_id=' + this_axios.room_id,
      }).then(function(response) {
        if (response.data.message == 'OK') {
          this_axios.rdrs = response.data.result;
          this_axios.rdrtable = true;
        } else alert(response.data.message);
      }).catch(function(error) {
        alert(error);
      })
    },
    print_rdr: function() {
      //3.6 打印详单
      var this_axios = this;
      this_axios.$axios({
        url: this.$store.state.website+'/logger/print_rdr?room_id='+this_axios.room_id, // 接口名字
        method: 'get',
        responseType: "blob"
      }).then(function(response) {
        const blob = new Blob([response.data])
        const aEle = document.createElement('a'); // 创建a标签
        const href = window.URL.createObjectURL(blob); // 创建下载的链接
        aEle.href = href;
        aEle.download = this_axios.room_id+'详单'+'.csv'; // 下载后文件名
        document.body.appendChild(aEle);
        aEle.click(); // 点击下载
        document.body.removeChild(aEle); // 下载完成移除元素
        window.URL.revokeObjectURL(href) // 释放掉blob对象
      })
    },
  }
}
</script>

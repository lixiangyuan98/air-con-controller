<template>
  <div id="receptionpages">
    <div class="receptionpage" v-show="page_1">
      <div class="receptiontop">
          <button class="returnbtn" v-on:click="backhome"><i class="fa fa-times-rectangle"></i></button>
      </div>
      <button class="receptioncontain" v-on:click="invoice">
        <div class="receptioncontainer">
          <i class="fa fa-file"><p>生成账单</p></i>
        </div>
      </button>
      <button class="receptioncontain" v-on:click="detail">
        <div class="receptioncontainer">
          <i class="fa fa-file-text"><p>生成详单</p></i>
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
            <td>{{ room_id }}</td>
            <td>check_in_time</td>
            <td>check_out_time</td>
            <td>fee</td>
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
            <th>目标温度</th>
            <th>费率</th>
            <th>费用</th>
          </tr>
          <tr>
            <td>{{ room_id }}</td>
            <td>start_time</td>
            <td>end_time</td>
            <td>speed</td>
            <td>target_temper</td>
            <td>fee_rate</td>
            <td>fee</td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<style>
  html, body, #receptionpages, .receptionpage{
    width: 100%;
    height:100%;
    margin: 0;
    background-color: #173446;
    color: #598DAC;
  }
  button{
    margin: 0;
    padding: 0;
    border: 0;
    outline: none;
    background-color: #173446;
    color: #598DAC;
  }
  .returnbtn{
    background-color: #09212F;
    position: absolute;
    top: 0;
    right: 0;
    height: 79px;
    width:79px;
    font-size: 28px;
  }
  .returnbtn:hover{
    transition: all 0.7s;
    background-color: #010101;
  }
  .receptionnewbutton{
    background-color: #09212F;
    color: #173446;
    font-size: 24px;
  }
  .receptiontop{
    text-align: center;
    width:100%;
    height:79px;
    background-color: #09212F;
    color: #7296AC;
    border-bottom: 1px solid #1A2B36;
    line-height: 79px;
    font-size: 24px;
  }
  .receptioninput{
    line-height: 28px;
    color: #7296AC;
    background:none;
    border:none;
    margin: 0;
    border-bottom: 2px solid #7296AC;
  }
  .receptioncontain{
    display: flex;
    float: left;
    height: calc(100% - 80px);
    width: 50%;
  }
  .receptioncontain:hover{
    transition: all 0.7s;
    background-color: #1A2B36;
  }
  .receptioncontainer{
    margin: auto;
    text-align: center;
  }
  .receptioncontainer i{
    text-align: center;
    font-size: 10em;
  }
  .receptioncontainer p{
    margin: 0 auto;
    line-height: 2em;
    font-size: 0.2em;
  }
  table{
    padding-top: 30px;
    width:100%;
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
    }
  },
  methods: {
    backhome: function(){
      this.$router.push("/");
    },
    changerole: function(){
      this.page_1 = true;
      this.page_2 = false;
      this.page_3 = false;
    },
    invoice: function(){
      this.page_1 = false;
      this.page_2 = true;
      this.page_3 = false;
    },
    detail: function(){
      this.page_1 = false;
      this.page_2 = false;
      this.page_3 = true;
    },
    get_invoice: function(){
      this.invoicetable = true;
      //console.log("get_invoice",this.room_id);
    },
    get_rdr: function(){
      this.rdrtable = true;
      //console.log("get_invoice",this.room_id);
    },
    print_invoice: function(){
      //console.log("print_invoice",this.room_id);
    },
    print_rdr: function(){
      //console.log("print_rdr",this.room_id);
    },
  }
}
</script>

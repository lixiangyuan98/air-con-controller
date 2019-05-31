//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
<template>
  <div id="managerpage">
    <div class="managertop">
      <button class="returnbtn" v-on:click="backhome"><i class="fa fa-times-rectangle"></i></button>
      <button :class="classA" v-on:click="qtype_day">日报表</button>
      <button :class="classB" v-on:click="qtype_week">周报表</button>
      <button :class="classC" v-on:click="qtype_month">月报表</button>
      <button :class="classD" v-on:click="qtype_year">年报表</button>
      房间号:
      <input class="managerinput" v-model="room_id">
      日期：
      <input class="managerinput" v-model="date.year" placeholder="年">-
      <input class="managerinput" v-model="date.month" placeholder="月">-
      <input class="managerinput" v-model="date.day" placeholder="日">
      <button class="managernewbutton" v-on:click="get_report">搜索</button>
      <button class="managernewbutton" v-on:click="print_report">打印</button>
    </div>
    <div v-if="reporttable">
      <table>
        <tr>
          <th>房间号</th>
          <th>起停次数</th>
          <th>工作时间/秒</th>
          <th>费用</th>
          <th>调度次数</th>
          <th>详单条目数</th>
          <th>改变温度次数</th>
          <th>改变风速次数</th>
        </tr>
        <tr>
          <td>{{ room_id }}</td>
          <td>on_off_times</td>
          <td>service_time</td>
          <td>fee</td>
          <td>dispatch_times</td>
          <td>rdr_number</td>
          <td>change_temp_times</td>
          <td>change_speed_times</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<style>
  html, body, #managerpage{
    width: 100%;
    height:100%;
    margin: 0;
    background-color: #173446;
    color: #598DAC;
  }
  button{
    line-height: 79px;
    margin: 0;
    padding: 0 20px;
    border: 0;
    outline: none;
    background-color: #173446;
    color: #598DAC;
  }
  .managernewbutton{
    background-color: #09212F;
    color: #173446;
    font-size: 24px;
  }
  .managernewbutton_on{
    background-color: #1A2B36;
    color: #7296AC;
    font-size: 24px;
  }
  .managertop{
    text-align: center;
    width:100%;
    height:79px;
    background-color: #09212F;
    color: #7296AC;
    border-bottom: 1px solid #1A2B36;
    line-height: 79px;
    font-size: 24px;
  }
  .managerinput{
    line-height: 28px;
    color: #7296AC;
    background:none;
    border:none;
    margin: 0;
    border-bottom: 2px solid #7296AC;
    font-size: 24px;
    width: 96px;
    text-align: center;
  }
  input::-webkit-input-placeholder {
    color: #173446;
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
      classA: 'managernewbutton',
      classB: 'managernewbutton',
      classC: 'managernewbutton',
      classD: 'managernewbutton',
      reporttable: false,
      qtype: '',
      room_id: '',
      date:{
        year: '',
        month: '',
        day: '',
      },
      report:{
        room_id: '',
        on_off_times: '',
        service_time: '',
        fee: '',
        dispatch_times: '',
        rdr_number: '',
        change_temp_times: '',
        change_speed_times: '',
      },
    }
  },
  methods: {
    backhome: function(){
      this.$router.push("/");
    },
    qtype_day:function(){
      this.qtype = 'day';
      this.classA= 'managernewbutton_on';
      this.classB= 'managernewbutton';
      this.classC= 'managernewbutton';
      this.classD= 'managernewbutton';
    },
    qtype_week:function(){
      this.qtype = 'week';
      this.classA= 'managernewbutton';
      this.classB= 'managernewbutton_on';
      this.classC= 'managernewbutton';
      this.classD= 'managernewbutton';
    },
    qtype_month:function(){
      this.qtype = 'month';
      this.classA= 'managernewbutton';
      this.classB= 'managernewbutton';
      this.classC= 'managernewbutton_on';
      this.classD= 'managernewbutton';
    },
    qtype_year:function(){
      this.qtype = 'year';
      this.classA= 'managernewbutton';
      this.classB= 'managernewbutton';
      this.classC= 'managernewbutton';
      this.classD= 'managernewbutton_on';
    },
    get_report: function(){
      //3.1 查询报表
      this.$axios({
        method:'get',
        url:'/logger/query_report?qtype='+this.qtype+'&room_id='+this.room_id+
        '&date='+this.date.year+'-'+this.date.month+'-'+this.date.day,
      }).then(function(response){
        if(response.message == 'OK'){
          this.report = response.result;
          this.reporttable = true;
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
    print_report: function(){
      //3.2 打印报表
      this.$axios({
        method:'get',
        url:'/logger/print_report?qtype='+this.qtype+'&room_id='+this.room_id+
        '&date='+this.date.year+'-'+this.date.month+'-'+this.date.day,
      }).then(function(response){
        if(response.message == 'OK'){
          alert("打印报表");
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
  }
}
</script>

//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
//----------------------------------------------------------------------------//
<template>
  <div id="serverpage">
    <div v-if="poweron" class="servercontainer">
      <div class="servercontain">
        设置最高温度：
        <input v-if="!startup" class="serverinput" v-model="highest_temper">
        <span v-if="startup">{{ highest_temper }}</span>
      </div>
      <div class="servercontain">
        设置最低温度：
        <input v-if="!startup" class="serverinput" v-model="lowest_temper">
        <span v-if="startup">{{ lowest_temper }}</span>
      </div>
      <div class="servercontain">
        设低风速费率：
        <input v-if="!startup" class="serverinput" v-model="low_speed_fee">
        <span v-if="startup">{{ low_speed_fee }}</span>
      </div>
      <div class="servercontain">
        设中风速费率：
        <input v-if="!startup" class="serverinput" v-model="middle_speed_fee">
        <span v-if="startup">{{ middle_speed_fee }}</span>
      </div>
      <div class="servercontain">
        设高风速费率：
        <input v-if="!startup" class="serverinput" v-model="high_speed_fee">
        <span v-if="startup">{{ high_speed_fee }}</span>
      </div>
      <div class="servercontain">
        设置默认温度：
        <input v-if="!startup" class="serverinput" v-model="default_temper">
        <span v-if="startup">{{ default_temper }}</span>
      </div>
      <div class="servercontain">
        设置默认风速：
        <input v-if="!startup" class="serverinput" v-model="default_speed">
        <span v-if="startup">{{ default_speed }}</span>
      </div>
      <div class="servercontain">
        设置默认模式：
        <input v-if="!startup" class="serverinput" v-model="mode">
        <span v-if="startup">{{ mode }}</span>
      </div>
    </div>
    <div class="serverfoot">
      <button class="serverbtn" v-on:click="power_on"><i class="fa fa-power-off">{{ power_turn }}</i></button>
      <button class="serverbtn" v-on:click="check" v-if="!checkout"><i class="fa fa-check"></i></button>
      <button class="serverbtn" v-on:click="start_up" v-if="checkout"><i class="fa fa-play"></i></button>
      <button class="serverbtn" v-on:click="changerole"><i class="fa fa-times-rectangle"></i></button>
      <button class="serverbtn" v-on:click="check_room_state"><i class="fa fa-calculator"></i></button>
    </div>
    <div v-if="view_room">
      <table>
        <tr>
          <th>房间号</th>
          <th>当前温度</th>
          <th>当前风速</th>
          <th>模式</th>
          <th>费用</th>
          <th>费率</th>
          <th>房间状态</th>
          <th>工作时间</th>
          <th>目标温度</th>
        </tr>
        <tr v-for="roomstate in roomstates" :key="roomstate.room_id">
          <td v-text="roomstate.room_id"></td>
          <td v-text="roomstate.current_temper"></td>
          <td v-text="roomstate.speed"></td>
          <td v-text="roomstate.mode"></td>
          <td v-text="roomstate.fee"></td>
          <td v-text="roomstate.fee_rate"></td>
          <td v-text="roomstate.status"></td>
          <td v-text="roomstate.service_time"></td>
          <td v-text="roomstate.target_temper"></td>
        </tr>
      </table>
      <button class="serverbtn" v-on:click="stop_room_state"><i class="fa fa-times-rectangle"></i></button>
    </div>
  </div>
</template>

<style>
  html,body,#serverpage {
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

  .serverbtn {
    background-color: none;
    margin: 0 100px;
    height: 80px;
    width: 80px;
    font-size: 28px;
  }

  .serverbtn:hover {
    transition: all 0.7s;
    color: #010101;
  }

  .servercontainer {
    padding: 40px 0 0 0;
  }

  .servercontain {
    margin: 24px 0;
    font-size: 24px;
    text-align: center;
    line-height: 48px;
  }

  .serverfoot {
    display: flex;
    justify-content: center;
    padding-top: 40px;
  }

  .serverinput {
    font-size: 24px;
    line-height: 28px;
    color: #7296AC;
    background: none;
    border: none;
    margin: 0;
    border-bottom: 2px solid #7296AC;
  }
</style>

<script>
// @ is an alias to /src
export default {
  data() {
    return {
      highest_temper: this.$store.state.highest_temper,
      lowest_temper: this.$store.state.lowest_temper,
      low_speed_fee: this.$store.state.low_speed_fee,
      middle_speed_fee: this.$store.state.middle_speed_fee,
      high_speed_fee: this.$store.state.high_speed_fee,
      default_temper: this.$store.state.default_temper,
      default_speed: this.$store.state.default_speed,
      mode: this.$store.state.mode,
      power_turn: 'ON',
      checkout: false,
      startup: false,
      poweron: false,
      roomstates:[],
      view_room: false,
      timer2:'',
    }
  },
  created:function () {
    if (this.$store.state.power_state==true){
      this.power_turn = 'OFF';
      this.checkout = true;
      this.startup = true;
      this.poweron = true;
    }
  },
  methods: {
    power_on: function() {
      //1.1主机开机
      if (this.$store.state.power_state==false){
        var this_axios = this;
        this_axios.$axios({
          method:'get',
          url:this.$store.state.website+'/main_machine/power_on',
        }).then(function(response){
          if(response.data.message == 'OK'){
            this_axios.poweron = true;
            this_axios.power_turn='OFF';
            this_axios.$store.state.power_state=true;
          }
          else window.console.log(response.data.message);
        }).catch(function(error){
          alert(error);
        })
      }
      //1.5关机
      else if (this.$store.state.power_state==true){
        this_axios = this;
        this_axios.$axios({
          method:'get',
          url:this.$store.state.website+'/main_machine/close',
        }).then(function(response){
          if(response.data.message == 'OK'){
            this_axios.poweron = false;
            this_axios.power_turn='ON';
            this_axios.checkout = false;
            this_axios.startup = false;
            this_axios.roomstates = [];
            this_axios.$store.state.highest_temper = '';
            this_axios.$store.state.lowest_temper = '';
            this_axios.$store.state.low_speed_fee = '';
            this_axios.$store.state.middle_speed_fee = '';
            this_axios.$store.state.high_speed_fee = '';
            this_axios.$store.state.default_temper = '';
            this_axios.$store.state.default_speed = '';
            this_axios.$store.state.mode = '';
            this_axios.$store.state.power_state=false;
          }
          else alert(response.data.message);
        }).catch(function(error){
          alert(error);
        })
        window.console.log(this.$store.state);
      }
    },
    check: function() {
      //1.2参数初始化
      if ((this.highest_temper > this.lowest_temper) && (this.high_speed_fee > this.middle_speed_fee) &&
      (this.middle_speed_fee > this.low_speed_fee)){
        var this_axios = this;
        this_axios.$axios({
          method:'get',
          url:this.$store.state.website+'/main_machine/init_param?highest_temper='+this_axios.highest_temper+
          '&lowest_temper='+this_axios.lowest_temper+'&low_speed_fee='+this_axios.low_speed_fee+
          '&middle_speed_fee='+this_axios.middle_speed_fee+'&high_speed_fee='+this_axios.high_speed_fee+
          '&default_temper='+this_axios.default_temper+'&default_speed='+this_axios.default_speed+
          '&mode='+this_axios.mode,
        }).then(function(response){
          if(response.data.message == 'OK'){
            this_axios.checkout = true;
            this_axios.$store.state.highest_temper = this_axios.highest_temper;
            this_axios.$store.state.lowest_temper = this_axios.lowest_temper;
            this_axios.$store.state.low_speed_fee = this_axios.low_speed_fee;
            this_axios.$store.state.middle_speed_fee = this_axios.middle_speed_fee;
            this_axios.$store.state.high_speed_fee = this_axios.high_speed_fee;
            this_axios.$store.state.default_temper = this_axios.default_temper;
            this_axios.$store.state.default_speed = this_axios.default_speed;
            this_axios.$store.state.mode = this_axios.mode;
          }
          else alert(response.data.message);
        }).catch(function(error){
          alert(error);
        })
      }
      window.console.log(this.$store.state);
    },
    start_up: function() {
      //1.3开始执行
      var this_axios = this;
      this_axios.$axios({
        method:'get',
        url:this.$store.state.website+'/main_machine/start_up',
      }).then(function(response){
        if(response.data.message == 'OK'){
          this_axios.startup = true;
        }
        else window.console.log(response.data.message);
      }).catch(function(error){
        alert(error);
      })
    },
    changerole: function() {
      this.$router.push("/");
    },
    checking: function() {
      //1.4监视空调
      var this_axios = this;
      this_axios.$axios({
        method:'get',
        url:this.$store.state.website+'/main_machine/check_room_state',
      }).then(function(response){
        if(response.data.message == 'OK'){
          this_axios.roomstates = response.data.result;
        }
        else alert(response.data.message);
      }).catch(function(error){
        alert(error);
      })
    },
    check_room_state: function() {
        this.view_room=true;
        this.timer2 = setInterval(this.checking, 1200);//3s
      //1.4监视空调
      // 当开始运行startup的时候,保持3秒轮询
    },
    stop_room_state: function() {
        this.view_room=false;
        clearInterval(this.timer2);
      //1.4监视空调
      // 当开始运行startup的时候,保持3秒轮询
    },
  },
}
</script>

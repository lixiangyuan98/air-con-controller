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
      highest_temper: '',
      lowest_temper: '',
      low_speed_fee: '',
      middle_speed_fee: '',
      high_speed_fee: '',
      default_temper: '',
      default_speed: '',
      mode: '',
      power_turn: 'ON',
      checkout: false,
      startup: false,
      poweron: false,
      roomstates:[],
    }
  },
  methods: {
    power_on: function() {
      //1.1主机开机
      if (this.$store.state.power_state==false){
        this.$axios({
          method:'get',
          url:'/main_machine/power_on',
        }).then(function(response){
          if(response.message == 'OK'){
            this.poweron = true;
            this.power_turn='OFF';
            this.$store.state.power_state=true;
          }
          else alert(response.message);
        }).catch(function(error){
          alert(error);
        })
      }
      //1.5关机
      else if (this.$store.state.power_state==true){
        this.$axios({
          method:'get',
          url:'/main_machine/close',
        }).then(function(response){
          if(response.message == 'OK'){
            this.poweron = false;
            this.power_turn='ON';
            this.$store.state.power_state=false;
          }
          else alert(response.message);
        }).catch(function(error){
          alert(error);
        })
      }
    },
    check: function() {
      //1.2参数初始化
      if ((this.highest_temper > this.lowest_temper) && (this.high_speed_fee > this.middle_speed_fee) &&
      (this.middle_speed_fee > this.low_speed_fee)){
        this.$axios({
          method:'get',
          url:'/main_machine/init_param?highest_temper='+this.highest_temper+
          '&lowest_temper='+this.lowest_temper+'&low_speed_fee='+this.low_speed_fee+
          '&middle_speed_fee='+this.middle_speed_fee+'&high_speed_fee='+this.high_speed_fee+
          '&default_temper='+this.default_temper+'&default_speed='+this.default_speed+
          '&mode='+this.mode,
        }).then(function(response){
          if(response.message == 'OK'){
            this.checkout = true;
          }
          else alert(response.message);
        }).catch(function(error){
          alert(error);
        })
      }
    },
    start_up: function() {
      //1.3开始执行
      this.$axios({
        method:'get',
        url:'/main_machine/start_up',
      }).then(function(response){
        if(response.message == 'OK'){
          this.startup = true;
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
    changerole: function() {
      this.$router.push("/");
    },
    checking: function() {
      //1.4监视空调
      this.$axios({
        method:'get',
        url:'/main_machine/check_room_state',
      }).then(function(response){
        if(response.message == 'OK'){
          this.roomstates = response.result;
        }
        else alert(response.message);
      }).catch(function(error){
        alert(error);
      })
    },
  },
  watch: {
    //1.4监视空调
    check_room: function () {
      // 当开始运行startup的时候,保持3秒轮询
      if (this.startup == true) {
        var timer = setInterval(() => {
          setTimeout(() => {
            this.checking(); //调用接口的方法
          }, 0)
        }, 3000);//3s
      }
      // 当页面关闭的时候,结束轮询,否则就会一直发请求,
      //使用$once(eventName, eventHandler)一次性监听事件
      this.$once('hook:boforeDestory', () => {
        clearInterval(timer);
      })
    }
  }
}
</script>
